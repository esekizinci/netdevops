from netmiko import ConnectHandler
from inventory import load_inventory
from random import randint, choice
from datetime import datetime

def generate_random_acl():
    acl = []
    for i in range(1, 26):
        src_ip = f"{randint(1, 223)}.{randint(0, 255)}.{randint(0, 255)}.{randint(0, 255)}"
        dst_ip = f"{randint(1, 223)}.{randint(0, 255)}.{randint(0, 255)}.{randint(0, 255)}"
        port = randint(1, 65535)
        action = choice(['permit', 'deny'])
        rule = f"{action} tcp host {src_ip} host {dst_ip} eq {port}"
        acl.append(rule)
    return acl

def configure_acl_on_device(device):
    try:
        netmiko_device = {
            'host': device['host'],
            'username': device['username'],
            'password': device['password'],
            'device_type': device['device_type']
        }

        net_connect = ConnectHandler(**netmiko_device)
        net_connect.enable()
        net_connect.send_command('terminal pager 0')

        # Interface'leri çekiyoruz
        output = net_connect.send_command('show nameif')
        interfaces = []
        for line in output.splitlines():
            if "interface" not in line.lower() and line.strip() != '':
                iface = line.split()[1]
                interfaces.append(iface)

        if not interfaces:
            print(f"[!] No interfaces found on {device.get('name', device['host'])}")
            net_connect.disconnect()
            return

        # Interface listesi:
        print(f"\n[+] Available Interfaces on {device.get('name', device['host'])}:")
        for idx, iface in enumerate(interfaces):
            print(f"{idx + 1}: {iface}")

        choice_idx = int(input("\nSelect the interface by number: ")) - 1
        selected_iface = interfaces[choice_idx]
        print(f"\n[!] You selected: {selected_iface}")

        # Random ACL oluşturuyoruz
        acl_name = f"BACKUP_ACL_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        acl_rules = generate_random_acl()
        print(f"\n[*] Generated ACL {acl_name} with rules:")
        for rule in acl_rules:
            print(rule)

        # ASA'ya ACL ve Access-Group uygulama
        commands = [f"access-list {acl_name} extended {rule}" for rule in acl_rules]
        commands.append(f"access-group {acl_name} in interface {selected_iface}")

        print("\n[*] Sending configuration to ASA...")
        net_connect.send_config_set(commands)

        print(f"\n[✔] ACL applied successfully on {device.get('name', device['host'])}!")
        net_connect.disconnect()

    except Exception as e:
        print(f"[X] Error on {device['host']}: {e}")

def main():
    category = "cisco_asa"
    devices = load_inventory(category)

    if not devices:
        print(f"[!] No devices found in category: {category}")
        return

    for device in devices:
        print(f"\n[!] Connecting to {device['host']} ({device.get('name', 'No Name')})...")
        configure_acl_on_device(device)

if __name__ == "__main__":
    main()
