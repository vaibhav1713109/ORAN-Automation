import sys,os
import time
import paramiko,xmltodict,xml.dom.minidom
import threading
from configparser import ConfigParser
from VXT_Control import *
from ncclient import manager

root_dir = os.path.dirname(os.path.abspath(__file__))
configur = ConfigParser()
configur.read('{}/inputs.ini'.format(root_dir))


def check_RU_sync(host,username,password):
    with manager.connect(host = host, port=830, hostkey_verify=False,username = username, password = password,timeout = 60,allow_agent = False , look_for_keys = False) as session:
        print("-"*100)
        print(f'Connect to the netopeer session id {session.session_id}')
        print("-"*100)
        print('Checking the sync state of RU')
        print("-"*100)
        sync_filter = '''<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <sync xmlns="urn:o-ran:sync:1.0">
                </sync>
                </filter>
                '''
        xml_pretty_str = ''
        start_time = time.time() + 1200
        while time.time() < start_time:
            get_filter = session.get(sync_filter).data_xml
            dict_data_sync = xmltodict.parse(str(get_filter))
            parsed_data = xml.dom.minidom.parseString(get_filter)
            xml_pretty_str = parsed_data.toprettyxml()
            state = dict_data_sync['data']['sync']['sync-status']['sync-state']
            if state == 'LOCKED':
                print(xml_pretty_str)
                print("-"*100)
                print('RU is Syncronized...'.center(98))
                print("-"*100)
                return True
        else:
            print("-"*100)
            print('RU Taking too much time, It is not syncronized yet...'.center(98))
            print("-"*100)
            return False

def capture_ru_state(host,username,password):
	try:
		port = 22
		command = "cd /etc/scripts/; ./stat_ru.sh"
		client = paramiko.SSHClient()
		client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		client.connect(host, port, username, password)
		stdin, stdout, stderr = client.exec_command(command)
		Error = stderr.read().decode()
		if Error:
			return Error, False
		else:
			ru_state = stdout.read().decode()
		return ru_state, True
	except Exception as e:
		time.sleep(5)
		error = f'Check_ru_state Error : {e}'
		print(error)
		return error, False


def verify_ru_stat(host,ru_user,ru_pswed):
	ru_state, status = capture_ru_state(host,ru_user,ru_pswed)
	if status:
		dl_TOTAL_RX_packets_max = 0
		dl_RX_ON_TIME_packets_max = 0
		dl_c_plane_TOTAL_RX_packets_max = 0
		dl_c_plane_RX_ON_TIME_packets_max = 0
		ul_cplane_TOTAL_RX_packets_max = 0
		ul_cplane_RX_ON_TIME_packets_max = 0
		ru_stat = ru_state.split('=============================================================================================')
		dl_counter = ru_stat[3]

		print('========================= RECIEVE COUNTERS DL =============================================')
		for line in dl_counter.split('\n'):
			if 'LAYER' in line:
				print(line)
			elif 'TOTAL_RX Packets' in line:
				# print(line)
				dl_TOTAL_RX_packets = int(line.rsplit(" ",1)[1])
				if dl_TOTAL_RX_packets > dl_TOTAL_RX_packets_max:
					dl_TOTAL_RX_packets_max = dl_TOTAL_RX_packets
				print(f'TOTAL_RX_packets : {dl_TOTAL_RX_packets}') 
			elif 'RX_ON-TIME' in line:
				# print(line)
				dl_RX_ON_TIME_packets = int(line.rsplit(" ",1)[1])
				if dl_RX_ON_TIME_packets > dl_RX_ON_TIME_packets_max:
					dl_RX_ON_TIME_packets_max = dl_RX_ON_TIME_packets
				print(f'RX_ON-TIME_packets : {dl_RX_ON_TIME_packets}')

		'=========================Receive counter DL C Plane============================================='
		dl_Cplane_counter = ru_stat[4]
		print('=========================Receive counter DL C Plane=============================================')
		for line in dl_Cplane_counter.split('\n'):
			if 'LAYER' in line:
				print(line)
			elif 'TOTAL_RX Packets' in line:
				# print(line)
				dl_c_plane_TOTAL_RX_packets = int(line.rsplit(" ",1)[1])
				print(f'TOTAL_RX_packets : {dl_c_plane_TOTAL_RX_packets}') 
				if dl_c_plane_TOTAL_RX_packets > dl_c_plane_TOTAL_RX_packets_max:
					dl_c_plane_TOTAL_RX_packets_max = dl_c_plane_TOTAL_RX_packets
			elif 'RX_ON-TIME' in line:
				# print(line)
				dl_c_plane_RX_ON_TIME_packets = int(line.rsplit(" ",1)[1])
				print(f'RX_ON-TIME_packets : {dl_c_plane_RX_ON_TIME_packets}') 
				if dl_c_plane_RX_ON_TIME_packets > dl_c_plane_RX_ON_TIME_packets_max:
					dl_c_plane_RX_ON_TIME_packets_max = dl_c_plane_RX_ON_TIME_packets
				
		'=========================Receive counter UL C Plane============================================='
		ul_Cplane_counter = ru_stat[5]
		print('=========================Receive counter UL C Plane=============================================')
		for line in ul_Cplane_counter.split('\n'):
			if 'LAYER' in line:
				print(line)
			elif 'TOTAL_RX Packets' in line:
				# print(line)
				ul_cplane_TOTAL_RX_packets = int(line.rsplit(" ",1)[1])
				print(f'TOTAL_RX_packets : {ul_cplane_TOTAL_RX_packets}') 
				if ul_cplane_TOTAL_RX_packets > ul_cplane_TOTAL_RX_packets_max:
					ul_cplane_TOTAL_RX_packets_max = ul_cplane_TOTAL_RX_packets
			elif 'RX_ON-TIME' in line:
				# print(line)
				ul_cplane_RX_ON_TIME_packets = int(line.rsplit(" ",1)[1])
				print(f'RX_ON-TIME_packets : {ul_cplane_RX_ON_TIME_packets}')
				if ul_cplane_RX_ON_TIME_packets > ul_cplane_RX_ON_TIME_packets_max:
					ul_cplane_RX_ON_TIME_packets_max = ul_cplane_RX_ON_TIME_packets

		'=========================Check Wether on-time packets are more then 95% of total packets================================'
		if dl_RX_ON_TIME_packets_max < (dl_TOTAL_RX_packets_max*95)//100 or ((dl_RX_ON_TIME_packets_max == 0)):
			print(f'dl_RX_ON_TIME_packets {dl_RX_ON_TIME_packets_max} are less then 95% of dl_TOTAL_RX_packets {dl_TOTAL_RX_packets_max}')
		else:
			print('DL Counter packets are on time..')
		if dl_c_plane_RX_ON_TIME_packets_max < (dl_c_plane_TOTAL_RX_packets_max*95)//100 or dl_c_plane_RX_ON_TIME_packets_max == 0:
			print(f'dl_c_plane_RX_ON_TIME_packets {dl_c_plane_RX_ON_TIME_packets_max} are less then 95% of dl_c_plane_TOTAL_RX_packets {dl_c_plane_TOTAL_RX_packets_max}')
		else:
			print('DL C Plane packets are on time..')
		if ul_cplane_RX_ON_TIME_packets_max < (ul_cplane_TOTAL_RX_packets_max*95)//100 or ul_cplane_RX_ON_TIME_packets_max == 0:
			print(f'ul_cplane_RX_ON_TIME_packets {ul_cplane_RX_ON_TIME_packets_max} are less then 95% of ul_cplane_TOTAL_RX_packets {ul_cplane_TOTAL_RX_packets_max}')
		else:
			print('DL C Plane packets are on time..')
			return False
		return True
	else:
		print(ru_state)
		return False



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
    with open("channel1_log.txt", "a") as file:
        while not STOP_FLAG:
            if channel1.recv_ready():
                output1 = channel1.recv(1024).decode("utf-8")
                file.write(output1)
            else:
                time.sleep(0.05)

def channel2_listener(channel2):
    global STOP_FLAG
    print("\n" + 30 * "*" + "Testmac" + 30 * "*" + "\n")
    with open("channel2_log.txt", "a") as file:
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
    ssh1.connect(test_mac_ip, username=test_mac_username, password=test_mac_password)
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
    ssh2.connect(test_mac_ip, username=test_mac_username, password=test_mac_password)
    chan2 = ssh2.invoke_shell()
    time.sleep(2)
    if T2_Layer_2_Testmac(chan2) != 0:
        print("Command to Testmac Application failed,,, Aborting")
        close_and_exit_from_test_mac(chan1,chan2,ssh1,ssh2)
        sys.exit(2000)

    # check_RU_Sync_Status()
    RU_sync_status = check_RU_sync(ru_ip,ru_username,ru_password)
    if RU_sync_status!= True:
        ### Ru is not syncronized....
        pass
    print("checking_RU_Stats")
    time.sleep(5)

    if command_to_testmac(chan2, "T2", "phystart 4 0 0", "TESTMAC>", False, 5) != 0:
        sys.exit
    #command_to_testmac(chan2, "T2", "runnr 0 0 10 1007", "Sebu", False, 1)
    send_to_testmac(chan2, "runnr 0 0 10 1007")

    t1 = threading.Thread(target=channel1_listener, args=(chan1,))
    t2 = threading.Thread(target=channel2_listener, args=(chan2,))
    t1.start()
    t2.start()

    #check RU_state()
    ru_stat_status = verify_ru_stat(ru_ip, username=ru_username, password=ru_password)
    if ru_stat_status != True:
          ### Ru Packets are not on time...
          print('Ru Packets are not on time...')
          pass
    
    obj = vxt_configuration_and_result_capture()
    Check_VXT_Stats = obj.Constellation_check()

    #verify the status of VXT Constellation and channel power
    if Check_VXT_Stats != True:
          ### VXT constellation is not expected....
          pass
    time.sleep(40)
    print("checking_VXT_for Pass_Or_Fail")
    time.sleep(30)
    
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

