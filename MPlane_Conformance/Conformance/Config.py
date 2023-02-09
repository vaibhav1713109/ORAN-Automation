###############################################################################
##@ FILE NAME:      Configuration File
##@ TEST SCOPE:     M PLANE O-RAN CONFORMANCE \n
##@ Version:        V_1.0.0
##@ Support:        @Ramiyer, @VaibhavDhiman, @PriyaSharma
###############################################################################

###############################################################################
## Package Imports 
###############################################################################

import os, sys

directory_path = os.path.dirname(os.path.dirname(__file__))
print(directory_path)
sys.path.append(directory_path)

from require.Write_Data import *


def take_input():
    data = {'super_user' : input('Enter root user of RU: '),
    'super_pass' : input('Enter root password of RU: '),
    'syslog_path' : input('Enter System log path of RU {eg. /media/sd-mmcblk0p4/mcb1.log}: '),
    'ru_name_rev' : input('Enter RU Name and rev {eg. MCB1_revA}: '),
    'sudo_user' : input('Enter Sudo user: '),
    'sudo_pass' : input('Enter Sudo password: '),
    'fh_interface' : input('Enter Fronthaul interface of RU {eg. eth0/eth1}: '),
    'bandwidth' : input('Enter Bandwidths: '),
    'tx_arfcn' : input('Enter TX Arfcn: '),
    'rx_arfcn' : input('Enter RX Arfcn: '),
    'tx_center_frequency' : input('Enter TX center frequency {eg. 490000}: '),
    'rx_center_frequency' : input('Enter RX center frequency {eg. 390000}: '),
    'duplex_scheme' : input('Enter Duplex scheme {eg. TDD/FDD}: '),
    'du_pass' : input('Enter DU Password: '),
    'sw_path' : input('Enter SW file path {eg. sftp://{whoami}@{ip_address_sftpserver}:22/path/to/sw/file}: '),
    'currupt_path' : input('Enter SW file path {eg. sftp://{whoami}@{ip_address_sftpserver}:22/path/to/corrupt_sw/file}: '),
    'nms_user' : input('Enter nms user: '),
    'nms_pass' : input('Enter nms password: '),
    'fmpm_user' : input('Enter fmpm user: '),
    'fmpm_pass' : input('Enter fmpm password: '),
    'paragon_ip' : input('Enter Paragon Neo IP address: '),
    'ptpsynceport' : input('Enter Ptp&SyncE port: ')

    }
    WriteData(data, '{}/Conformance/inputs.ini'.format(directory_path))
    try:
        os.mkdir('{}/LOGS/{}'.format(directory_path,data['ru_name_rev']))
    except Exception as e:


if __name__ == '__main__':
    take_input()
    pass




