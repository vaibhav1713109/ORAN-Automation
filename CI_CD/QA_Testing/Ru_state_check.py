import paramiko, time


def check_sync():
	pass

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



host,ru_user,ru_pswed = '','',''