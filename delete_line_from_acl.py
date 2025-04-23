from netmiko import ConnectHandler
from inventory import load_inventory
import re

def clean_acl_line(line):
    # Remove 'line XX'
    line = re.sub(r'line \d+ ', '', line)
    # Remove '(hitcnt=...)' and hex at the end
    line = re.sub(r'\(hitcnt=\d+\)\s+0x[0-9a-fA-F]+', '', line)
    return line.strip()

def select_device(devices):
    print("\n[+] Available ASA Devices:")
    for idx, dev in enumerate(devices):
        print(f"{idx + 1}: {dev.get('name', dev['host'])}")
    choice = int(input("\nSelect a device to connect: ")) - 1
    return devices[choice]

def delete_acl_rule(device):
    try:
        netmiko_device = {
            'host': device['host'],
            'username': device['username'],
            'password': device['password'],
            'device_type': device['device_type']
        }

        net_connect = ConnectHandler(**netmiko_device)
        net_connect.enable()
        net_connect.send_command("terminal pager 0")

        output = net_connect.send_command('show access-list')
        acl_names = set()

        for line in output.splitlines():
            if line.startswith('access-list'):
                acl_name = line.split()[1].rstrip(';')
                acl_names.add(acl_name)

        acl_names = sorted(list(acl_names))

        if not acl_names:
            print("[-] No ACLs found!")
            net_connect.disconnect()
            return

        print("\n[+] Available ACLs:")
        for idx, acl in enumerate(acl_names):
            print(f"{idx + 1}: {acl}")

        choice_idx = int(input("\nSelect the ACL by number: ")) - 1
        selected_acl = acl_names[choice_idx]
        print(f"\n[!] You selected ACL: {selected_acl}")

        acl_output = net_connect.send_command(f"show access-list {selected_acl}")
        acl_lines = []
        print(f"\n[*] Rules in {selected_acl}:")
        for idx, line in enumerate(acl_output.splitlines()):
            print(f"{idx + 1}: {line}")
            acl_lines.append(line)

        rule_idx = int(input("\nSelect the rule to DELETE by number: ")) - 1
        selected_rule = acl_lines[rule_idx]
        clean_rule = clean_acl_line(selected_rule)
        delete_command = f"no {clean_rule}"

        print(f"\n[*] Sending command: {delete_command}")
        net_connect.send_config_set([delete_command])

        print("\n[✔] Rule deleted successfully!")
        net_connect.disconnect()

    except Exception as e:
        print(f"[X] Failed to connect to {device['host']}: {e}")

def main():
    category = "cisco_asa"
    devices = load_inventory(category)

    if not devices:
        print(f"[!] No devices found in category: {category}")
        return

    selected_device = select_device(devices)
    delete_acl_rule(selected_device)

if __name__ == "__main__":
    main()
