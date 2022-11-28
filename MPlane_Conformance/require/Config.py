import os

directory_path = os.path.dirname(__file__)
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




