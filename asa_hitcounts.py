#bu script cisco_asa kategorisinde var olan inventory dosyasindan tek tek cihazlara baglanir ve kurallarin hitcount'larini ceker.

from netmiko import ConnectHandler
from inventory import load_inventory
import re

def check_acl_hitcount(device):
    try:
        netmiko_device = {
            'host': device['host'],
            'username': device['username'],
            'password': device['password'],
            'device_type': device['device_type']
        }

        net_connect = ConnectHandler(**netmiko_device)
        net_connect.enable()
        net_connect.send_command('terminal pager 0')  # Tüm output'un gelmesi için

        output = net_connect.send_command('show access-list')
        rules = []

        for line in output.splitlines():
            # ACL satırlarını line numarası olsa da olmasa da yakala
            if re.match(r"^access-list\s+\S+(?:\s+line\s+\d+)?\s+extended", line):
                hitcount_match = re.search(r'\(hitcnt=(\d+)\)', line)
                if hitcount_match:
                    hitcount = int(hitcount_match.group(1))
                    rules.append({
                        "line": line.strip(),
                        "hitcount": hitcount
                    })

        print(f"\n[+] Device: {device.get('name', device['host'])} - ACL Hitcount Report:")
        if not rules:
            print("[-] No ACL rules with hitcount found.")
        else:
            sorted_rules = sorted(rules, key=lambda x: x['hitcount'])
            for r in sorted_rules:
                print(f"hitcnt={r['hitcount']:>5} | {r['line']}")

        net_connect.disconnect()

    except Exception as e:
        print(f"[X] Failed to connect to {device['host']}: {e}")

def main():
    category = "cisco_asa"
    devices = load_inventory(category)

    if not devices:
        print(f"[!] No devices found in category: {category}")
        return

    for device in devices:
        print(f"\n[!] Connecting to {device['host']}...")
        check_acl_hitcount(device)

if __name__ == "__main__":
    main()
