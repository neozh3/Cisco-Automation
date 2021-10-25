# This script ssh into a cisco device, and perform commands stated in commands.txt
# It will output the results of the commands in a txt file similar to when you are logging your session via ssh


from netmiko import ConnectHandler
from pprint import pprint

mySwitch = {
    'device_type': 'cisco_ios',
    'host':   '192.168.30.131',
    'username': 'cisco',
    'password': 'cisco',
    'secret': 'cisco',     # optional, defaults to ''
}

commands = "commands.txt"
with open(commands) as f:
    #create a list with commands as string
    cmd = f.read().splitlines()

#cmd = ["show ip int br", "show int status","show version"]

with ConnectHandler(**mySwitch) as con:
    con.disable_paging() #term len 0
    con.enable()         #enable
    prompt = con.find_prompt() #get the prompt eg. ESW01#
    hostname = prompt[:-1]
    #list with the outputs of commands entered
    cmdOutput = []
    for c in cmd:
        #print(c)
        op = con.send_command(c)
        cmdOutput.append(op)


with open(f"{hostname}.txt", "w") as f:
    #netmiko remove prompt from command output, to manually put back
    for i in range(len(cmd)):
        f.write(prompt)
        f.write(cmd[i])
        f.write('\n')
        f.write(cmdOutput[i])
        f.write('\n')
        f.write('\n')


