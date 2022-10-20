import os

directory_path = os.path.dirname(os.path.abspath(__file__))
print(directory_path)
file_name = 'giru_revALL_dummy_v4.7.1.zip'
# list_of_RU = ['garuda','mcb1','mcel']

########################################### Store Image here ####################################################
# absolute_path_garuda = os.path.join(directory_path, 'SW_IMAGE/GARUDA')
# absolute_path_mcel = os.path.join(directory_path, 'SW_IMAGE/MCEL')
# absolute_path_msb1 = os.path.join(directory_path, 'SW_IMAGE/MCB1')
# remote_path = 'sftp://vvdn@192.168.4.15:22/{}{}'.format(absolute_path_garuda,file_name)
# print(absolute_path_garuda,'1')

CONF = {
  'SUPER_USER': 'root',
  'SUPER_USER_PASS' : {'garuda' : 'garuda', 'mcb1' : 'root'},
  'SYSLOG_PATH' : {'garuda' : '/media/sd-mmcblk0p4','mcb1' : '/run/media/mmcblk0p4'},
  'syslog_name' : {'garuda' : 'garuda.log','mcb1' : 'mcb1.log'},
  'uplane_xml'  : {'garuda' : 'Yang_xml/GARUDA_UPLANE.xml','mcb1' : 'Yang_xml/MCB1_UPLANE.xml'},
  'TC_27_xml'  : {'garuda' : 'Yang_xml/GARUDA_TC_27.xml','mcb1' : 'Yang_xml/MCB1_TC_27.xml'}
}

details = {
  'SUPER_USER': CONF['SUPER_USER'],
  'SUPER_USER_PASS' : list(CONF['SUPER_USER_PASS'].values())[0],
  'SUDO_USER' : 'operator',
  'SUDO_PASS' : 'admin123',
  'NMS_USER' : 'installer',
  'NMS_PASS' : 'wireless123',
  'FM_PM_USER' : 'observer',
  'FM_PM_PASS' : 'admin123',
  'IPADDR_PARAGON' : '172.17.80.4',
  'PORT' : '1',
  'DU_PASS' : 'vvdntech',
  'DU_MAC' : '64:9d:99:b1:7e:63',
  'remote_path' : 'sftp://vvdn@192.168.4.15:22/home/vvdn/Downloads/garuda_image/garuda/giru_RevAll_5.1.2.zip',
  'Corrupt_File': 'sftp://vvdn@192.168.4.15:22/home/vvdn/Downloads/garuda_image/garuda/Corrupt_5.0.2.zip',
  'SYSLOG_PATH' : list(CONF['SYSLOG_PATH'].values())[0],
  'syslog_name' : list(CONF['syslog_name'].values())[0],
  'uplane_xml'  : list(CONF['uplane_xml'].values())[0],
  'TC_27_xml'  : list(CONF['TC_27_xml'].values())[0]
  }
# print(list(CONF['SUPER_USER_PASS'].values())[0])
import configparser

filename = "{}/input.ini".format(directory_path)

########################################################################
# Writing Data
########################################################################
def WriteDate(dic):
    config = configparser.ConfigParser()
    config.read(filename)

    try:
        config.add_section("INFO")
    except configparser.DuplicateSectionError:
        pass
    for key,val in dic.items():
        config.set("INFO", str(key), str(val))
    with open(filename, "w") as config_file:
        config.write(config_file)
    print('Data append...')


########################################################################
## Check Ping
########################################################################
def PINGING(hostname):
    print("\t ########### Pinging ###########")
    response = os.system("ping -c 5 " + hostname)
    #and then check the response...
    if response == 0:
        return True
    else:
        return False


########################################################################
## Take USER Input
########################################################################
if __name__ == "__main__":
  input_dict = {}
  input_dict['super_user'] = input('Enter the super user of RU: ')
  input_dict['super_user_pswrd'] = input('Enter the super user password of RU: ')
  input_dict['du_pswrd'] = input('Enter the DU password of RU: ')
  while True:
    input_dict['paragon_ip'] = input('Enter the pragon neo IP address: ')
    status = PINGING(input_dict['paragon_ip'])
    if status:
      print('Paragon Ip is not pinging, please check the paragon IP...')
      break
    else:
      print('Paragon Ip is pinging...')
  input_dict['paragon_port'] = input('Enter the pragon neo port for enable PTP&SYNCE {eg. 1/2}: ')
  input_dict['du_mac'] = input('Enter the MAC address of RU: ')
  input_dict['remote_path'] = input('Enter the remote file path of software {eg. sftp://vvdn@192.168.4.15:22/giru_RevAll_5.1.2.zip}: ')
  input_dict['corrupt_file_path'] = input('Enter the remote file path of software {eg. sftp://vvdn@192.168.4.15:22/giru_RevAll_5.1.2.zip}: ')
  input_dict['syslog_path'] = input('Enter the system log path of RU {eg. /media/sd-mmcblk0p4/filename.log}: ')
  input_dict['channel_bandwidth'] = input('Enter the channel bandwidth of RU {eg. 10/20/100}: ')
  input_dict['center_channel_bandwidth'] = float(input('Enter the center of channel bandwidth of RU in GHz {eg. 3.6/2.6}: '))
  input_dict['tx_arfcn'] = int(input('Enter the tx ARFCN {eg. 633333}: '))
  input_dict['rx_arfcn'] = int(input('Enter the rx ARFCN {eg. 633333}: '))

  WriteDate(input_dict)




