import paramiko
import subprocess
import json
import time

print("\n********************Enter Configurations********************\n")

subprocess.run("python Config.py", shell=True)

f = open('configurations.json')
config = json.load(f)

subprocess.run("python disable_master.py",shell=True)
subprocess.run("python enable_master.py",shell=True)
time.sleep(15)
print("\n********************STARTING EXECUTION PLEASE WAIT********************\n")

while 1:
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        connected=ssh.connect(hostname=config["o_ru_ip"],username=config["username"],password=config["password"])
        if connected==None:
            print("\n********************Connection Established with O-RU********************\n")
            break

    except paramiko.ssh_exception.NoValidConnectionsError as stderr:
        pass

    except:
        pass

print("\n********************MC_TC_001********************\n")

subprocess.run("python MC_TC_001.py",shell=True)

print("\n********************MC_TC_002********************\n")

subprocess.run("python MC_TC_002.py",shell=True)

print("\n********************MC_TC_003********************\n")

subprocess.run("python MC_TC_003.py",shell=True)
try:

    cmd1="tail -n 6 /var/log/synctimingptp2.log"
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=config["o_ru_ip"],username=config["username"],password=config["password"])
    stdin, stdout, stderr = ssh.exec_command(cmd1)
    stdout.channel.set_combine_stderr(True)
    output = stdout.readlines()
    kword = ('not synchronized')
    while 1:
        if kword.encode('utf-8') in output:
            pass
        else:
            break
except paramiko.ssh_exception.NoValidConnectionsError as stderr:
    pass

except:
    pass




print("\n********************Sync_State:LOCKED********************\n")


print("\n********************MC_TC_007********************\n")

subprocess.run("python MC_TC_007.py",shell=True)

try:
    cmd2="sysrepocfg --import=/media/sd-mmcblk0p4/O-RAN/default/startup.xml -d startup; sync"
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=config["o_ru_ip"],username=config["username"],password=config["password"])
    stdin, stdout, stderr = ssh.exec_command(cmd2)
    stdout.channel.set_combine_stderr(True)
    output = stdout.readlines()
except paramiko.ssh_exception.NoValidConnectionsError as stderr:
    pass

except:
    pass


print("\n********************MC_TC_008 & MC_TC_009********************\n")

subprocess.run("python MC_TC_008_9.py",shell=True)

print("\n********************O-RU Went for Reboot********************\n")

while 1:
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        connected=ssh.connect(hostname=config["o_ru_ip"],username=config["username"],password=config["password"])
        if connected==None:
            print("\n********************Connection Established with O-RU********************\n")
            break

    except paramiko.ssh_exception.NoValidConnectionsError as stderr:
        pass

    except:
        pass


print("\n********************MC_TC_010********************\n")

subprocess.run("python MC_TC_010.py",shell=True)

print("\n********************MC_TC_011********************\n")

subprocess.run("python MC_TC_011.py",shell=True)

subprocess.run("python disable_master.py",shell=True)
subprocess.run("python enable_master.py",shell=True)
time.sleep(15)

while 1:
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        connected=ssh.connect(hostname=config["o_ru_ip"],username=config["username"],password=config["password"])
        if connected==None:
            print("\n********************Connection Established with O-RU********************\n")
            break

    except paramiko.ssh_exception.NoValidConnectionsError as stderr:
        pass

print("\n********************MC_TC_012********************\n")

subprocess.run("python MC_TC_012.py",shell=True)

print("\n********************Turning Master Off********************\n")

subprocess.run("python disable_master.py",shell=True)
time.sleep(15)

while 1:
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        connected=ssh.connect(hostname=config["o_ru_ip"],username=config["username"],password=config["password"])
        if connected==None:
            print("\n********************Connection Established with O-RU********************\n")
            break

    except paramiko.ssh_exception.NoValidConnectionsError as stderr:
        pass

    except:
        pass

print("\n********************MC_TC_013********************\n")

subprocess.run("python MC_TC_013.py",shell=True)

print("\n********************MC_TC_018********************\n")

subprocess.run("python MC_TC_018.py",shell=True)

print("\n********************MC_TC_019********************\n")

subprocess.run("python MC_TC_019.py",shell=True)

print("\n********************MC_TC_020********************\n")

subprocess.run("python MC_TC_020.py",shell=True)

print("\n********************MC_TC_021********************\n")

subprocess.run("python MC_TC_021.py",shell=True)

print("\n********************MC_TC_022********************\n")

subprocess.run("python MC_TC_022.py",shell=True)

print("\n********************MC_TC_023********************\n")

subprocess.run("python MC_TC_023.py",shell=True)

print("\n********************MC_TC_026********************\n")

subprocess.run("python MC_TC_026.py",shell=True)

print("\n********************MC_TC_027********************\n")

subprocess.run("python MC_TC_027.py",shell=True)

f.close()

print("\n********************EXECUTION COMPLETED********************\n")
