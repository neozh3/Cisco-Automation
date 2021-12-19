from nornir import InitNornir
from nornir_utils.plugins.functions import print_result
from nornir_netmiko import netmiko_send_command

nr = InitNornir(config_file="config.yaml")

res = nr.run(task=netmiko_send_command,command_string="wr")

print_result(res)