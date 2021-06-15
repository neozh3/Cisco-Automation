from netmiko import ConnectHandler
from pprint import pprint
import time

mySwitch = {
    'device_type': 'cisco_ios',
    'host':   '192.168.30.133',
    'username': 'cisco',
    'password': 'cisco',
    'secret': 'cisco',     # optional, defaults to ''
}

# takes output of show int status, return a list of connected ports


def getConnectedPorts(shIntStatusOp):
    conPorts = []
    for iface in shIntStatusOp:
        if iface['status'] == 'connected':
            conPorts.append(iface['port'])
    return conPorts  # eg.['Gi0/0', 'Gi0/1', 'Gi0/2', 'Gi0/3']

# takes a list of ports, run show interface {portnumber} and extract relevant values


def getIfacecInfo(conPorts):
    '''This function prints out interfaces that have errors from show interface {portnumber}
        and returns a nested dict of values from the attr list
                ----Example output of function - nested dict ----
    {'GigabitEthernet0/0': {'address': '4000.0001.0004',
                        'crc': '0',
                        'duplex': 'Auto Duplex',
                        'input_errors': '0',
                        'input_packets': '6913',
                        'output_errors': '0',
                        'output_packets': '11675',
                        'speed': 'Auto Speed'},
    'GigabitEthernet0/1': {'address': '5000.0001.0002',...
    '''
    ifaceValues = {}

    # values of interest
    # use this con.send_command("show int g0/1", use_textfsm=True) to test for available values
    attr = ["address", "crc", "duplex", "input_errors",
            "input_packets", "output_errors", "output_packets", "speed"]

    # edit these 2 lists if there are new values to check
    toCheckifZero = ["crc", "input_errors", "output_errors"]
    toCheckifNotZero = ["input_packets", "output_packets"]

    print("####################################################")
    print("# Checking for interface errors on connected ports #")
    print("####################################################")
    print("\n")

    clearCntInput = input(r"Do you want to clear counters [y/n]: ")
    print("\n")
    if clearCntInput == 'y':
        # --clear counters and wait 5 seconds--
        con.send_command("clear counters", expect_string=r"[confirm]")
        con.send_command("\n")
        time.sleep(5)
        # -------------------------------------

    for port in conPorts:
        # --- to get attributes of interest from show show int {portnumber} ---
        command = f"show interface {port}"
        op = con.send_command(command, use_textfsm=True)
        # get iface number eg. GigabitEthernet0/0 to use as dict key
        iface = op[0]["interface"]
        # only keep keys that is in attr list
        ifaceValues[iface] = {v: op[0][v] for v in attr}

        # --- to check for errors in the interface by checking values of crc errors etc
        for value in toCheckifZero:
            contChecking = True
            if op[0][value] != '0':
                print(f"ERROR - There is error in interface {iface}")
                contChecking = False
                break
        if contChecking == True:
            for value in toCheckifNotZero:
                if op[0][value] == 0:
                    print(f"ERROR - There is error in interface {iface}")
                    break
                else:
                    print(f"{iface} interface is ok")
                    break

    return ifaceValues


def checkArpForIp(ip):
    op = con.send_command(f"show ip arp | in {ip}", use_textfsm=True)

    if op == "":
        print(f"ERROR - Unable to arp for gateway {ip}")
    else:
        arpSuccess = False
        for value in op:
            if ip in value['address'] == ip:
                print(f"arp for gateway {ip} successful")
                arpSuccess = True
        if arpSuccess == False:
            print(f"ERROR - Unable to arp for gateway {ip}")


if __name__ == "__main__":

    cmd = ["show int status", "show mac address-table dynamic"]

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

        shIntStatusOp = cmdOutput['show int status']
        ###example value###
        # [{'duplex': 'a-full',
        #  'fc_mode': '',
        #  'name': '',
        #  'port': 'Gi0/0',
        #  'speed': 'auto',
        #  'status': 'connected',
        #  'type': 'RJ45',
        #  'vlan': 'routed'}, {..Next dict..}]

        shMacTableOp = cmdOutput['show mac address-table dynamic']
        ###exampe value###
        # [{'destination_address': '2200.0001.0002',
        #  'destination_port': 'Gi0/2',
        #  'type': 'DYNAMIC',
        #  'vlan': '1'},
        # {'destination_address': '5000.0011.1111',
        #  'destination_port': 'Gi0/1',
        #  'type': 'DYNAMIC',
        #  'vlan': '1'}]

        connectedPorts = getConnectedPorts(shIntStatusOp)

        ifaceInfo = getIfacecInfo(connectedPorts)
        # print(ifacecInfo.keys())
        
        print("\n")
        gwInput = input(r"Is there gateway configured [y/n]: ")
        print("\n")

        if gwInput == 'y':

            print("####################################")
            print("# Checking if gateway is reachable #")
            print("####################################")
            print("\n")
            gateway = con.send_command(r"show run | in gateway")
            # assume that show run | in gateway output is - ip default-gateway {ipaddr}
            # slice first part of string to only get the ip address
            # sometimes slice not working?? sometimes there will be another space infront of ip
            gateway = gateway[19:]
            gateway = gateway.lstrip()

            # ping gateway to trigger arp request
            con.send_command(r"ping {gateway}")

            checkArpForIp(gateway)
        print("--------Script Completed--------")
