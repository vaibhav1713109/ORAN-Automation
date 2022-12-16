
import json
import subprocess
import time
import paramiko
import glob
import os

f = open('configurations.json')
config = json.load(f)

file1 = open('MC_TC_026_27.xml').read()
file2 = open('interface.xml').read()
file3 = open('processing.xml').read()
file4 = open('uplane_26.xml').read()
file2 = file2.format(ru_mac=config["ru_mac"])
file3 = file3.format(ru_mac=config["ru_mac"],du_mac=config["du_mac"])
file4 = file4.format(arfcn=config["arfcn"])
file1 = file1.format(interface = file2,processing=file3,uplane=file4)
file5 = open('C:\\ProgramData\\Keysight\\MPlane\\Client\\duprofile\\v2\\MC_TC_026.xml', 'w')
file5 = file5.writelines(file1)

def write_json(new_data, filename='C:\\ProgramData\\Keysight\\MPlane\\Client\\duprofile\\v2\\client_config.json'):
    with open(filename,'w') as file:
        json.dump(new_data, file, indent = 4)

with open ("C:\\ProgramData\\Keysight\\MPlane\\Client\\duprofile\\v2\\client_config.json") as json_file:
    data=json.load(json_file)
    temp=data["general"]
    x= {"call-flow-xml": ["MC_TC_026.xml"], "fail_call_home": "False", "username": "operator", "password": "admin123", "tls-hostname": "operator",}
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

os.rename(latest_file,'MPlane_Toolkit_Logs_026.log')

time.sleep(2)

f.close()

print("\n********************EXECUTED********************\n")

