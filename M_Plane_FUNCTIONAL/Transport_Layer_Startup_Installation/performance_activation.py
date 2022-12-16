###############################################################################
##@ FILE NAME:      performance activation
##@ TEST SCOPE:     M PLANE O-RAN Functional
##@ Version:        V_1.0.0
##@ Support:        @Ramiyer, @VaibhavDhiman, @PriyaSharma
###############################################################################

###############################################################################
## Package Imports 
###############################################################################


from logging import exception
import sys,os
from ncclient import manager, operations
import string
from ncclient.operations.rpc import RPCError
from ncclient.transport.errors import SSHError
import paramiko
from configparser import ConfigParser
import xmltodict, time
from paramiko.ssh_exception import NoValidConnectionsError
from ncclient.operations.errors import TimeoutExpiredError
from ncclient.transport.errors import SessionCloseError

###############################################################################
## Directory Path
###############################################################################
dir_name = os.path.dirname(os.path.abspath(__file__))
parent = os.path.dirname(dir_name)
print(parent)
sys.path.append(parent)

########################################################################
## For reading data from .ini file
########################################################################
configur = ConfigParser()
configur.read('{}/inputs.ini'.format(dir_name))

###############################################################################
## Related Imports
###############################################################################
from require import STARTUP, Config
from require.Vlan_Creation import *

pdf_log = STARTUP.PDF_CAP()

class terminate_alarm(vlan_Creation):

    def __init__(self) -> None:
        super().__init__()
        try:
            Check1 = self.linked_detected()
            if Check1 == False or Check1 == None:
                return Check1

            sniff(iface = self.interface, stop_filter = self.check_tcp_ip, timeout = 100)
            self.port = 830
            
        except Exception as e:  
            STARTUP.STORE_DATA('{}'.format(e), Format = True,PDF=pdf_log)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format = False,PDF=pdf_log)
            return '{}'.format(e)


    def session_login(self):
        host = self.hostname
        port = 22
        username = self.user
        password = self.pswd
        try:
            command = "cat {};".format(configur.get('INFO','syslog_path'))
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(host, port, username, password)

            STARTUP.STORE_DATA('Make a ssh connection',Format=True,PDF=pdf_log)
            ssh_o = '''
                vvdn@vvdn:~$ ssh operator@{0}
                operator@{0}'s password:
                cat {1};'''.format(host,configur.get('INFO','syslog_path'))
            STARTUP.STORE_DATA(ssh_o,Format=False,PDF=pdf_log)

            pdf_log.add_page()
            STARTUP.STORE_DATA('########### SYSTEM LOGS ###########',Format=True,PDF=pdf_log)
            stdin, stdout, stderr = ssh.exec_command(command)
            lines1 = stdout.readlines()
            for i in lines1:
                STARTUP.STORE_DATA(i,Format=False,PDF=pdf_log)
        except Exception as e:
            STARTUP.STORE_DATA('{}'.format(e),Format=False,PDF=pdf_log)


    def test_MAIN(self):
        # give the input configuration in xml file format
        #xml_1 = open('o-ran-hardware.xml').read()
        # give the input in the format hostname, port, username, password
        # xml_data = input("Enter the xml below:\n")
        # oper=input("Enter the operation: \n")
        self.user = configur.get('INFO', 'sudo_user')
        self.pswd = configur.get('INFO', 'sudo_pass')
        try:
            
            session = manager.connect(host = self.hostname, port=830, hostkey_verify=False,username = self.user, password = self.pswd ,allow_agent = False , look_for_keys = False)
            
                
            slots = STARTUP.demo(session)
            for key, val in slots[1].items():
                    if val[0] == 'true' and val[1] == 'true':
                        ############################### Test Description #############################
                        Test_Desc = '''Test Description : Verify whether the NETCONF client checks the performance management in O-RU'''
                        CONFIDENTIAL = STARTUP.ADD_CONFIDENTIAL(filename,SW_R = val[2]) 
                        STARTUP.STORE_DATA(CONFIDENTIAL,Format='CONF',PDF= pdf_log)
                        STARTUP.STORE_DATA(Test_Desc,Format='DESC',PDF= pdf_log)
                        pdf_log.add_page()

            # For Capturing the logs
            self.session_login()
            pdf_log.add_page()
            Exp_Result = 'Expected Result : Verify O-RU performs performance managment check  procedure in the start up'
            STARTUP.STORE_DATA(Exp_Result,Format='DESC',PDF= pdf_log)

            STARTUP.STORE_DATA('\t\t{}'.format('****************** Actual Result ******************'),Format=True,PDF= pdf_log)
            
            STARTUP.ACT_RES(f"{'Performance Measurement Activation' : <50}{'=' : ^20}{'SUCCESS' : ^20}",PDF= pdf_log,COL=(105, 224, 113))

        
        except exception as e:
            STARTUP.STORE_DATA('{}'.format(e), Format=True,PDF=pdf_log)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf_log)
            return e

        ############################### MAKE PDF File ####################################################
        finally:
            STARTUP.CREATE_LOGS('M_FTC_ID_{}'.format(filename),PDF=pdf_log)



if __name__== '__main__':
    filename = sys.argv[1]
    obj = terminate_alarm()
    obj.test_MAIN()
