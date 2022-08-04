import socket
import sys, os, warnings
import time
from ncclient import manager, operations
from ncclient.operations import rpc
from ncclient.operations.rpc import RPCError
import subprocess
from ncclient.transport import errors
from paramiko.ssh_exception import NoValidConnectionsError
from ncclient.operations.errors import TimeoutExpiredError
from ncclient.transport.errors import SessionCloseError
import subprocess
import STARTUP, Config
import re

pdf = STARTUP.PDF_CAP()

class M_CTC_id_001():

    def __init__(self,host, port, user, pswrd):
        self.host = host
        self.port = port
        self.user = user
        self.pswrd = pswrd
        self.usr1 = ''
        self.pswrd1 = ''


    # Check DHCP status----
    

    # Call Home initialization----
    def Call_Home(self,user,pswrd):
        
        try:
            m1 = manager.call_home(host='', port=4334, username=user, password=pswrd, timeout = 10,allow_agent = False , look_for_keys = False)
            # li = m1._session._transport.sock.getpeername()   #['ip_address', 'TCP_Port']
            
        
            
        except:
            LISTEN = f'''> listen --ssh --login {user}\nWaiting 60s for an SSH Call Home connection on port 4334...'''
            STARTUP.STORE_DATA(LISTEN,Format=False,PDF = pdf)

            SSH_AUTH = f'''The authenticity of the host '::ffff:{self.host}' cannot be established.
ssh-rsa key fingerprint is 59:9e:90:48:f1:d7:6e:35:e8:d1:f6:1e:90:aa:a3:83:a0:6b:98:5a.
Are you sure you want to continue connecting (yes/no)? no
nc ERROR: Checking the host key failed.
cmd_listen: Receiving SSH Call Home on port 4334 as user "{user}" failed.'''
            STARTUP.STORE_DATA(SSH_AUTH,Format=False,PDF = pdf)
            STARTUP.STORE_DATA('{}\n'.format('-'*100),Format=False,PDF=pdf)



########################### Main Function ############################
def test_MAIN_FUNC_002():
    
    
    
    try:
        USER_N = Config.details['SUDO_USER']
        PSWRD = Config.details['SUDO_PASS']

        ############################### Perform Call Home to get IP #######################################
        m = manager.call_home(host = '', port=4334, hostkey_verify=False,username = USER_N, password = PSWRD,timeout = 60,allow_agent = False , look_for_keys = False)
        li = m._session._transport.sock.getpeername()   #['ip_address', 'TCP_Port']
        sid = m.session_id
        
        if m:
            
            obj = M_CTC_id_001(li[0],830,USER_N,PSWRD)
            STARTUP.kill_ssn(li[0], 830, USER_N, PSWRD,sid)
            RU_Details = STARTUP.demo(li[0], 830, 'operator', 'admin123')
            
            for key, val in RU_Details[1].items():
                    if val[0] == 'true' and val[1] == 'true':
                        ############################### Test Description #############################
                        Test_Desc = '''This scenario validates that the O-RU properly executes the session establishment procedure with VLANs and a DHCPv4 server. This test is applicable to IPv4 environments. Two negative flows are included in this test:
        The TER NETCONF Client does not trigger a SSH session establishment in reaction to Call Home initiated by THE O-RU NETCONF Server.'''
                        CONFIDENTIAL = STARTUP.ADD_CONFIDENTIAL('02',SW_R = val[2]) 
                        STARTUP.STORE_DATA(CONFIDENTIAL,Format='CONF',PDF= pdf)
                        STARTUP.STORE_DATA(Test_Desc,Format='DESC',PDF= pdf)
                        pdf.add_page()

            
            ############################### DU Side Interfaces #############################
            STARTUP.STORE_DATA("\t Interfaces Present in DU Side",Format=True,PDF = pdf)
            ip_config = subprocess.getoutput('ifconfig')
            STARTUP.STORE_DATA(ip_config,Format='XML',PDF = pdf)

            pdf.add_page()
            ############################### DHCP Status #############################
            STARTUP.STORE_DATA("\t DHCP Status",Format=True,PDF = pdf)
            st = subprocess.getoutput('sudo /etc/init.d/isc-dhcp-server status')
            STARTUP.DHCP_Status(data=st,PDF = pdf)


            ################# Pinging vlan ip and perform call home #################
            STARTUP.STORE_DATA("\t ########### Pinging ###########",Format=True,PDF = pdf)
            st = subprocess.getoutput(f'ping {li[0]} -c 5')
            STARTUP.STORE_DATA(st,Format=False,PDF = pdf)



            pdf.add_page()
            hs = {'observer':'admin123','stli':'4647dn','installer':'wireless123','installer':'admin','operator':'admin123'}
            Test_Step1 = '\tThe O-RU NETCONF Serve  establishes TCP connection and performs a Call Home procedure towards the NETCONF Client and not establishes a SSH.'
            STARTUP.STORE_DATA('{}'.format(Test_Step1),Format='TEST_STEP',PDF = pdf)


            for key, val in hs.items():
                res = obj.Call_Home(key,val)          
                time.sleep(80)


            # For Capturing the logs
            ############################### Expected/Actual Result ####################################################
            STARTUP.GET_SYSTEM_LOGS(li[0],USER_N,PSWRD,pdf)
            Exp_Result = 'Expected Result : The O-RU NETCONF Server falls into Call Home procedure loop.'
            STARTUP.STORE_DATA(Exp_Result,Format='DESC',PDF= pdf)

            STARTUP.STORE_DATA('\t\t{}'.format('****************** Actual Result ******************'),Format=True,PDF= pdf)
            
            if type(res) == list:
                STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
                Error_Info = '''\terror-tag \t: \t{}\n\terror-type \t: \t{}\n\terror-severity \t: \t{}\n\tDescription' \t: \t{}'''.format(*map(str,res))
                STARTUP.STORE_DATA(Error_Info,Format=False,PDF= pdf)
                STARTUP.ACT_RES(f"{'NETCONF Client does not initiate the SSH session' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(255,0,0))
                return Error_Info
                # raise '\t\tFAIL-REASON\t\n{}'.format(Error_Info)
                
            else:
                STARTUP.ACT_RES(f"{'NETCONF Client does not initiate the SSH session' : <50}{'=' : ^20}{'SUCCESS' : ^20}",PDF= pdf,COL=(0,255,0))
                return True
                


    ############################### Known Exceptions ####################################################
    except socket.timeout as e:
        Error = '{} : Call Home is not initiated, SSH Socket connection lost....'.format(
            e)
        STARTUP.STORE_DATA(Error, Format=True,PDF=pdf)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(
            f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
        return Error
        # raise socket.timeout('{}: SSH Socket connection lost....'.format(e)) from None

    except errors.SSHError as e:
        Error = '{} : SSH Socket connection lost....'.format(e)
        STARTUP.STORE_DATA(Error, Format=True,PDF=pdf)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(
            f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
        return Error
        # raise errors.SSHError('{}: SSH Socket connection lost....'.format(e)) from None

    except errors.AuthenticationError as e:
        Error = "{} : Invalid username/password........".format(e)
        STARTUP.STORE_DATA(Error, Format=True,PDF=pdf)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(
            f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
        return Error
        # raise f'{e} : Invalid username/password........'

    except NoValidConnectionsError as e:
        Error = '{} : ...'.format(e)
        STARTUP.STORE_DATA(Error, Format=True,PDF=pdf)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(
            f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
        return Error
        # raise e

    except TimeoutError as e:
        Error = '{} : Call Home is not initiated, Timout Expired....'.format(e)
        STARTUP.STORE_DATA(Error, Format=True,PDF=pdf)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(
            f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
        return Error
        # raise f'{e} : Call Home is not initiated, Timout Expired....'

    except SessionCloseError as e:
        Error = "{} : Unexpected_Session_Closed....".format(e)
        STARTUP.STORE_DATA(Error, Format=True,PDF=pdf)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(
            f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
        return Error
        # raise f'{e},Unexpected_Session_Closed....'

    except TimeoutExpiredError as e:
        Error = "{} : TimeoutExpiredError....".format(e)
        STARTUP.STORE_DATA(Error, Format=True,PDF=pdf)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(
            f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
        return Error
        # raise e

    except OSError as e:
        Error = '{} : Call Home is not initiated, Please wait for sometime........'.format(
            e)
        STARTUP.STORE_DATA(Error, Format=True,PDF=pdf)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(
            f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
        return Error
        # raise Exception('{} : Please wait for sometime........'.format(e)) from None

    except Exception as e:
        STARTUP.STORE_DATA('{}'.format(e), Format=True,PDF=pdf)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(
            f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
        return e
        # raise Exception('{}'.format(e)) from None


    ############################### MAKE PDF File ####################################################
    finally:
        STARTUP.CREATE_LOGS('M_CTC_ID_002',PDF=pdf)

if __name__ == '__main__':
    result = test_MAIN_FUNC_002()
    if result == True:
        pass
    else:
        STARTUP.ACT_RES(f"{'NETCONF Client does not initiate the SSH session' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(255,0,0))

        
        
