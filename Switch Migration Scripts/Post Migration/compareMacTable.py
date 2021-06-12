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
        newTableJson = con.send_command("show mac address-table dynamic", use_textfsm=True)

        #to read the file from another script
        with open("oldMacTable.json") as f:
            oldTableJson = json.load(f)


        pprint(newTableJson)
        print("-----------------")
        pprint(oldTableJson)
