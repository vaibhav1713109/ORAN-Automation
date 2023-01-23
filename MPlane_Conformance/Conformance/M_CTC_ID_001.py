###############################################################################
##@ FILE NAME:      M_CTC_ID_001
##@ TEST SCOPE:     M PLANE O-RAN CONFORMANCE \n
##@ Version:        V_1.0.0
##@ Support:        @Ramiyer, @VaibhavDhiman, @PriyaSharma
###############################################################################

###############################################################################
## Package Imports 
###############################################################################
import ifcfg, sys, os, time, subprocess
from ncclient import manager
from ncclient.operations.rpc import RPCError
from paramiko.ssh_exception import NoValidConnectionsError
from ncclient.operations.errors import TimeoutExpiredError
# from ncclient.transport.errors import sessionCloseError
from tabulate import tabulate
from scapy.all import *
from configparser import ConfigParser
from binascii import hexlify



###############################################################################
## Directory Path
###############################################################################
dir_name = os.path.dirname(os.path.abspath(__file__))
parent = os.path.dirname(dir_name)
# print(parent)
#print(dir_name)
sys.path.append(parent)

###############################################################################
## For reading data from .ini file
###############################################################################
configur = ConfigParser()
configur.read('{}/inputs.ini'.format(dir_name))

###############################################################################
## Related Imports
###############################################################################
from Conformance.Notification import *
from require import STARTUP, Config
from require.ISC_DHCP_SERVER import *
from require.DHCP_CONF_VLAN import *
from require.Vlan_Creation import *


###############################################################################
## Initiate PDF
###############################################################################
pdf = STARTUP.PDF_CAP()

class M_CTC_id_001(test_DHCP_CONF):

    def __init__(self):
        super().__init__()
        self.interface = ''
        self.status, self.ip_address = '',''
        self.session = ''
        self.dhcpp_st = ''
        self.ping = ''
        self.USER_N = ''
        self.PSWRD = ''
        self.DU_vlan = ''
    


    #######################################################################
    ## Check The vlan tag is persent in DHCP Discover message
    #######################################################################
    def ethtool_linked(self,interface):
                    # STARTUP.STORE_DATA(interface,OUTPUT_LIST=OUTPUT_LIST)
        cmd = "sudo ethtool " + interface
        # STARTUP.STORE_DATA(cmd,OUTPUT_LIST=OUTPUT_LIST)
        gp = os.popen(cmd)
        fat=gp.read().split('\n')
        for line in fat:
            # STARTUP.STORE_DATA(line,OUTPUT_LIST=OUTPUT_LIST)
            if "Speed" in line and ('25000' in line or '10000' in line):
                return interface


    #######################################################################
    ## Check SFP Link is detected
    #######################################################################
    def linked_detected(self):
        t = time.time() + 100
        while time.time() < t:
            Interfaces = list(ifcfg.interfaces().keys())
            for interface in Interfaces:
                if '.' not in interface:
                    if self.ethtool_linked(interface):
                        self.interface = self.ethtool_linked(interface)
                        if self.interface !=None:
                            print('\n ********** SFP Link is detected!!! ********** \n')
                            return True
        else:
            print('\n ********** SFP is not Connected!!! ********** \n')
            return False
    #######################################################################
    ## Check DHCP ACK
    #######################################################################
    def check_dhcp_ack(self,pkt):
        summary = pkt.summary()
        try:
            if 'DHCP' in summary:
                # pkt.show()
                if pkt.vlan == self.DU_vlan and pkt['DHCP'].options[0][1] == 5:
                    print('Got ip to the VLAN...')
                    print('VLAN IP is : {}'.format(pkt['IP'].dst))
                    self.ip_address = pkt['IP'].dst
                    print(self.ip_address)
                    # time.sleep(5)
                    # return True
        except Exception as e:
            # print(e)
            return False

    #######################################################################
    ## Sniffing(reading) live packets
    #######################################################################
    def read_live_packets(self,iface = 'wlp0s20f3'):
        pkts = sniff(iface = iface, stop_filter = self.check_vlan_tag, timeout = 100)
        for pkt in pkts:
            val = self.check_vlan_tag(pkt)
            if val:
                break
        else:
            return False
        wrpcap('{}/vlan_tag.pcap'.format(parent), pkts)
        self.create_vlan()
        pkts2 = sniff(iface = iface, stop_filter = self.check_dhcp_ack,timeout = 150)
        for pkt in pkts2:
            val = self.check_dhcp_ack(pkt)
            if val != False:
                break
        else:
            print('No DHCP ack message..')
            return False
        wrpcap('{}/dhcp.pcap'.format(parent), pkts2)
        time.sleep(2)
        os.system('mergecap -w {0}/LOGS/{1}/M_CTC_ID_001.pcap {0}/vlan_tag.pcap {0}/dhcp.pcap'.format(parent,configur.get('INFO','ru_name_rev')))
        os.system('rm {0}/vlan_tag.pcap {0}/dhcp.pcap'.format(dir_name))
        # wrpcap('{}\M_CTC_ID_001.pcap'.format(parent),pkts)
        return True
        # print(pkts)

    #######################################################################
    ## Check The vlan tag is persent in DHCP Discover message
    #######################################################################
    def check_vlan_tag(self,pkt):
        summary = pkt.summary()
        try:
            if 'DHCP' in summary:
                if pkt.vlan:
                    first_vlan_tag_ru = pkt.vlan
                    print('\nfirst_vlan_tag_of_ru: {}\n'.format(pkt.vlan))
                    self.DU_vlan = pkt.vlan + 5
                    # self.create_vlan(DU_vlan)
                    #######################################################################
                    ## Check Vlan comes from RU and Create Vlan in Test PC
                    #######################################################################
                    return True
        except Exception as e:
            # print(e)
            return False

    ###############################################################################
    ## create Vlan and append it into DHCP server
    ###############################################################################
    def create_vlan(self):
        obj = ISC_DHCP_SERVER.test_DHCP_CONF()
        obj.test_read(self.interface,self.DU_vlan)
        obj1 = DHCP_CONF_VLAN.test_DHCP_CONF()
        IPADDR = obj1.test_read()
        VLAN_NAME = '{}.{}'.format(self.interface,self.DU_vlan)
        d = os.system(f'sudo ip link add link {self.interface} name {self.interface}.{self.DU_vlan} type vlan id {self.DU_vlan}')
        d = os.system(f'sudo ifconfig {self.interface}.{self.DU_vlan} {IPADDR} up')
        d = os.system('sudo /etc/init.d/isc-dhcp-server restart')
        st = subprocess.getoutput('sudo /etc/init.d/isc-dhcp-server status')
        li_of_interfaces = list(ifcfg.interfaces().keys())
        if VLAN_NAME in li_of_interfaces:
            return True
        else:
            return False

    ###############################################################################
    ## Check Ping and DHCP Status
    ###############################################################################
    def ping_status(self):
        self.dhcpp_st = subprocess.getoutput('sudo /etc/init.d/isc-dhcp-server status')
        ## Check3 : Ping of VLAN IP
        check3 = True
        response = os.system("ping -c 5 {}".format(self.ip_address))
        self.ping = subprocess.getoutput('ping -c 5 {}'.format(self.ip_address))
        if response == 0:
            print('DHCP IP is Pinging...')
        else:
            print('DHCP IP not Pinging...')
            check3 = False
        return check3

    ###############################################################################
    ## Performing Call home
    ###############################################################################
    def Call_Home(self):
        notification("Test Case M_CTC_ID_001 is under process...")
        Check1 = self.linked_detected()
        obj1 = ISC_DHCP_SERVER.test_DHCP_CONF()
        obj1.test_read('lo',random.randint(0,1))
        subprocess.getoutput('sudo /etc/init.d/isc-dhcp-server restart')
        Check2 = self.read_live_packets(self.interface)
        Check3 = self.ping_status()
        print(Check1, Check2, Check3)
        if (Check1 and Check2 and Check3) != True:
            return Check1 and Check2 and Check3
        ###############################################################################
        ## Read User Name and password from Config.INI of Config.py
        ###############################################################################
        self.USER_N = configur.get('INFO','sudo_user')
        self.PSWRD = configur.get('INFO','sudo_pass')

        for _ in range(5):
            try:
                STARTUP.delete_system_log(host= self.ip_address)
                time.sleep(2)
                ###############################################################################
                ## Perform call home to get ip_details
                ###############################################################################
                self.session = STARTUP.call_home(host = '0.0.0.0', port=4334, hostkey_verify=False,username = self.USER_N, password = self.PSWRD,timeout = 60,allow_agent = False , look_for_keys = False)
                self.ip_address, self.call_home_port = self.session._session._transport.sock.getpeername()   #['ip_address', 'TCP_Port']
                server_key_obj = self.session._session._transport.get_remote_server_key()
                self.fingerprint = STARTUP.colonify(hexlify(server_key_obj.get_fingerprint()))

                if self.session:
                    RU_Details = STARTUP.demo(session = self.session,host= self.ip_address, port= 830)
                    
                    for key, val in RU_Details[1].items():
                        if val[0] == 'true' and val[1] == 'true':
                            ###############################################################################
                            ## Test Description
                            ###############################################################################
                            Test_Desc = '''This scenario validates that the O-RU properly executes the session establishment procedure \nwith VLANs and a DHCPv4 server. This test is applicable to IPv4 environments.'''
                            CONFIDENTIAL = STARTUP.ADD_CONFIDENTIAL('01',SW_R = val[2]) 
                            STARTUP.STORE_DATA(CONFIDENTIAL,Format='CONF',PDF= pdf)
                            STARTUP.STORE_DATA(Test_Desc,Format='DESC',PDF= pdf)
                            pdf.add_page()


                    STARTUP.DHCP_Status(data=self.dhcpp_st,PDF = pdf)
                    STARTUP.STORE_DATA("\t ########### Pinging ###########",Format=True,PDF = pdf)
                    STARTUP.STORE_DATA(self.ping,Format=False,PDF = pdf)
                    ###############################################################################
                    ## VLAN of Test PC
                    ###############################################################################
                    STARTUP.STORE_DATA("\t Interfaces Present in DU Side",Format=True,PDF= pdf)
                    ip_config = subprocess.getoutput('ifconfig')
                    STARTUP.STORE_DATA(ip_config,Format='XML',PDF= pdf)


                    pdf.add_page()
                    time.sleep(10)
                    ###############################################################################
                    ## Execution of Test Case
                    ###############################################################################

                    ###############################################################################
                    ## Test Procedure 1
                    ###############################################################################
                    Test_Step1 = '\tThe O-RU NETCONF Serve  establishes TCP connection and performs a Call Home procedure towards the NETCONF Client and establishes a SSH.'
                    STARTUP.STORE_DATA('{}'.format(Test_Step1),Format='TEST_STEP',PDF = pdf)
                    LISTEN = f'''> listen --ssh --login {self.USER_N }\nWaiting 60s for an SSH Call Home connection on port 4334...'''
                    STARTUP.STORE_DATA(LISTEN,Format=False,PDF = pdf)
                    str_out = f'''The authenticity of the host '::ffff:{self.ip_address}' cannot be established.
                            ssh-rsa key fingerprint is {self.fingerprint}.
                            Are you sure you want to continue connecting (yes/no)? yes'''.strip()
                    STARTUP.STORE_DATA(str_out,Format=False,PDF = pdf)
                    STARTUP.STORE_DATA(f'''\n{self.USER_N }@::ffff:{self.ip_address} password: \n''',Format=False,PDF = pdf)
                    notification('Netconf Session Established!!')

                    ###############################################################################
                    ## Test Procedure 2
                    ###############################################################################
                    Test_Step2 = "\tTER NETCONF Client and O-RU NETCONF Server exchange capabilities through the NETCONF <hello> messages"
                    STARTUP.STORE_DATA('{}'.format(Test_Step2),Format='TEST_STEP',PDF = pdf)
                    STARTUP.STORE_DATA(f'''> status\nCurrent NETCONF self.session:\nID\t: {self.session.session_id}\nHost\t: :ffff:{self.ip_address}\nPort\t: {self.call_home_port}\nTransport\t: SSH\nCapabilities:''',Format=False,PDF = pdf)
                    for server_capability in self.session.server_capabilities:
                        STARTUP.STORE_DATA(server_capability,Format=False,PDF = pdf)
                    time.sleep(10)

                    ###############################################################################
                    ## Closing the self.session
                    ###############################################################################
                    self.session.close_session()
                    return True

                    
            
            ###############################################################################
            ## Exception
            ###############################################################################
            except socket.timeout as e:
                pass
                
            except RPCError as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                STARTUP.STORE_DATA(
                    f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
                return [e.type, e.tag, e.severity, e.path, e.message, exc_tb.tb_lineno]

            except Exception as e:
                STARTUP.STORE_DATA('{}'.format(e), Format=True,PDF=pdf)
                exc_type, exc_obj, exc_tb = sys.exc_info()
                STARTUP.STORE_DATA(
                    f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
                return e
        return False
            # raise Exception('{}'.format(e)) from None




def test_M_ctc_id_001():
    tc001_obj = M_CTC_id_001()
    Check = tc001_obj.Call_Home()
    if Check == False:
        STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
        STARTUP.STORE_DATA('SFP link not detected/DHCP IP not pinged...',Format=False,PDF= pdf)
        STARTUP.ACT_RES(f"{'Transport and Handshake in IPv4 Environment (positive case)' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(235, 52, 52))
        notification('FAIL_REASON :SFP link not detected/DHCP IP not pinging...')
        notification(f"{'Transport and Handshake in IPv4 Environment (positive case)' : <50}{'=' : ^20}{'FAIL' : ^20}")
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
            STARTUP.ACT_RES(f"{'Transport and Handshake in IPv4 Environment (positive case)' : <50}{'=' : ^20}{'SUCCESS' : ^20}",PDF= pdf,COL=(105, 224, 113))
            notification(f"{'Transport and Handshake in IPv4 Environment (positive case)' : <50}{'=' : ^20}{'PASS' : ^20}")
            return True

        elif type(Check) == list:
            STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
            Error_Info = '''\terror-tag \t: \t{}\n\terror-type \t: \t{}\n\terror-severity \t: \t{}\n\tDescription' \t: \t{}'''.format(*map(str,Check))
            STARTUP.STORE_DATA(Error_Info,Format=False,PDF= pdf)
            STARTUP.ACT_RES(f"{'Transport and Handshake in IPv4 Environment (positive case)' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(235, 52, 52))
            notification("Error Info : {}".format(Error_Info))
            notification(f"{'Transport and Handshake in IPv4 Environment (positive case)' : <50}{'=' : ^20}{'FAIL' : ^20}")
            return False

        else:
            STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
            STARTUP.STORE_DATA('{}'.format(Check),Format=False,PDF= pdf)
            STARTUP.ACT_RES(f"{'Transport and Handshake in IPv4 Environment (positive case)' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(235, 52, 52))
            notification('FAIL_REASON : {}'.format(Check))
            notification(f"{'Transport and Handshake in IPv4 Environment (positive case)' : <50}{'=' : ^20}{'FAIL' : ^20}")
            return False
            
    except Exception as e:
            STARTUP.STORE_DATA('{}'.format(e), Format=True,PDF=pdf)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
            notification('FAIL_REASON : {}'.format(e))
            notification(f"{'Transport and Handshake in IPv4 Environment (positive case)' : <50}{'=' : ^20}{'FAIL' : ^20}")
            return False  

    ###############################################################################
    ## For Capturing the logs
    ###############################################################################
    finally:
        STARTUP.CREATE_LOGS('M_CTC_ID_001',PDF=pdf)
        notification("Successfully completed Test Case M_CTC_ID_001. Logs captured !!")
    

if __name__ == "__main__":
    start_time = time.time()
    test_M_ctc_id_001()
    end_time = time.time()
    print('Execution Time is : {}'.format(int(end_time-start_time)))
    pass

