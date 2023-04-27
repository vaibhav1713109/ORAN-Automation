import time, os
import paramiko,xmltodict,xml.dom.minidom
from ncclient import manager
from configparser import ConfigParser

root_dir = os.path.dirname(os.path.abspath(__file__))
print(root_dir)
configur = ConfigParser()
configur.read('{}/inputs.ini'.format(root_dir))


def check_RU_sync(host,username,password):
    try:
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
    
    except Exception as e:
	    print(f'Check_RU_sync Error : {e}')

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
			else:
				print(line)

		'=========================Receive counter DL C Plane============================================='
		dl_Cplane_counter = ru_stat[4]
		print('=========================Receive counter DL C Plane=============================================')
		for line in dl_Cplane_counter.split('\n'):
			if 'LAYER' in line:
				print(line)
			elif 'TOTAL_RX Packets' in line:
				print(line)
				dl_c_plane_TOTAL_RX_packets = int(line.rsplit(" ",1)[1])
				# print(f'TOTAL_RX_packets : {dl_c_plane_TOTAL_RX_packets}') 
				if dl_c_plane_TOTAL_RX_packets > dl_c_plane_TOTAL_RX_packets_max:
					dl_c_plane_TOTAL_RX_packets_max = dl_c_plane_TOTAL_RX_packets
			elif 'RX_ON-TIME' in line:
				print(line)
				dl_c_plane_RX_ON_TIME_packets = int(line.rsplit(" ",1)[1])
				# print(f'RX_ON-TIME_packets : {dl_c_plane_RX_ON_TIME_packets}') 
				if dl_c_plane_RX_ON_TIME_packets > dl_c_plane_RX_ON_TIME_packets_max:
					dl_c_plane_RX_ON_TIME_packets_max = dl_c_plane_RX_ON_TIME_packets
			else:
				print(line)
				
		'=========================Receive counter UL C Plane============================================='
		ul_Cplane_counter = ru_stat[5]
		print('=========================Receive counter UL C Plane=============================================')
		for line in ul_Cplane_counter.split('\n'):
			if 'LAYER' in line:
				print(line)
			elif 'TOTAL_RX Packets' in line:
				print(line)
				ul_cplane_TOTAL_RX_packets = int(line.rsplit(" ",1)[1])
				# print(f'TOTAL_RX_packets : {ul_cplane_TOTAL_RX_packets}') 
				if ul_cplane_TOTAL_RX_packets > ul_cplane_TOTAL_RX_packets_max:
					ul_cplane_TOTAL_RX_packets_max = ul_cplane_TOTAL_RX_packets
			elif 'RX_ON-TIME' in line:
				print(line)
				ul_cplane_RX_ON_TIME_packets = int(line.rsplit(" ",1)[1])
				# print(f'RX_ON-TIME_packets : {ul_cplane_RX_ON_TIME_packets}')
				if ul_cplane_RX_ON_TIME_packets > ul_cplane_RX_ON_TIME_packets_max:
					ul_cplane_RX_ON_TIME_packets_max = ul_cplane_RX_ON_TIME_packets
			else:
				print(line)

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
			return False
		else:
			print('DL C Plane packets are on time..')
		return True
	else:
		print(ru_state)
		return False



if __name__ == "__main__":
	ru_ip = configur.get('INFO','ru_ip')
	ru_username = configur.get('INFO','ru_username')
	ru_password = configur.get('INFO','ru_password')
	RU_sync_status = check_RU_sync(ru_ip,ru_username,ru_password)
	if RU_sync_status != True:
		print('Ru is not syncronized....')
	print('='*100)
	print("checking_RU_Stats_for_ontime_count")
	print('='*100)
	ru_stat_status = verify_ru_stat(ru_ip, ru_user=ru_username, ru_pswed=ru_password)
	# print(ru_stat_status)
	if ru_stat_status != True:
		print('='*100)
		print('Ru Packets are not on time....')
		print('='*100)
	    