#bu cihaz asa'nin backup'ini alir.

from netmiko import ConnectHandler
from inventory import load_inventory, load_ftp_info
from ftplib import FTP
import datetime
import os

def backup_device(device, ftp_info):
    try:
        netmiko_device = {
            'host': device['host'],
            'username': device['username'],
            'password': device['password'],
            'device_type': device['device_type']
        }

        print(f"\n[+] Connecting to ASA: {device.get('name', device['host'])}...")
        net_connect = ConnectHandler(**netmiko_device)
        net_connect.enable()
        net_connect.send_command_timing('terminal pager 0')

        output = net_connect.send_command_timing('show running-config')
        net_connect.disconnect()
        print("[+] Configuration fetched successfully.")

        now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"{device.get('name', device['host'])}_running_{now}.txt"

        # Lokale kaydet:
        with open(backup_filename, 'w') as file:
            file.write(output)
        print(f"[+] Config saved locally as {backup_filename}")

        # FTP Upload:
        print("[+] Connecting to FTP server...")
        ftp = FTP(ftp_info['server'])
        ftp.login(user=ftp_info['username'], passwd=ftp_info['password'])
        with open(backup_filename, 'rb') as file:
            ftp.storbinary(f'STOR {backup_filename}', file)
        ftp.quit()
        print(f"[✓] Backup uploaded to FTP server as {backup_filename}")

        # Lokaldeki dosyayı sil:
        if os.path.exists(backup_filename):
            os.remove(backup_filename)
            print(f"[✓] Local file {backup_filename} deleted after upload.")
        else:
            print(f"[!] Local file {backup_filename} not found for deletion.")

    except Exception as e:
        print(f"[X] Error backing up device {device.get('name', device['host'])}: {e}")

def main():
    category = "cisco_asa"
    devices = load_inventory(category)
    ftp_info = load_ftp_info()

    if not devices:
        print(f"[!] No devices found in category: {category}")
        return
    if not ftp_info:
        print(f"[!] FTP server info missing in inventory.yml!")
        return

    for device in devices:
        backup_device(device, ftp_info)

if __name__ == "__main__":
    main()
