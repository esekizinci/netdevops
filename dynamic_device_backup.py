#inventory.yml icerisinde bulunan cihazlara tek tek baglanir.
#configlerini alip yedekler, onu FTP ye upload eder.

import yaml
from netmiko import ConnectHandler
from ftplib import FTP
import datetime
import os

# ====== INVENTORY OKUMA ======
with open("inventory.yml") as f:
    inventory = yaml.safe_load(f)

for device in inventory['devices']:
    print(f"\n[+] Connecting to {device['name']} ({device['host']})")

    try:
        net_connect = ConnectHandler(
            device_type=device['device_type'],
            host=device['host'],
            username=device['username'],
            password=device['password']
        )

        # ====== PAGINATION KAPAT ======
        if device['device_type'] == 'cisco_asa':
            net_connect.send_command_timing('terminal pager 0')
        elif device['device_type'] == 'cisco_ios':
            net_connect.send_command_timing('terminal length 0')
        else:
            print(f"[!] Unknown device type for {device['name']}, skipping...")
            net_connect.disconnect()
            continue

        # ====== CONFIG CEK ======
        output = net_connect.send_command_timing('show running-config')
        net_connect.disconnect()
        print(f"[+] Configuration fetched successfully from {device['name']}.")

        # ====== BACKUP FILENAME ======
        now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"{device['name']}_running_{now}.txt"

        # ====== CONFIG LOCAL YAZ ======
        with open(backup_filename, 'w') as file:
            file.write(output)
        print(f"[+] Config saved locally as {backup_filename}")

        # ====== FTP'YE YUKLE ======
        ftp_server = '10.10.10.10'
        ftp_user = 'backupuser'
        ftp_pass = 'backup123'

        print("[+] Connecting to FTP server...")
        ftp = FTP(ftp_server)
        ftp.login(user=ftp_user, passwd=ftp_pass)

        with open(backup_filename, 'rb') as file:
            ftp.storbinary(f'STOR {backup_filename}', file)
        ftp.quit()
        print(f"[✓] Backup uploaded to FTP server as {backup_filename}")

        # ====== LOCAL DOSYAYI SIL ======
        if os.path.exists(backup_filename):
            os.remove(backup_filename)
            print(f"[✓] Local file {backup_filename} deleted after upload.")
        else:
            print(f"[!] Local file {backup_filename} not found for deletion.")

    except Exception as e:
        print(f"[!] Error connecting to {device['name']} ({device['host']}): {e}")

print("\n[✓] All device backups completed successfully!")
