
import json
import subprocess
import time
import paramiko
import glob
import os

def write_json(new_data, filename='C:\\ProgramData\\Keysight\\MPlane\\Client\\duprofile\\v2\\client_config.json'):
    with open(filename,'w') as file:
        json.dump(new_data, file, indent = 4)

with open ("C:\\ProgramData\\Keysight\\MPlane\\Client\\duprofile\\v2\\client_config.json") as json_file:
    data=json.load(json_file)
    temp=data["general"]
    x= {"call-flow-xml": ["MC_TC_001.xml"], "fail_call_home": "False", "username": "operator", "password": "admin123", "tls-hostname": "operator",}
    temp.update(x)

write_json(data)

f = open('configurations.json')
config = json.load(f)

try:
    command1="cd {}; rm -rf {};".format(config['sys_log_path'],config['sys_log_file'])
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=config["o_ru_ip"],username=config["username"],password=config["password"])
    stdin, stdout, stderr = ssh.exec_command(command1)
    stdout.channel.set_combine_stderr(True)
    output = stdout.readlines()
except paramiko.ssh_exception.NoValidConnectionsError as stderr:
    print("**",end=" ")
    pass

except:
    print("*",end=" ")
    pass

time.sleep(2)

subprocess.run(f"MPlaneClient.bat --ip {config['dhcp_server_ip']} --duprofile duprofile\\v2 --ruprofile ruprofile\\v2", shell=True)

time.sleep(2)

print("\n********************SYSTEM LOGS********************\n")
try:
    command2="cd {}; cat {};".format(config['sys_log_path'],config['sys_log_file'])
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=config["o_ru_ip"],username=config["username"],password=config["password"])
    stdin, stdout, stderr = ssh.exec_command(command2)
    lines = stdout.readlines()
    for i in lines:
        print(i,end='')
except paramiko.ssh_exception.NoValidConnectionsError as stderr:
    print("**",end=" ")
    pass

except:
    print("*",end=" ")
    pass







list_of_files = glob.glob('C:\\ProgramData\\Keysight\\MPlane\\Client\\log\\mPlaneClient_*.log*')
latest_file = max(list_of_files, key=os.path.getctime)
print(latest_file)

os.rename(latest_file,'MPlane_Toolkit_Logs_001.log')

time.sleep(2)

f.close()

print("\n********************EXECUTED********************\n")

