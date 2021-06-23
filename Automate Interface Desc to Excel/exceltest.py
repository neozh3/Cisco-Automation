from netmiko import ConnectHandler
from pprint import pprint
import textfsm
import os
from tabulate import tabulate


#---------------CHANGE THESE-----------------------------------------#
mySwitch = {
    'device_type': 'cisco_ios',
    'host':   '192.168.30.133',
    'username': 'cisco',
    'password': 'cisco',
    'secret': 'cisco',     # optional, defaults to ''
}

templatePath = r"C:\Program Files\ntc-templates-master\ntc_templates\templates"

#----------------------- END ----------------------------------------#


def convertTxtfsmOp(header, result):
    '''convert textfsm output to netmiko textfsm output(JSON)'''
    output = []
    for n in range(len(result)):
        res = {header[i].lower(): result[n][i] for i in range(len(header))}
        output.append(res)

    return output


if __name__ == "__main__":

    cmd = ["show int desc"]

    with ConnectHandler(**mySwitch) as con:
        con.disable_paging()  # term len 0
        con.enable()  # enable
        prompt = con.find_prompt()  # get the prompt eg. ESW01#
        hostname = prompt[0:-1]
        # Dict with the key as command entered, value as output
        # eg. to access show int status output -> cmdOutput['show int status']
        cmdOutput = {}
        for c in cmd:
            # print(c)
            op = con.send_command(c, use_textfsm=True)
            cmdOutput[c] = op

        intDesc = cmdOutput['show int desc']
        # Example output
        # [{'descrip': 'DESC1', 'port': 'Gi0/0', 'protocol': 'up', 'status': 'up'},
        # {'descrip': 'DESC2', 'port': 'Gi0/1', 'protocol': 'up', 'status': 'up'}, ... ]
        pprint(intDesc)
        print(hostname)
