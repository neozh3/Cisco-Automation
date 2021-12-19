
ctr = 0
excel_filename = "inventory.csv"
hosts_filename = "hosts.yaml"
defaults_filename = "defaults.yaml"
groups_filename = "groups.yaml"
config_filename = "config.yaml"

device = {}

with open(excel_filename, "r") as excel_csv:
    for line in excel_csv:
        if ctr == 0:
            ctr+=1  # Skip the coumn header
        else:
            # save the csv as a dictionary
            hostname,ip,login = line.replace(' ','').strip().split(',')
            device[hostname] = {'hostname': ip, 'groups': [login]}

def create_hosts_yml():
    with open(hosts_filename, "w+") as yf :
        yf.write(f"---\n")
        for k,v in device.items():
            yf.write(f"{k} : \n")
            yf.write(f"    hostname : {v['hostname']}\n")
            yf.write(f"    groups :\n")
            yf.write(f"        - {v['groups'][0]}\n")

def create_groups_yml():
    with open(groups_filename, "w+") as yf :
        yf.write(f"---\n")
        yf.write(f"tacacs_grp : \n")
        yf.write(f'    username : "TACACSCUSERNAME"\n')
        yf.write(f'    password : "TACACSPASSWORD"\n')
        yf.write(f"\n")
        yf.write(f"local_grp : \n")
        yf.write(f'    username : "LOCALUSERNAME"\n')
        yf.write(f'    password : "LOCALPASSWORD"\n')

def create_defaults_yml():
    with open(defaults_filename, "w+") as yf :
        yf.write(f"---\n")
        yf.write(f'platform : "ios"\n')

def create_config_yml():
    with open(config_filename, "w+") as yf :
        yf.write(f"---\n")
        yf.write(f"inventory : \n")
        yf.write(f'    plugin: SimpleInventory\n')
        yf.write(f'    options :\n')
        yf.write(f'        host_file : "hosts.yaml"\n')
        yf.write(f'        group_file : "groups.yaml"\n')
        yf.write(f'        defaults_file : "defaults.yaml"\n')
        yf.write(f"\n")
        yf.write(f"runner : \n")
        yf.write(f'    plugin: threaded\n')
        yf.write(f'    options :\n')
        yf.write(f'        num_workers : 2')


create_hosts_yml()
create_groups_yml()
create_config_yml()
create_defaults_yml()
