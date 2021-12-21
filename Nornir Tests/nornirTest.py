from nornir import InitNornir
from nornir.core.inventory import Group
from nornir_utils.plugins.functions import print_result
from nornir_utils.plugins.tasks.files import write_file
from nornir_netmiko import netmiko_send_command
from nornir.core.filter import F

nr = InitNornir(config_file="config.yaml")


#routers = nr.filter(F(groups__contains="local_grp"))
#res = routers.run(task=netmiko_send_command,command_string="show ip int br | ex unas")
res = nr.run(task=netmiko_send_command,command_string="show ip int br | ex unas")
print_result(res)


#cli output
#a = res["R1"][0].result
