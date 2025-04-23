import yaml

def load_inventory(category):
    with open("inventory.yaml") as f:
        inventory = yaml.safe_load(f)
    return inventory.get(category, [])

def load_ftp_info():
    with open("inventory.yaml") as f:
        inventory = yaml.safe_load(f)
    return inventory.get("ftp", {})
