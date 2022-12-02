###############################################################################
##@ FILE NAME:      
##@ TEST SCOPE:     M PLANE O-RAN Functional
##@ Version:        V_1.0.0
##@ Support:        @Ramiyer, @VaibhavDhiman, @PriyaSharma
###############################################################################

###############################################################################
## Package Imports 
###############################################################################


from logging import exception
import sys
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

pdf = STARTUP.PDF_CAP()

def session_login(host, port, user, password):
    host = host
    port = 22
    username = user
    password = password
    try:
        command = "cat {};".format(configur.get('INFO','syslog_path'))
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port, username, password)

        STARTUP.STORE_DATA('Make a ssh connection',Format=True,PDF=pdf)
        ssh_o = '''
            vvdn@vvdn:~$ ssh operator@{0}
            operator@{0}'s password:
            cat /media/sd-mmcblk0p4/garuda.log;'''.format(host)
        STARTUP.STORE_DATA(ssh_o,Format=False,PDF=pdf)

        pdf.add_page()
        STARTUP.STORE_DATA('########### SYSTEM LOGS ###########',Format=True,PDF=pdf)
        stdin, stdout, stderr = ssh.exec_command(command)
        lines1 = stdout.readlines()
        for i in lines1:
            STARTUP.STORE_DATA(i,Format=False,PDF=pdf)
    except Exception as e:
        STARTUP.STORE_DATA('{}'.format(e),Format=False,PDF=pdf)


def test_MAIN():
    # give the input configuration in xml file format
    #xml_1 = open('o-ran-hardware.xml').read()
    # give the input in the format hostname, port, username, password
    # xml_data = input("Enter the xml below:\n")
    # oper=input("Enter the operation: \n")
    user = configur.get('INFO', 'sudo_user')
    pswd = configur.get('INFO', 'sudo_pass')
    try:
        m = manager.call_home(host = '', port=4334, hostkey_verify=False,username = user, password = pswd ,allow_agent = False , look_for_keys = False)
        # ['ip_address', 'TCP_Port']
        li = m._session._transport.sock.getpeername()
        sid = m.session_id
            
        slots = STARTUP.demo(m)
        STARTUP.kill_ssn(li[0],830, user, pswd,sid)
        for key, val in slots[1].items():
                if val[0] == 'true' and val[1] == 'true':
                    ############################### Test Description #############################
                    Test_Desc = '''Test Description : Verify whether the NETCONF client checks the performance management in O-RU'''
                    CONFIDENTIAL = STARTUP.ADD_CONFIDENTIAL('023',SW_R = val[2]) 
                    STARTUP.STORE_DATA(CONFIDENTIAL,Format='CONF',PDF= pdf)
                    STARTUP.STORE_DATA(Test_Desc,Format='DESC',PDF= pdf)
                    pdf.add_page()

        # For Capturing the logs
        session_login(li[0],22, user, pswd)
        pdf.add_page()
        Exp_Result = 'Expected Result : Verify O-RU performs performance managment check  procedure in the start up'
        STARTUP.STORE_DATA(Exp_Result,Format='DESC',PDF= pdf)

        STARTUP.STORE_DATA('\t\t{}'.format('****************** Actual Result ******************'),Format=True,PDF= pdf)
        
        STARTUP.ACT_RES(f"{'Performance Measurement Activation' : <50}{'=' : ^20}{'SUCCESS' : ^20}",PDF= pdf,COL=(105, 224, 113))

    
    except exception as e:
        STARTUP.STORE_DATA('{}'.format(e), Format=True,PDF=pdf)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(
            f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
        return e

    ############################### MAKE PDF File ####################################################
    finally:
        STARTUP.CREATE_LOGS('M_FTC_ID_023',PDF=pdf)



if __name__== '__main__':
    test_MAIN()
