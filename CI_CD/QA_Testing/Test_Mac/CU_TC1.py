import sys
import time
import paramiko
import threading
import pyvisa as visa
import os
from configparser import ConfigParser
from ru_sync_and_ru_stat import *

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print("root_dir",root_dir)
configur = ConfigParser()
configur.read('{}/TestMac/inputs.ini'.format(root_dir))

class vxt_configuration_and_result_capture():
    def __init__(self,file_name,ScreenShot) -> None:
        self.vxt_add = 'TCPIP::172.25.96.160::inst1::INSTR'
        #self.vxt_add = 'TCPIP::172.25.96.131::inst3::INSTR'
        self.state_file = file_name
        self.Local_path = "/comon-space/QA_Testing/CUPLANE/TestMac/StateFiles/"        
        self.remote_folder = "C:\\Users\\Administrator\\Documents\\CU_Plane_Conf"
        self.evm_limit = 5
        self.power_limit = [23,25]
        self.clgc_gain_calculation_time = 5
        """
        self.basic_scpis = [
                    ":INST:SEL NR5G", ":OUTP:STAT OFF", ":FEED:RF:PORT:INP RFIN",':CONF:EVM', ":DISP:EVM:VIEW NORM",
                    ":INIT:CONT ON",f'''MMEMory:LOAD:EVM:SET ALL,"{self.scp_path}"''']
        """
        remote_file = os.path.normpath(self.remote_folder+"\\"+self.state_file)
        #cmd = f'MMEM:LOAD:STAT "{self.remote_folder}{self.state_file}"'
        self.basic_scpis = [f':MMEMory:LOAD:STAT "{remote_file}"']
        #filePathPc1 = "/comon-space/QA_Testing/CUPLANE/TestMac/Results/"
        filePathPc1 = "/home/sebu.mathew/QA_CICD/"
        self.filePathPc = os.path.normpath(filePathPc1+ScreenShot)

    def visa_connection(self,vxt_add = None, gpib_id= None):
        try:
            if(vxt_add):
                self.rm = visa.ResourceManager()
                self.device = self.rm.open_resource(vxt_add)
                print(f'Connected to {self.device}')
                return 0
            elif(gpib_id):
                self.rm = visa.ResourceManager()
                self.device = self.rm.open_resource('GPIB0::{}::INSTR'.format(gpib_id)) 
                return 0       
            else:
                Error = 'Visa_connection Error: No valid instrument IP or GBIB ID given'
                print(Error)
                return 100
        except Exception as e:
            Error = f'Visa_connection Error : {e}'
            print(Error)
            return 100

    def send_file_to_vxt(self, local_path,file_name,remote_path):
        try:
            if not self.device:
                print("Device not connected")
                return 100
            local_file = os.path.join(local_path, file_name)
            if not os.path.isfile(local_file):
                print(f"File not found: {local_file}")
                return 404

            with open(local_file, 'rb') as f:
                read_data = f.read()

            #remote_file = os.path.join(remote_path, file_name)
            rem_file = os.path.normpath(remote_path+'\\'+file_name)            
            self.device.write(f':MMEMory:MDIRectory "{remote_path}"')
            status_complte = self.device.query("*OPC?")
            self.device.write_binary_values(f':MMEMory:DATA "{rem_file}",', read_data, datatype='B')
            status_complete = self.device.query("*OPC?")
            if int(status_complete) != 1:
                print("not completed",status_complete)
                error = f'send_file_to_VXT Error: Failed to transfer {local_file} to {rem_file}'
                return 1303
            else:
                print(f'File {local_file} successfully transferred to {rem_file}')
                return 0
            # include one more SCPI for file check here

        except Exception as e:
            error = f'send_file_to_VXT Error: {e}'
            print(error)
            return 500
        
    def clear_status_reg_of_device(self):
        self.device.write('*CLS')                                #Clear Status Register of device
        self.device.write('*WAI')                                #Wait till Clear command is complete

    def reset_device(self):
        self.device.write('*RST')                                #Reset the device
        self.device.write('*WAI')                                #Wait till Reset command is complete

    def scpi_write(self, cmnd):
        print(cmnd)
        self.device.write(cmnd)
        self.device.write('*WAI')
        status = self.device.query("*OPC?")
        if int(status) != 1: # Check for any error during the execution of SCPI command
            return 1
        else:
            return 0

    def vxt_configuration(self,scpi_cmds):
        for scpi in scpi_cmds:
            if not self.scpi_write(scpi):
                continue
            else:
                return 1
        return 0


    def fetch_EVM_power(self):
        Error = ''
        captured_evm = 0
        output_power = 0
        time.sleep(2)
        try:
            self.device.timeout = 5000
            CMD = ':FETCh:EVM000001?'
            Res = self.device.query_ascii_values(CMD)
            #time.sleep(1)
            print(Res)
            captured_evm = "{:.2f}".format(float(Res[1]))
            output_power = "{:.2f}".format(float(Res[0]))
        except Exception as e:
            Error = self.device.write("SYST:ERR?")
            #Error = 'fetch_EVM_power Error : {}'.format(e))
            print(Error)
            return "failed","failed",100
        if float(captured_evm) < float(self.evm_limit) and (float(output_power) > float(self.power_limit[0]) and float(output_power) < float(self.power_limit[1])):
            return captured_evm,output_power, 0
        else:
            return captured_evm,output_power, 1 

    def verify_result_and_capture_screenshot(self):
        try:
            # power_result = self.Check_Power()
            power_evm_result = self.fetch_EVM_power()
            #filepath = r"C:\temp\capture.png"
            filepath = r"C:\Users\Administrator\Documents\capture.png"
            self.device.write(":MMEM:STOR:SCR '{}'".format(filepath))
            status = self.device.query('*OPC?')
            print("print taken")
            time.sleep(5)
            # image=r"C:\Users\Administrator\Documents\Keysight\Instrument\NR5G\screen\capture.png"
            ResultData = bytes(self.device.query_binary_values(f'MMEM:DATA? "{filepath}"', datatype='s'))
            status = self.device.query('*OPC?')
            newFile = open(self.filePathPc, "wb")
            newFile.write(ResultData)
            newFile.close()
            print("Constellation Saved")
            # print(power_evm_result)
            if power_evm_result[-1] != 0:
                Error = f'Fail due to unexpected Power/EVM : {power_evm_result[1]} or EVM : {power_evm_result[0]}'
                print(Error)
                return 1
            print(f'{0}\nChannel Power : {power_evm_result[1]}\nEVM : {power_evm_result[0]}\n{0}'.format('*'*100))
            return 0
        except Exception as e:
            Error = 'Capture_screenshot Error : {}'.format(e)
            print(Error)
            return 100

    def Constellation_check(self):
        try:
            Visa_status = self.visa_connection(self.vxt_add)
            if not Visa_status:
                time.sleep(1)
                self.clear_status_reg_of_device()
                time.sleep(1)
                self.reset_device()
                time.sleep(2)
                if self.send_file_to_vxt(self.Local_path,self.state_file,self.remote_folder):
                    return 200
                time.sleep(2)
                print("send")
                # self.common_cmds.extend(scpi_cmds)
                if not self.vxt_configuration(self.basic_scpis):
                    time.sleep(13)
                    status = self.verify_result_and_capture_screenshot()
                    return status 
                else:
                    print("VXT Configuration are Failed") 
                    return 1
            else:
                return Visa_status
        except Exception as e:
            print(f'Constellation_check Error : {e}')
        
    def disconnect_from_VXT(self):
        try:
            self.device.close()
            self.rm.close()
            print("Disconnected from the VXT!")
        except Exception as e:
            Error = 'Capture_screenshot Error : {}'.format(e)
            print(Error)
            return 100



def VXT_control(state_file,ScreenShot_file):
    vxt_obj = vxt_configuration_and_result_capture(state_file,ScreenShot_file)
    if not vxt_obj.Constellation_check():
        return 0
    else:
        return 1
    vxt_obj.disconnect_from_VXT()

def send_to_testmac(channel, command):
    try:
        channel.send(command + "\n")
        start_time = time.monotonic()
        while True:
            if time.monotonic() - start_time >= 0.1:
                break
            time.sleep(0.01)
        return 0
    except paramiko.SSHException as e:
        print(f"Error sending command: {e}")
        return 5
    
def receive_until(channel, wait_string=None, timeout=None):
    start_time = time.monotonic()
    while True:
        if (time.monotonic() - start_time) < timeout:
            if channel.recv_ready():
                output = channel.recv(1024).decode("utf-8")
                print(output)
                if wait_string in output:
                    return 0
            else:
                if time.monotonic() - start_time < timeout:
                    continue
        else:
            print(f"\nCommand '{command}' timed out after {timeout} seconds\n")
            return 1

def send_and_recieve(channel, command, wait_string=None, timeout=None):
    if timeout or wait_string:
        if send_to_testmac(channel, command) != 0:
            return 5
        status = receive_until(channel, wait_string, timeout)
    else:
        print("Neither Check_string nor Timeout is Provided")    
        return 10
    return status

def command_to_testmac(channel, terminal, command, wait_string=None, is_separation=False, timeout=None):
    if is_separation:
        print("\n" + 25 * "*" + "  " + command + " in " + terminal + "  " + 25 * "*" + "\n")
        status = send_and_recieve(channel, command, wait_string, timeout)
        print("\n" + 70 * "*" + "\n")
    else:
        status = send_and_recieve(channel, command, wait_string, timeout)
    return status

def T1_Layer_1_xran(chan1):
    if command_to_testmac(chan1, "T1", "sudo su -", "vvdn:", False, 10) != 0:
        return 1
    if command_to_testmac(chan1, "T1", "vvdn", "#", False, 10) != 0:
        return 1
    print("Logged in as root user in Terminal 1")    
    if command_to_testmac(chan1, "T1", "/home/vvdn/vf.sh", "(intelpython-python3.9) root@vvdn:~#", True, 13) != 0:
        return 1
    if command_to_testmac(chan1, "T1", "cd /home/vvdn/Source/FlexRAN_v22.07_release_pacakge/", "(intelpython-python3.9) root@vvdn:/home/vvdn/Source/FlexRAN_v22.07_release_pacakge#", False, 5) != 0:
        return 1
    if command_to_testmac(chan1, "T1", "source set_env_var.sh -d", "root@vvdn:/home/vvdn/Source/FlexRAN_v22.07_release_pacakge#", True, 15) != 0:
        return 1
    if command_to_testmac(chan1, "T1", "cd bin/nr5g/gnb/l1/", "root@vvdn:/home/vvdn/Source/FlexRAN_v22.07_release_pacakge/bin/nr5g/gnb/l1#", False, 5) != 0:
        return 1
    if command_to_testmac(chan1, "T1", "./l1.sh -xran", "PHY>welcome to application console", True, 40) != 0:
        return 1
    if command_to_testmac(chan1, "T1", "\n", "PHY>", False, 5) != 0:
        return 1
    return 0

def T2_Layer_2_Testmac(chan2):
    if command_to_testmac(chan2, "T2", "sudo su -", "vvdn:", False, 10) != 0:
        return 1
    if command_to_testmac(chan2, "T2", "vvdn", "#", False, 10) != 0:
        return 1
    print("Logged in as root user in Terminal 2")    
    if command_to_testmac(chan2, "T2", "cd /home/vvdn/Source/FlexRAN_v22.07_release_pacakge/", "(intelpython-python3.9) root@vvdn:/home/vvdn/Source/FlexRAN_v22.07_release_pacakge#", False, 5) != 0:
        return 1
    if command_to_testmac(chan2, "T2", "source set_env_var.sh -d", "root@vvdn:/home/vvdn/Source/FlexRAN_v22.07_release_pacakge#", True, 15) != 0:
        return 1
    if command_to_testmac(chan2, "T2", "cd bin/nr5g/gnb/testmac/", "root@vvdn:/home/vvdn/Source/FlexRAN_v22.07_release_pacakge/bin/nr5g/gnb/testmac#", False, 5) != 0:
        return 1
    if command_to_testmac(chan2, "T2", "./l2.sh", "TESTMAC>welcome to application console", True, 60) != 0:
        return 1
    if command_to_testmac(chan2, "T2", "\n", "TESTMAC>", False, 3) != 0:
        return 1
    return 0

def channel1_listener(channel1):
    global STOP_FLAG
    print("\n" + 30 * "*" + "Layer_1" + 30 * "*" + "\n") 
    with open("/home/sebu.mathew/QA_Testing/channel1_log.txt", "a") as file:
        while not STOP_FLAG:
            if channel1.recv_ready():
                output1 = channel1.recv(1024).decode("utf-8")
                file.write(output1)
            else:
                time.sleep(0.05)

def channel2_listener(channel2):
    global STOP_FLAG
    print("\n" + 30 * "*" + "Testmac" + 30 * "*" + "\n")
    with open("/home/sebu.mathew/QA_Testing/channel2_log.txt", "a") as file:
        while not STOP_FLAG:
            if channel2.recv_ready():
                output2 = channel2.recv(1024).decode("utf-8")
                file.write(output2)
            else:
                time.sleep(0.05)

def close_and_exit_from_test_mac(chan1,chan2,ssh1,ssh2):
    chan1.close()
    chan2.close()
    ssh1.close()
    ssh2.close()
   

if __name__ == "__main__":
    test_mac_ip = configur.get('INFO','test_mac_ip')
    test_mac_username = configur.get('INFO','test_mac_username')
    test_mac_password = configur.get('INFO','test_mac_password')
    ru_ip = configur.get('INFO','ru_ip')
    ru_username = configur.get('INFO','ru_username')
    ru_password = configur.get('INFO','ru_password')

    STOP_FLAG = False
    print("Connecting to the Test-Mac server via T1")
    ssh1 = paramiko.SSHClient()
    ssh1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh1.connect("172.25.96.58", username="vvdn", password="vvdn")
    chan1 = ssh1.invoke_shell()
    time.sleep(2)
    if T1_Layer_1_xran(chan1) != 0:
        print("Command to Layer_1 Application failed,,, Aborting")
        chan1.close()
        ssh1.close()
        sys.exit(1000)

    print("Connecting to the Test-Mac server via T2")
    ssh2 = paramiko.SSHClient()
    ssh2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh2.connect("172.25.96.58", username="vvdn", password="vvdn")
    chan2 = ssh2.invoke_shell()
    time.sleep(2)
    if T2_Layer_2_Testmac(chan2) != 0:
        print("Command to Testmac Application failed,,, Aborting")
        close_and_exit_from_test_mac(chan1,chan2,ssh1,ssh2)
        sys.exit(2000)

    # check_RU_Sync_Status()
    print('='*100)
    print("checking_RU_Stats")
    print('='*100)
    time.sleep(2)
    RU_sync_status = check_RU_sync(ru_ip,ru_username,ru_password)
    if RU_sync_status!= True:
        ### Ru is not syncronized....
        print('='*100)
        print('Ru is not syncronized....')
        print('='*100)
        pass
    time.sleep(5)

    if command_to_testmac(chan2, "T2", "phystart 4 0 0", "TESTMAC>", False, 5) != 0:
        sys.exit
    #command_to_testmac(chan2, "T2", "runnr 0 0 10 1007", "Sebu", False, 1)
    send_to_testmac(chan2, "runnr 0 1 100 11111")

    t1 = threading.Thread(target=channel1_listener, args=(chan1,))
    t2 = threading.Thread(target=channel2_listener, args=(chan2,))
    t1.start()
    t2.start()

    # check_RU_for_Ontime_Stats()
    time.sleep(13)
    print('='*100)
    print("checking_RU_Stats_for_ontime_count")
    print('='*100)
    for _ in range(3):
        ru_stat_status = verify_ru_stat(ru_ip, ru_username, ru_password)
        if ru_stat_status != True:
            ### Ru Packets are not on time....
            print('='*100)
            print('Ru Packets are not on time....')
            print('='*100)
            pass
        else:
            print('='*100)
            print('Ru Packets are on time....')
            print('='*100)

    time.sleep(3)
    print('='*100)
    print("checking_VXT_for Pass_Or_Fail")
    print('='*100)
    if not VXT_control("TM_1_1_LPRU.state", "CU_TC1.png"):
        print('='*100)
        print("Passed")
        print('='*100)
    else:
        print('='*100)
        print("Failed")
        print('='*100)

    print("Stoping")
    time.sleep(5)
    
    STOP_FLAG = True
    t1.join()
    t2.join()

    command_to_testmac(chan2, "T2", "\n\n", "TESTMAC>", False, 5)
    command_to_testmac(chan2, "T2", "exit", "root@vvdn:/home/vvdn/Source/FlexRAN_v22.07_release_pacakge/bin/nr5g/gnb/testmac#", False, 5)
    command_to_testmac(chan1, "T1", "\n\n", "PHY>", False, 5)
    command_to_testmac(chan1, "T1", "exit", "root@vvdn:/home/vvdn/Source/FlexRAN_v22.07_release_pacakge/bin/nr5g/gnb/l1#", False, 5)

    print("Exiting")
    close_and_exit_from_test_mac(chan1,chan2,ssh1,ssh2)
    sys.exit(0)
