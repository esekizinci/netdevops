from netmiko import ConnectHandler
from inventory import load_inventory
import re

def summarize_interface_status(device):
    try:
        netmiko_device = {
            'host': device['host'],
            'username': device['username'],
            'password': device['password'],
            'device_type': device['device_type']
        }

        print(f"\n[+] Connecting to {device.get('name', device['host'])}...")
        net_connect = ConnectHandler(**netmiko_device)
        net_connect.enable()

        output = net_connect.send_command("show interfaces | include line protocol")

        admin_up = 0
        admin_down = 0
        protocol_up = 0
        protocol_down = 0

        for line in output.splitlines():
            match = re.match(r"(\S+) is (.+), line protocol is (.+)", line)
            if match:
                intf = match.group(1).strip()
                status = match.group(2).strip()
                protocol = match.group(3).strip()

                # Logical interface'leri hariç tut
                if intf.lower().startswith(("vlan", "loopback", "port-channel")):
                    continue

                # Admin status
                if status == "administratively down":
                    admin_down += 1
                else:
                    admin_up += 1

                # Protocol status
                if protocol == "up":
                    protocol_up += 1
                else:
                    protocol_down += 1

        print(f"\n[+] Interface Status Summary for {device.get('name', device['host'])}:")
        print(f"Toplam admin up       : {admin_up}")
        print(f"Toplam admin down     : {admin_down}")
        print(f"Toplam protocol up    : {protocol_up}")
        print(f"Toplam protocol down  : {protocol_down}")

        net_connect.disconnect()

    except Exception as e:
        print(f"[X] Failed to connect to {device['host']}: {e}")

def main():
    devices = load_inventory("cisco_ios")

    if not devices:
        print("[!] No devices found in category: cisco_ios")
        return

    # Sadece ilk cihaza bağlan (çoklu istenirse for ile döneriz)
    summarize_interface_status(devices[0])

if __name__ == "__main__":
    main()
