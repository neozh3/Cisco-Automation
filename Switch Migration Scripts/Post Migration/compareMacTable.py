from netmiko import ConnectHandler
from pprint import pprint
import textfsm
import glob
import os
from tabulate import tabulate

# this script reads multiple txt files with the output of show mac address-table
# txt file should only include the command output - remove "hostname# show mac table"
# txt file filename should be the hostname of the switch - To be used in this script as the hostname

# script will compile all the mac table txt files and compare with the new mac table which is taken
# by sshing into the new switch and run the show mac address-table command
# both tables wil be compared and the script will find if the mac exists on new switch and if vlan is same
#
#--------------------- Example Output ------------------------------#

# New Port    Old Port + Switch    VLAN                MAC Address
# ----------  -------------------  ------------------  --------------
# Gi0/2       Gi0/2 esw01          Wrong VLAN- Old: 3  2200.0001.0002
# NOT FOUND   Gi0/1 esw01          1                   8888.0011.1111
# Gi0/1       Gi0/2 esw02          1                   5000.0011.1111
# Gi1/0       Gi0/1 esw02          1                   5000.0022.2222
# NOT FOUND   Gi0/2 esw03          1                   3333.3333.3333
# NOT FOUND   Gi0/1 esw03          1                   3232.3232.3232

#--------------------------------------------------------------------#

mySwitch = {
    'device_type': 'cisco_ios',
    'host':   '192.168.30.133',
    'username': 'cisco',
    'password': 'cisco',
    'secret': 'cisco',     # optional, defaults to ''
}


def convertTxtfsmOp(header, result):
    '''convert textfsm output to netmiko textfsm output(JSON)'''
    output = []
    for n in range(len(result)):
        res = {header[i].lower(): result[n][i] for i in range(len(header))}
        output.append(res)

    return output


if __name__ == "__main__":

    cmd = ["show mac address-table dynamic"]

    with ConnectHandler(**mySwitch) as con:
        con.disable_paging()  # term len 0
        con.enable()  # enable
        #prompt = con.find_prompt() #get the prompt eg. ESW01#

        # Dict with the key as command entered, value as output
        # eg. to access show int status output -> cmdOutput['show int status']
        cmdOutput = {}
        for c in cmd:
            # print(c)
            op = con.send_command(c, use_textfsm=True)
            cmdOutput[c] = op

        newShMacTableOp = cmdOutput['show mac address-table dynamic']
        ###exampe value###
        # [{'destination_address': '2200.0001.0002',
        #  'destination_port': 'Gi0/2',
        #  'type': 'DYNAMIC',
        #  'vlan': '1'},
        # {'destination_address': '5000.0011.1111',
        #  'destination_port': 'Gi0/1',
        #  'type': 'DYNAMIC',
        #  'vlan': '1'}]

    # pprint(shMacTableOp)

    templatePath = r"C:\Program Files\ntc-templates-master\ntc_templates\templates\cisco_ios_show_mac-address-table.textfsm"
    combinedOldMacTable = []

    for filename in glob.glob('*.txt'):

        with open(templatePath) as template, open(os.path.join(os.getcwd(), filename), 'r') as output:
            table = textfsm.TextFSM(template)
            header = table.header
            result = table.ParseText(output.read())
            for row in result:
                row[3] = row[3] + f" {filename.split('.')[0]}"

        oldShMacTableOp = convertTxtfsmOp(header, result)

        # pprint(oldShMacTableOp)
        for v in oldShMacTableOp:
            combinedOldMacTable.append(v)

    # ----compare and print the 2 mac tables----
    # NOT TESTED FOR TRUNK PORTS WITH MULTIPLE VLANS YET
    # once stable, can consider just printing error only
    # header for print output
    compareHdr = ["New Port", "Old Port + Switch", "VLAN", "MAC Address"]
    finalResult = []
    for entry in combinedOldMacTable:
        tmp = []
        oldPort = entry['destination_port']
        vlan = entry['vlan']
        mac = entry['destination_address']

        for nEntry in newShMacTableOp:
            # if mac is the same
            if nEntry['destination_address'] == mac:
                newPort = nEntry['destination_port']
                # if same vlan
                if vlan == nEntry['vlan']:
                    vlanOp = vlan
                else:
                    vlanOp = f"Wrong VLAN- Old: {vlan}"

                tmp = [newPort, oldPort, vlanOp, mac]
        # if tmp list is empty, means old mac address does not appear in new switch mac table
        if not tmp:
            tmp = ["NOT FOUND", oldPort, vlan, mac]

        finalResult.append(tmp)

    print(tabulate(finalResult, headers=compareHdr))
