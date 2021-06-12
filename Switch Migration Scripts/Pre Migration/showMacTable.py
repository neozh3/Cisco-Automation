import json
from netmiko import ConnectHandler
from pprint import pprint

mySwitch = {
    'device_type': 'cisco_ios',
    'host':   '192.168.30.133',
    'username': 'cisco',
    'password': 'cisco',
    'secret': 'cisco',}   # optional, defaults to ''


if __name__ == "__main__":

    with ConnectHandler(**mySwitch) as con:
        con.disable_paging() #term len 0
        con.enable()         #enable
        macTable = con.send_command("show mac address-table dynamic", use_textfsm=True)

        with open("oldMacTable.json", 'w') as f:
            json.dump(macTable, f)

        with open("oldMacTable.json") as z:
            s = json.load(z)
            pprint(s)
