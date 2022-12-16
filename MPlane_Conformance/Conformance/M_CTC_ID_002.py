###############################################################################
##@ FILE NAME:      M_CTC_ID_002
##@ TEST SCOPE:     M PLANE O-RAN CONFORMANCE \n
##@ Version:        V_1.0.0
##@ Support:        @Ramiyer, @VaibhavDhiman, @PriyaSharma
###############################################################################

###############################################################################
## Package Imports 
###############################################################################
import ifcfg, sys, os, time, subprocess, socket, xmltodict
from ncclient import manager
from ncclient.operations.rpc import RPCError
from paramiko.ssh_exception import NoValidConnectionsError
from ncclient.operations.errors import TimeoutExpiredError
from  ncclient.transport.errors import TransportError, SSHUnknownHostError
from tabulate import tabulate
from scapy.all import *
from configparser import ConfigParser


###############################################################################
## Directory Path
###############################################################################
dir_name = os.path.dirname(os.path.abspath(__file__))
parent = os.path.dirname(dir_name)
# print(parent)
sys.path.append(parent)

########################################################################
## For reading data from .ini file
########################################################################
configur = ConfigParser()
configur.read('{}/inputs.ini'.format(dir_name))

###############################################################################
## Related Imports
###############################################################################
from Conformance.Notification import *
from require import STARTUP
from Conformance.M_CTC_ID_001 import *

###############################################################################
## Initiate PDF
###############################################################################
pdf = STARTUP.PDF_CAP()

class M_CTC_id_002(M_CTC_id_001):

    def __init__(self):
        super().__init__()


    # Check DHCP status----
    def check_vlan_tag(self,pkt):
        summary = pkt.summary()
        try:
            if 'TCP' in summary:
                # pkt.show()
                if  pkt['TCP'].flags == 'RA' or pkt['TCP'].sport == 4334 or pkt['TCP'].sport == 830:
                    print('Got ip to the VLAN...')
                    print('VLAN IP is : {}'.format(pkt['IP'].dst))
                    self.ip_address = pkt['IP'].dst
                    print(self.ip_address)
                    time.sleep(5)
                    return True
        except Exception as e:
            # print(e)
            return False
        pass

    def software_detail(self):
        
        new_session = manager.connect(host = self.ip_address, port=830, hostkey_verify=False,username = self.USER_N, password = self.PSWRD,timeout = 60,allow_agent = False , look_for_keys = False)
        server_key_obj = new_session._session._transport.get_remote_server_key()
        self.fingerprint = STARTUP.colonify(hexlify(server_key_obj.get_fingerprint()))
        sw_inv = '''<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            <software-inventory xmlns="urn:o-ran:software-management:1.0">
            </software-inventory>
            </filter>'''
        s = {}
        slot_names = new_session.get(sw_inv).data_xml
        dict_slot = xmltodict.parse(str(slot_names))
        try:
            slots = dict_slot['data']['software-inventory']['software-slot']
            for k in slots:
                active_s = k['active']
                running_s = k['running']
                slot_name = k['name']
                sw_build = k['build-version']
                slot_status = k['status']
                s[slot_name] = [active_s,running_s,sw_build,slot_status]

        except:
            print("User doesn't have SUDO permission")


        
        print(s)
        return s



    ###############################################################################
    ## Performing Call home
    ###############################################################################
    def Call_Home(self,user,pswrd):
        try:
            self.session = STARTUP.call_home(host='', port=4334, username=user, password=pswrd, timeout = 10,allow_agent = False , look_for_keys = False)
            print(self.session.session_id)
            self.session.close_session()
            return False
            
        
            
        except SSHUnknownHostError as e:
            LISTEN = f'''> listen --ssh --login {self.USER_N}\nWaiting 60s for an SSH Call Home connection on port 4334...'''
            STARTUP.STORE_DATA(LISTEN,Format=False,PDF = pdf)

            SSH_AUTH = f'''The authenticity of the host '::ffff:{self.ip_address}' cannot be established.
            ssh-rsa key fingerprint is {self.fingerprint}.
            Are you sure you want to continue connecting (yes/no)? no
            nc ERROR: Checking the host key failed.
            cmd_listen: Receiving SSH Call Home on port 4334 as user "{self.USER_N}" failed.'''
            STARTUP.STORE_DATA(SSH_AUTH,Format=False,PDF = pdf)
            STARTUP.STORE_DATA('{}\n'.format('-'*100),Format=False,PDF=pdf)
            return True
        
        except Exception as e:
            print(e)
            self.session.close_session()


    ###############################################################################
    ## Main Function
    ###############################################################################
    def test_call_home(self):
        
        notification("Test Case M_CTC_ID_002 is Started !!! ")
        Check1 = self.linked_detected()
        pkt = sniff(iface = self.interface, stop_filter = self.check_vlan_tag, timeout = 100)
        Check3 = self.ping_status()
        if Check1 and Check3 != True:
            return Check1 and Check3

        
        self.USER_N = configur.get('INFO','sudo_user')
        self.PSWRD = configur.get('INFO','sudo_pass')
        try:
            
            RU_Details = self.software_detail()
            STARTUP.delete_system_log(host= self.ip_address)
            time.sleep(2)
                
            for key, val in RU_Details.items():
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
            st = subprocess.getoutput(f'ping -c 5 {self.ip_address}')
            STARTUP.STORE_DATA(st,Format=False,PDF = pdf)



            pdf.add_page()
            users, users1= {'observer':'admin123','operator':'admin123','installer':'wireless123'},{'installer':'wireless123','operator':'admin123'}
            # print(hs)
            Test_Step1 = '\tThe O-RU NETCONF Serve  establishes TCP connection and performs a Call Home procedure towards the NETCONF Client and not establishes a SSH.'
            STARTUP.STORE_DATA('{}'.format(Test_Step1),Format='TEST_STEP',PDF = pdf)

            results = []
            for key, val in users.items():
                res = self.Call_Home(key,val)
                results.append(res)
            for key, val in users1.items():
                res = self.Call_Home(key,val)
                results.append(res)
            for i in results:
                if i == False:
                    return 'Call home initiated..'
            return True

                    


        ###############################################################################
        ## Exception
        ###############################################################################
        except socket.timeout as e:
            Error = '{} : Call Home is not initiated, SSH Socket connection lost....'.format(
                e)
            STARTUP.STORE_DATA(Error, Format=True,PDF=pdf)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
            return Error
            
        except RPCError as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
            # self.session.close_session()
            return [e.type, e.tag, e.severity, e.path, e.message, exc_tb.tb_lineno]

        except Exception as e:
            STARTUP.STORE_DATA('{}'.format(e), Format=True,PDF=pdf)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
            # self.session.close_session()
            return e
        
        # finally:
        #     self.session.close_session()

    
def test_M_ctc_id_002():
    tc001_obj = M_CTC_id_002()
    Check = tc001_obj.test_call_home()
    if Check == False:
        STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
        STARTUP.STORE_DATA('SFP link not detected/DHCP IP not pinging...',Format=False,PDF= pdf)
        STARTUP.ACT_RES(f"{'Transport and Handshake in IPv4 Environment (negative case: refuse SSH Connection)' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(235, 52, 52))
        notification("Test Case is FAIL")
        return False

    ###############################################################################
    ## Expected/Actual Result
    ###############################################################################
    STARTUP.GET_SYSTEM_LOGS(tc001_obj.ip_address,tc001_obj.USER_N,tc001_obj.PSWRD,pdf)
    Exp_Result = 'Expected Result : The TER NETCONF Client and O-RU NETCONF Server exchange capabilities through NETCONF <hello> messages.'
    STARTUP.STORE_DATA(Exp_Result,Format='DESC',PDF= pdf)
    STARTUP.STORE_DATA('\t\t{}'.format('****************** Actual Result ******************'),Format=True,PDF= pdf)
    try:
        if Check == True:
            STARTUP.ACT_RES(f"{'Transport and Handshake in IPv4 Environment (negative case: refuse SSH Connection)' : <50}{'=' : ^20}{'SUCCESS' : ^20}",PDF= pdf,COL=(105, 224, 113))
            notification("Test Case is PASS")
            return True

        elif type(Check) == list:
            STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
            Error_Info = '''\terror-tag \t: \t{}\n\terror-type \t: \t{}\n\terror-severity \t: \t{}\n\tDescription' \t: \t{}'''.format(*map(str,Check))
            STARTUP.STORE_DATA(Error_Info,Format=False,PDF= pdf)
            STARTUP.ACT_RES(f"{'Transport and Handshake in IPv4 Environment (negative case: refuse SSH Connection)' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(235, 52, 52))
            notification("Error Info : {}".format(Error_Info))
            return False

        else:
            STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
            STARTUP.STORE_DATA('{}'.format(Check),Format=False,PDF= pdf)
            STARTUP.ACT_RES(f"{'Transport and Handshake in IPv4 Environment (negative case: refuse SSH Connection)' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(235, 52, 52))
            notification("Test Case is FAIL")
            return False
            
    except Exception as e:
            STARTUP.STORE_DATA('{}'.format(e), Format=True,PDF=pdf)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
            return False


    ###############################################################################
    ## For Capturing the logs
    ###############################################################################
    finally:
        STARTUP.CREATE_LOGS('M_CTC_ID_002',PDF=pdf)
        notification("Test Case M_CTC_ID_002 is completed and Logs captured")
    
if __name__ == "__main__":
    test_M_ctc_id_002()
    pass
        

