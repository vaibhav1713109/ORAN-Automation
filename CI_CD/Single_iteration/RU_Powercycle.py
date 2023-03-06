import logging
import subprocess
import time
import re
import sys,os
from configparser import ConfigParser
from datetime import datetime

###############################################################################
## Directory Path
###############################################################################
dir_name = os.path.dirname(os.path.abspath(__file__))
parent = os.path.dirname(dir_name)
# print(parent)
sys.path.append(parent)

########################################################################
## For reading data from .ini file
########################################################################
configur = ConfigParser()
configur.read('{}/require/inputs.ini'.format(parent))
from require.Notification import *

# Time taken for reboot
wait_time = configur.getint('INFO','wait_time')
summary = []

logging.basicConfig(level=logging.INFO)

class PowerCycleError(Exception):
    def __init__(self, message, error_code):
        super().__init__(message)
        self.error_code = error_code

# Define error codes for custom exceptions
ERROR_NO_INTERFACES = 1001
ERROR_NO_10G_INTERFACE = 1002
ERROR_NO_LINK_TO_ORU = 1003
ERROR_IP_OBTAIN_FAILED = 1004
ERROR_PING_TO_ORU_FAILED = 1005
ERROR_DHCP_SERVER_NOT_RUNNING = 1006
ERROR_DHCP_SERVER_RESTART_FAILED = 1007

def identify_10G_interface():
    cmd = "ls /sys/class/net/"
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if err:
        raise PowerCycleError(f"Failed to list network interfaces: {err.decode()}", ERROR_NO_INTERFACES)
    
    interfaces = out.decode().split()
    for interface in interfaces:
        cmd = f"ethtool {interface} | grep 'Speed:' | awk '{{print $2}}'"
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        print(out.decode())
        if '10000' in out.decode():
            return interface
    
    raise PowerCycleError("No 10G interface found.", ERROR_NO_10G_INTERFACE)

def check_link_status(interface):
    cmd = f"ethtool {interface} | grep 'Link detected' | awk '{{print $3}}'"
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    # print(out.decode(),err)
    if not err:
        if 'yes' in out.decode():
            append_data_and_print(f"Link Detection || successful.",summary)
            return True
    raise PowerCycleError("Link to O-RU not detected.", ERROR_NO_LINK_TO_ORU)

def is_active_DHCP_server_status():
    cmd = "systemctl status isc-dhcp-server.service"
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if "Active: active (running)" in out.decode():
        logging.info("DHCP server is running.")
        return True
    return False

def restart_dhcp_server():
    cmd = "sudo systemctl restart isc-dhcp-server.service"
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if err:
        return False
    return True

def is_DHCP_server_running():
    if is_active_DHCP_server_status():
        return True
    else:
        if restart_dhcp_server():
            time.sleep(1)
            if is_active_DHCP_server_status():
                return True
            else:
                raise PowerCycleError("DHCP server is not Active.", ERROR_DHCP_SERVER_NOT_RUNNING)
        else:
            raise PowerCycleError("Failed to start DHCP server.", ERROR_DHCP_SERVER_RESTART_FAILED)

def append_data_and_print(data,summary_list):
    print('-'*100)
    print(data)
    summary_list.append(data)
    pass

def check_ping(ip):
    cmd = f"ping -c 1 {ip}"
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    print(out)
    if not err:
        if "1 received" in out.decode():
            return True
    return False

def get_ip(interface, static_ip=''):
    if not static_ip:
        Result = subprocess.getoutput('sudo /etc/init.d/isc-dhcp-server status')
        Result = Result.split('\n')
        for line in Result:
            if "DHCPACK on" in line and f"via {interface}" in line: 
                pattern = '(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
                ans = re.findall(pattern,line)
                dhcp_ip = ans[0]
        print(f"DHCP IP: {dhcp_ip}")
    else:
        return False

def main():
    try:
        interface_name = identify_10G_interface()
        if interface_name is not None:
            append_data_and_print(f"10G interface {interface_name} found || successful.",summary)
            # Turn off O-RU
            subprocess.run(["curl", "-u", "admin:rpsadmin", f"http://172.25.96.188/rps?SetPower=1+0"])
            append_data_and_print("Power OFF || successful.",summary)
            time.sleep(7)
            # Turn on O-RU
            subprocess.run(["curl", "-u", "admin:rpsadmin", f"http://172.25.96.188/rps?SetPower=1+1"])
            append_data_and_print("Power ON || successful.",summary)
            time.sleep(30)
            if check_link_status(interface_name):
                is_DHCP_server_running()
                time.sleep(wait_time)
                ip = get_ip(interface_name, False)
                if ip:
                    append_data_and_print("DHCP IP Obtained || successful.",summary)
                    append_data_and_print("Power cycle || successful.",summary)
                else:
                    ip = configur.get('INFO','static_ip')
                    append_data_and_print("DHCP IP not Obtained || Checking for static_ip.",summary)
                    append_data_and_print("Static IP Obtained || successful.",summary)

                if check_ping(ip):
                    append_data_and_print("Power cycle || Fail.",summary)
                    append_data_and_print("Power cycle || successful.",summary)
                else:
                    raise PowerCycleError("Ping to O-RU failed. ", ERROR_PING_TO_ORU_FAILED)
                return True
    except PowerCycleError as e:
        print(f"Error: {e}")
        append_data_and_print(f"Fail Reason || {e}.",summary)
        return False

if __name__ == '__main__':
    num_iterations = 1
    start_time = datetime.fromtimestamp(int(time.time()))
    end_time = datetime.fromtimestamp(int(time.time()))
    Pass, Fail = 0, 0
    try:
        temp = start_time
        Test_procedure = [f"{'='*100}\nTest case *RU Powercycle* Started!! Status: Running\n{'='*100}",'** Test Coverage **'.center(50),'Power off',
                    'Power ON','Link Detection','Ping DHCP/STATIC IP', 'Start Time : {}'.format(start_time),'='*100]
        notification('\n'.join(Test_procedure))
        if len(sys.argv) > 1:
            num_iterations = int(sys.argv[1])
        for i in range(num_iterations):
            print(f"Iteration {i+1}")
            print("="*40)
            Result = main()
            print(Result)
            if Result:
                status = 'Pass'
                Pass+=1
            else:
                status = 'Fail'
                Fail+=1
            end_time = datetime.fromtimestamp(int(time.time()))
            st_time = 'Start Time : {}'.format(start_time)
            en_time = 'End Time : {}'.format(end_time)
            execution_time = 'Execution Time is : {}'.format(end_time-temp)
            temp = end_time
            print('-'*100)
            print(f'{st_time}\n{en_time}\n{execution_time}')
            summary.insert(0,'******* Result *******'.center(50))
            summary.insert(0,'='*100)
            notification('\n'.join(summary))
            notification(f'{st_time}\n{en_time}\n{execution_time}')
            notification(f"{'='*100}\nRU Powercycle\t\t || \t\t{status}\n{'='*100}")
    except Exception as e:
        print(e)

    finally:
        notification(f'Total Iteration : {num_iterations}\nPass : {Pass}\nFail : {Fail}\nTotal Execution Time : {end_time-start_time}')
        pass

