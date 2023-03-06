###############################################################################
##@ FILE NAME:      Vlan Scan
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
print(parent)
#print(dir_name)
sys.path.append(parent)

###############################################################################
## For reading data from .ini file
###############################################################################
configur = ConfigParser()
configur.read('{}/require/inputs.ini'.format(parent))

###############################################################################
## Related Imports
###############################################################################
from require.Notification import *
from require import STARTUP
from require.ISC_DHCP_SERVER import *
from require.DHCP_CONF_VLAN import *
from require.LINK_DETECTED import *


###############################################################################
## Initiate PDF
###############################################################################
pdf = STARTUP.PDF_CAP()
summary = []

class vlan_scan(test_DHCP_CONF, test_isc_server_conf,Link_Detect):

    def __init__(self):
        test_DHCP_CONF.__init__(self)
        Link_Detect.__init__(self)
        test_isc_server_conf.__init__(self)
        self.status = ''
        self.session = ''
        self.dhcpp_st = ''
        self.ping = ''
        self.USER_N = ''
        self.PSWRD = ''
        self.DU_vlan = ''
    

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
                    return True
        except Exception as e:
            # print(e)
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
                    self.hostname = pkt['IP'].dst
                    print(self.hostname)
                    STARTUP.append_data_and_print(f'Got DHCP IP {self.hostname} to the VLAN {self.DU_vlan} || Successful',summary)
        except Exception as e:
            # print(e)
            return False

    #######################################################################
    ## Sniffing(reading) live packets
    #######################################################################
    def read_live_packets_for_incoming_vlan_tag(self,iface = 'wlp0s20f3'):
        print(f'{"-"*100}\nReading Live packets for incoming vlan tag')
        pkts = sniff(iface = iface, stop_filter = self.check_vlan_tag, timeout = 100)
        for pkt in pkts:
            val = self.check_vlan_tag(pkt)
            if val:
                STARTUP.append_data_and_print('Captured incoming vlan tag || Successful',summary)
                wrpcap('{}/vlan_tag.pcap'.format(dir_name), pkts)
                return True
        else:
            STARTUP.append_data_and_print('Captured incoming vlan tag || Fail',summary)
            return 'Captured incoming vlan tag || Fail'
 
    ###############################################################################
    ## create Vlan and append it into DHCP server
    ###############################################################################
    def dhcp_configuration_and_vlan_creation(self):
        test_isc_server_conf.test_read(self,self.INTERFACE_NAME,self.DU_vlan)
        STARTUP.append_data_and_print('Configured DHCP server || Successful',summary)
        IPADDR = test_DHCP_CONF.test_read(self)
        VLAN_NAME = '{}.{}'.format(self.INTERFACE_NAME,self.DU_vlan)
        d = os.system(f'sudo ip link add link {self.INTERFACE_NAME} name {self.INTERFACE_NAME}.{self.DU_vlan} type vlan id {self.DU_vlan}')
        d = os.system(f'sudo ifconfig {self.INTERFACE_NAME}.{self.DU_vlan} {IPADDR} up')
        li_of_interfaces = list(ifcfg.interfaces().keys())
        if VLAN_NAME in li_of_interfaces:
            STARTUP.append_data_and_print('Vlan creation in test server || Successful',summary)
            d = os.system('sudo /etc/init.d/isc-dhcp-server restart')
            st = subprocess.getoutput('sudo /etc/init.d/isc-dhcp-server status')
            STARTUP.append_data_and_print('Restart DHCP server || Successful',summary)
            return True
        else:
            STARTUP.append_data_and_print('Vlan creation in test server || Fail',summary)
            return 'Vlan creation in test server || Fail'

    def check_ip_in_dhcp_ack_message(self,iface = 'wlp0s20f3'):
        pkts2 = sniff(iface = iface, stop_filter = self.check_dhcp_ack,timeout = 150)
        for pkt in pkts2:
            val = self.check_dhcp_ack(pkt)
            if val != False:
                STARTUP.append_data_and_print(f'Got DHCP IP {self.hostname} to the VLAN {self.DU_vlan} || Successful',summary)
                wrpcap('{}/dhcp.pcap'.format(dir_name), pkts2)
                time.sleep(2)
                os.system('mergecap -w {0}/LOGS/{1}/vlan_scan.pcap {0}/vlan_tag.pcap {0}/dhcp.pcap'.format(dir_name,configur.get('INFO','ru_name_rev')))
                os.system('rm {0}/vlan_tag.pcap {0}/dhcp.pcap'.format(dir_name))
                return True
        else:
            STARTUP.append_data_and_print(f'IP assignment to the VLAN {self.DU_vlan} || Fail',summary)
            return f'IP assignment to the VLAN {self.DU_vlan} || Fail'
       

    ###############################################################################
    ## Performing Call home
    ###############################################################################
    def Call_Home(self):
        print(f'{"-"*100}\nCheck the Link Detection')
        link_status = Link_Detect.link_detected(self)
        cmd = "ethtool " + self.INTERFACE_NAME
        ethtool_out = subprocess.getoutput(cmd)
        Result = STARTUP.basic_check_for_vlan_scan(link_status,pdf,self.INTERFACE_NAME,summary)
        if not Result[-1]:
            return Result[0]

        ###############################################################################
        ## Read User Name and password from Config.INI of Config.py
        ###############################################################################
        self.USER_N = configur.get('INFO','sudo_user')
        self.PSWRD = configur.get('INFO','sudo_pass')
        self.timeout = configur.getint('INFO','wait_time') - 30
        test_isc_server_conf.test_read(self,'lo',random.randint(0,1))
        subprocess.getoutput('sudo /etc/init.d/isc-dhcp-server restart')
        time.sleep(self.timeout)
        summary.clear()

        ###############################################################################
        ## Check the link detection
        ###############################################################################
        print(f'{"-"*100}\nCheck the Link Detection')
        Check1 = Link_Detect.link_detected(self)
        cmd = "ethtool " + self.INTERFACE_NAME
        ethtool_out = subprocess.getoutput(cmd)
        if Check1 == False or Check1 == None:
            STARTUP.STORE_DATA('{}'.format(cmd).center(100),Format=True,PDF=pdf)
            STARTUP.STORE_DATA(ethtool_out,Format=False,PDF=pdf)
            return Check1

        incoming_vlan = self.read_live_packets_for_incoming_vlan_tag(self.INTERFACE_NAME)
        if incoming_vlan != True:
            return incoming_vlan

        dhcp_configuration_status = self.dhcp_configuration_and_vlan_creation()
        if dhcp_configuration_status != True:
            return dhcp_configuration_status
        
        dhcp_ip_check = self.check_ip_in_dhcp_ack_message(self.INTERFACE_NAME)
        if dhcp_ip_check != True:
            return dhcp_ip_check


        timeout = time.time()+60
        print(f'{"-"*100}\nCheck the status of DHCP ip ping\n{"-"*100}')
        while time.time()<timeout:
            Check3 = STARTUP.ping_status(self.hostname)
            if Check3:
                STARTUP.append_data_and_print(f'DHCP IP {self.hostname} Ping || Successful',summary)
                ping_out = subprocess.getoutput("ping -c 5 {}".format(self.hostname))
                break
        else:
            STARTUP.STORE_DATA('{}'.format(cmd).center(100),Format=True,PDF=pdf)
            STARTUP.STORE_DATA(ethtool_out,Format=False,PDF=pdf)
            STARTUP.STORE_DATA('{}'.format("ping -c 5 {}".format(self.hostname)).center(100),Format=True,PDF=pdf)
            ping_out = subprocess.getoutput("ping -c 5 {}".format(self.hostname))
            STARTUP.STORE_DATA(ping_out,Format=False,PDF=pdf)
            return f'DHCP IP {self.hostname} not Pinging'

        

        for _ in range(5):
            try:
                time.sleep(5)
                STARTUP.delete_system_log(host= self.hostname)
                ###############################################################################
                ## Perform call home to get ip_details
                ###############################################################################
                self.session = STARTUP.call_home(host = '0.0.0.0', port=4334, hostkey_verify=False,username = self.USER_N, password = self.PSWRD,timeout = 60,allow_agent = False , look_for_keys = False)
                self.hostname, self.call_home_port = self.session._session._transport.sock.getpeername()   #['ip_address', 'TCP_Port']
                server_key_obj = self.session._session._transport.get_remote_server_key()
                self.fingerprint = STARTUP.colonify(hexlify(server_key_obj.get_fingerprint()))

                if self.session:
                    STARTUP.append_data_and_print('Netopeer Connection || Successful',summary)
                    RU_Details = STARTUP.Software_detail(session = self.session)
                    
                    for key, val in RU_Details.items():
                        if val[0] == 'true' and val[1] == 'true':
                            ###############################################################################
                            ## Test Description
                            ###############################################################################
                            Test_Desc = '''This scenario validates that the O-RU properly executes the session establishment procedure \nwith VLANs and a DHCPv4 server. This test is applicable to IPv4 environments.'''
                            CONFIDENTIAL = STARTUP.ADD_CONFIDENTIAL('Vlan Scan',SW_R = val[2]) 
                            STARTUP.STORE_DATA(CONFIDENTIAL,Format='CONF',PDF= pdf)
                            STARTUP.STORE_DATA(Test_Desc,Format='DESC',PDF= pdf)
                            pdf.add_page()


                    STARTUP.DHCP_Status(data=self.dhcpp_st,PDF = pdf)
                    STARTUP.STORE_DATA('{}'.format(cmd).center(100),Format=True,PDF=pdf)
                    STARTUP.STORE_DATA(ethtool_out,Format=False,PDF=pdf)
                    STARTUP.STORE_DATA('{}'.format("ping -c 5 {}".format(self.hostname)).center(100),Format=True,PDF=pdf)
                    STARTUP.STORE_DATA(ping_out,Format=False,PDF=pdf)
    
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
                    str_out = f'''The authenticity of the host '::ffff:{self.hostname}' cannot be established.
                            ssh-rsa key fingerprint is {self.fingerprint}.
                            Are you sure you waRU_Detailsnt to continue connecting (yes/no)? yes'''.strip()
                    STARTUP.STORE_DATA(str_out,Format=False,PDF = pdf)
                    STARTUP.STORE_DATA(f'''\n{self.USER_N }@::ffff:{self.hostname} password: \n''',Format=False,PDF = pdf)
                    STARTUP.append_data_and_print('Netconf Session Established || Successful',summary)

                    ###############################################################################
                    ## Test Procedure 2
                    ###############################################################################
                    Test_Step2 = "\tTER NETCONF Client and O-RU NETCONF Server exchange capabilities through the NETCONF <hello> messages"
                    STARTUP.STORE_DATA('{}'.format(Test_Step2),Format='TEST_STEP',PDF = pdf)
                    STARTUP.STORE_DATA(f'''> status\nCurrent NETCONF self.session:\nID\t: {self.session.session_id}\nHost\t: :ffff:{self.hostname}\nPort\t: {self.call_home_port}\nTransport\t: SSH\nCapabilities:''',Format=False,PDF = pdf)
                    for server_capability in self.session.server_capabilities:
                        STARTUP.STORE_DATA(server_capability,Format=False,PDF = pdf)
                    STARTUP.append_data_and_print('Hello Capabilities Exchanged || Successful',summary)
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
                STARTUP.STORE_DATA(f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
                return [e.type, e.tag, e.severity, e.path, e.message, exc_tb.tb_lineno]

            except Exception as e:
                STARTUP.STORE_DATA('{}'.format(e), Format=True,PDF=pdf)
                exc_type, exc_obj, exc_tb = sys.exc_info()
                STARTUP.STORE_DATA(f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
                return e
        return False




def result_Declaration():
    tc001_obj = vlan_scan()
    Check = tc001_obj.Call_Home()
    if Check == False:
        STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
        STARTUP.STORE_DATA('SFP link not detected',Format=False,PDF= pdf)
        STARTUP.ACT_RES(f"{'Create Vlan with Vlan Scan' : <50}{'||' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(235, 52, 52))
        STARTUP.append_data_and_print('FAIL_REASON || SFP link not detected',summary)
        STARTUP.append_data_and_print(f"{'Create Vlan with Vlan Scan' : <50}{'||' : ^20}{'FAIL' : ^20}",summary)
        return False

    ###############################################################################
    ## Expected/Actual Result
    ###############################################################################
    STARTUP.GET_SYSTEM_LOGS(tc001_obj.hostname,tc001_obj.USER_N,tc001_obj.PSWRD,pdf)
    Exp_Result = 'Expected Result : The TER NETCONF Client and O-RU NETCONF Server exchange capabilities through NETCONF <hello> messages.'
    STARTUP.STORE_DATA(Exp_Result,Format='DESC',PDF= pdf)
    STARTUP.STORE_DATA('\t\t{}'.format('****************** Actual Result ******************'),Format=True,PDF= pdf)
    try:
        if Check == True:
            STARTUP.ACT_RES(f"{'Create Vlan with Vlan Scan' : <50}{'||' : ^20}{'SUCCESS' : ^20}",PDF= pdf,COL=(105, 224, 113))
            STARTUP.append_data_and_print(f"{'Create Vlan with Vlan Scan' : <50}{'||' : ^20}{'PASS' : ^20}",summary)
            return True

        elif type(Check) == list:
            STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
            Error_Info = '''\terror-tag \t: \t{}\n\terror-type \t: \t{}\n\terror-severity \t: \t{}\n\tDescription' \t: \t{}'''.format(*map(str,Check))
            STARTUP.STORE_DATA(Error_Info,Format=False,PDF= pdf)
            STARTUP.ACT_RES(f"{'Create Vlan with Vlan Scan' : <50}{'||' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(235, 52, 52))
            STARTUP.append_data_and_print("FAIL_REASON || {}".format(Error_Info),summary)
            STARTUP.append_data_and_print(f"{'Create Vlan with Vlan Scan' : <50}{'||' : ^20}{'FAIL' : ^20}",summary)
            return False

        else:
            STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
            STARTUP.STORE_DATA('{}'.format(Check),Format=False,PDF= pdf)
            STARTUP.ACT_RES(f"{'Create Vlan with Vlan Scan' : <50}{'||' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(235, 52, 52))
            STARTUP.append_data_and_print('FAIL_REASON || {}'.format(Check),summary)
            STARTUP.append_data_and_print(f"{'Create Vlan with Vlan Scan' : <50}{'||' : ^20}{'FAIL' : ^20}",summary)
            return False
            
    except Exception as e:
            STARTUP.STORE_DATA('{}'.format(e), Format=True,PDF=pdf)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
            STARTUP.append_data_and_print('FAIL_REASON || {}'.format(e),summary)
            STARTUP.append_data_and_print(f"{'Create Vlan with Vlan Scan' : <50}{'||' : ^20}{'FAIL' : ^20}",summary)
            return False  

    ###############################################################################
    ## For Capturing the logs
    ###############################################################################
    finally:
        STARTUP.HEADING(PDF=pdf,data='{0} Summary {0}'.format('*'*30))
        STARTUP.render_table_data(pdf,STARTUP.append_data(summary))
        STARTUP.CREATE_LOGS('Vlan_Scan',PDF=pdf)
    

if __name__ == "__main__":
    start_time = datetime.fromtimestamp(int(time.time()))
    Test_procedure = [f"{'='*100}\nTest case *Vlan Scan* Started!! Status: Running\n{'='*100}",'** Test Coverage **'.center(50),'Read Vlan tag comes from RU',
                'Configure DHCP server','Create Vlan in test server','Restart DHCP Server','Ping the DHCP IP assign to Vlan',
                'Perform Call Home','Capability exchange', 'Start Time : {}'.format(start_time)]
    notification('\n'.join(Test_procedure))
    Result = result_Declaration()
    end_time = datetime.fromtimestamp(int(time.time()))
    st_time = 'Start Time : {}'.format(start_time)
    en_time = 'End Time : {}'.format(end_time)
    execution_time = 'Execution Time is : {}'.format(end_time-start_time)
    print('-'*100)
    print(f'{st_time}\n{en_time}\n{execution_time}')
    summary.insert(0,'******* Result *******'.center(50))
    notification('\n'.join(summary[:-1]))
    notification(f'{st_time}\n{en_time}\n{execution_time}')
    notification(f"{'='*100}\n{summary[-1]}\n{'='*100}")
    if Result!=True:
        sys.exit()

