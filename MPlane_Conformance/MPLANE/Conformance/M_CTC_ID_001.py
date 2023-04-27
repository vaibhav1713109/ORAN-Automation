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
from lxml import etree
from ncclient.operations.rpc import RPCError
from scapy.all import *
from configparser import ConfigParser
from binascii import hexlify


###############################################################################
## Directory Path
###############################################################################
dir_name = os.path.dirname(os.path.abspath(__file__))
parent = os.path.dirname(dir_name)
root_dir = parent.rsplit('/',1)[0]
print(parent,'\n',root_dir)
sys.path.append(parent)

########################################################################
## For reading data from .ini file
########################################################################
configur = ConfigParser()
configur.read('{}/require/inputs.ini'.format(parent))

###############################################################################
## Related Imports
###############################################################################
from require.Notification import *
from require.Configuration import *



class Transport_and_Handshake_in_IPv4_Environment_positive_case_3_1_1_1(PDF,Configuration,netopeer_connection,genrate_pdf_report):
   
    # init method or constructor 
    def __init__(self):
        PDF.__init__(self)
        netopeer_connection.__init__(self)
        Configuration.__init__(self)
        genrate_pdf_report.__init__(self)
        PDF.PDF_CAP(self)
        self.ru_name = configur.get('INFO','ru_name_rev')
        self.summary = []
        self.dhcpp_st = ''
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
                    self.DU_vlan = pkt.vlan + 2
                    return True
        except Exception as e:
            print(f'Check_vlan_tag Error : {e}')
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
                    Configuration.append_data_and_print(self,f'Got DHCP IP {self.hostname} to the VLAN {self.DU_vlan} || Successful')
        except Exception as e:
            print(f'check_dhcp_ack Error : {e}')
            return False

    #######################################################################
    ## Sniffing(reading) live packets
    #######################################################################
    def read_live_packets_for_incoming_vlan_tag(self,iface = 'wlp0s20f3'):
        print(f'{"-"*100}\nReading Live packets for incoming vlan tag')
        timeout = 2*configur.getint('INFO','wait_time')
        pkts = sniff(iface = iface, stop_filter = self.check_vlan_tag, timeout = timeout)
        for pkt in pkts:
            val = self.check_vlan_tag(pkt)
            print(val,'read_live_packets_for_incoming_vlan_tag')
            if val:
                Configuration.append_data_and_print(self,'Captured incoming vlan tag || Successful')
                wrpcap('{0}/{1}/LOGS/MPLANE/vlan_tag.pcap'.format(root_dir,self.ru_name), pkts)
                return True
        else:
            Configuration.append_data_and_print(self,'Captured incoming vlan tag || Fail')
            return 'Captured incoming vlan tag || Fail'
 
    ###############################################################################
    ## create Vlan and append it into DHCP server
    ###############################################################################
    def dhcp_configuration_and_vlan_creation(self):
        Configuration.test_configure_isc_dhcp_server(self,self.INTERFACE_NAME,self.DU_vlan)
        Configuration.append_data_and_print(self,'Configured DHCP server || Successful')
        IPADDR = Configuration.test_configure_dhcpd_conf(self)
        VLAN_NAME = '{}.{}'.format(self.INTERFACE_NAME,self.DU_vlan)
        d = os.system(f'sudo ip link add link {self.INTERFACE_NAME} name {self.INTERFACE_NAME}.{self.DU_vlan} type vlan id {self.DU_vlan}')
        d = os.system(f'sudo ifconfig {self.INTERFACE_NAME}.{self.DU_vlan} {IPADDR} up')
        li_of_interfaces = list(ifcfg.interfaces().keys())
        if VLAN_NAME in li_of_interfaces:
            Configuration.append_data_and_print(self,'Vlan creation in test server || Successful')
            d = os.system('sudo /etc/init.d/isc-dhcp-server restart')
            self.dhcpp_st = subprocess.getoutput('sudo /etc/init.d/isc-dhcp-server status')
            Configuration.append_data_and_print(self,'Restart DHCP server || Successful')
            return True
        else:
            Configuration.append_data_and_print(self,'Vlan creation in test server || Fail')
            return 'Vlan creation in test server || Fail'

    def check_ip_in_dhcp_ack_message(self,iface = 'wlp0s20f3'):
        timeout = configur.getint('INFO','wait_time')
        pkts2 = sniff(iface = iface, stop_filter = self.check_dhcp_ack,timeout = timeout)
        for pkt in pkts2:
            val = self.check_dhcp_ack(pkt)
            print(val)
            if val != False:
                wrpcap('{0}/{1}/LOGS/MPLANE/dhcp.pcap'.format(root_dir,self.ru_name), pkts2)
                time.sleep(2)
                os.system('mergecap -w {0}/{1}/LOGS/MPLANE/vlan_scan.pcap {0}/{1}/LOGS/MPLANE/vlan_tag.pcap {0}/{1}/LOGS/MPLANE/dhcp.pcap'.format(root_dir,self.ru_name))
                os.system('rm {0}/{1}/LOGS/MPLANE/vlan_tag.pcap {0}/{1}/LOGS/MPLANE/dhcp.pcap'.format(root_dir,self.ru_name))
                return True
        else:
            Configuration.append_data_and_print(self,f'IP assignment to the VLAN {self.DU_vlan} || Fail')
            return f'IP assignment to the VLAN {self.DU_vlan} || Fail'
       

    ###############################################################################
    ## Performing Call home
    ###############################################################################
    def Main_Function(self):
        Result = Configuration.basic_check_for_vlan_scan(self)
        if Result != True:
            return Result

        
        # self.rps_switch_ip = configur.get('INFO','rps_switch_ip')
        # # Turn off O-RU
        # subprocess.run(["curl", "-u", "admin:rpsadmin", f"http://{self.rps_switch_ip}/rps?SetPower=1+0"])
        # print("Power OFF || successful.")
        # time.sleep(7)
        # # Turn on O-RU
        # subprocess.run(["curl", "-u", "admin:rpsadmin", f"http://{self.rps_switch_ip}/rps?SetPower=1+1"])
        # print("Power ON || successful.")
        # time.sleep(30)

        self.timeout = configur.getint('INFO','wait_time') - 30
        Configuration.test_configure_isc_dhcp_server(self,'lo',random.randint(0,1))
        subprocess.getoutput('sudo /etc/init.d/isc-dhcp-server restart')
        time.sleep(self.timeout)
        self.summary.clear()

        ###############################################################################
        ## Check the link detection
        ###############################################################################
        print(f'{"-"*100}\nCheck the Link Detection')
        Check1 = Configuration.check_link_detection(self)
        cmd = "ethtool " + self.INTERFACE_NAME
        ethtool_out = subprocess.getoutput(cmd)
        if Check1 == False or Check1 == None:
            PDF.STORE_DATA(self,'{}'.format(cmd).center(100),Format=True)
            PDF.STORE_DATA(self,ethtool_out,Format=False)
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
            Check3 = Configuration.check_ping_status(self,self.hostname)
            if Check3:
                Configuration.append_data_and_print(self,f'DHCP IP {self.hostname} Ping || Successful')
                ping_out = subprocess.getoutput("ping -c 5 {}".format(self.hostname))
                break
        else:
            PDF.STORE_DATA(self,'{}'.format(cmd).center(100),Format=True)
            PDF.STORE_DATA(self,ethtool_out,Format=False)
            PDF.STORE_DATA(self,'{}'.format("ping -c 5 {}".format(self.hostname)).center(100),Format=True)
            ping_out = subprocess.getoutput("ping -c 5 {}".format(self.hostname))
            PDF.STORE_DATA(self,ping_out,Format=False)
            return f'DHCP IP {self.hostname} not Pinging'

        

        for _ in range(5):
            try:
                time.sleep(5)
                netopeer_connection.delete_system_log(self,host= self.hostname)
                ###############################################################################
                ## Perform call home to get ip_details
                ###############################################################################
                self.session = netopeer_connection.call_home(self,host = '0.0.0.0', port=4334, hostkey_verify=False,username = self.username, password = self.password,timeout = 60,allow_agent = False , look_for_keys = False)
                self.hostname, self.call_home_port = self.session._session._transport.sock.getpeername()   #['ip_address', 'TCP_Port']
                server_key_obj = self.session._session._transport.get_remote_server_key()
                self.fingerprint = netopeer_connection.colonify(self,hexlify(server_key_obj.get_fingerprint()))

                if self.session:
                    Configuration.append_data_and_print(self,'Netopeer Connection || Successful')
                    RU_Details = netopeer_connection.Software_detail(self) 
                    for key, val in RU_Details.items():
                        if val[0] == 'true' and val[1] == 'true':
                            ###############################################################################
                            ## Test Description
                            ###############################################################################
                            Test_Desc = '''This scenario validates that the O-RU properly executes the session establishment procedure \nwith VLANs and a DHCPv4 server. This test is applicable to IPv4 environments.'''
                            CONFIDENTIAL = PDF.ADD_CONFIDENTIAL(self,'Vlan Scan',SW_R = val[2]) 
                            PDF.STORE_DATA(self,CONFIDENTIAL,Format='CONF')
                            PDF.STORE_DATA(self,Test_Desc,Format='DESC')
                            PDF.add_page(self)

                    self.dhcpp_st = subprocess.getoutput('sudo /etc/init.d/isc-dhcp-server status')
                    PDF.DHCP_Status(self,data=self.dhcpp_st)
                    PDF.STORE_DATA(self,'{}'.format(cmd).center(100),Format=True)
                    PDF.STORE_DATA(self,ethtool_out,Format=False)
                    PDF.STORE_DATA(self,'{}'.format("ping -c 5 {}".format(self.hostname)).center(100),Format=True)
                    PDF.STORE_DATA(self,ping_out,Format=False)
    
                    ###############################################################################
                    ## VLAN of Test PC
                    ###############################################################################
                    PDF.STORE_DATA(self,"\t Interfaces Present in DU Side",Format=True)
                    ip_config = subprocess.getoutput('ifconfig')
                    PDF.STORE_DATA(self,ip_config,Format='XML')


                    PDF.add_page(self)
                    time.sleep(10)
                    ###############################################################################
                    ## Test Procedure 1
                    ###############################################################################
                    Test_Step1 = '\tThe O-RU NETCONF Serve  establishes TCP connection and performs a Call Home procedure towards the NETCONF Client and establishes a SSH.'
                    PDF.STORE_DATA(self,'{}'.format(Test_Step1),Format='TEST_STEP')
                    LISTEN = f'''> listen --ssh --login {self.username }\nWaiting 60s for an SSH Call Home connection on port 4334...'''
                    PDF.STORE_DATA(self,LISTEN,Format=False)
                    str_out = f'''The authenticity of the host '::ffff:{self.hostname}' cannot be established.
                            ssh-rsa key fingerprint is {self.fingerprint}.
                            Are you sure you waRU_Detailsnt to continue connecting (yes/no)? yes'''.strip()
                    PDF.STORE_DATA(self,str_out,Format=False)
                    PDF.STORE_DATA(self,f'''\n{self.username }@::ffff:{self.hostname} password: \n''',Format=False)
                    Configuration.append_data_and_print(self,'Netconf Session Established || Successful')

                    ###############################################################################
                    ## Test Procedure 2
                    ###############################################################################
                    Test_Step2 = "\tTER NETCONF Client and O-RU NETCONF Server exchange capabilities through the NETCONF <hello> messages"
                    PDF.STORE_DATA(self,'{}'.format(Test_Step2),Format='TEST_STEP')
                    PDF.STORE_DATA(self,f'''> status\nCurrent NETCONF self.session:\nID\t: {self.session.session_id}\nHost\t: :ffff:{self.hostname}\nPort\t: {self.call_home_port}\nTransport\t: SSH\nCapabilities:''',Format=False)
                    for server_capability in self.session.server_capabilities:
                        PDF.STORE_DATA(self,server_capability,Format=False)
                    Configuration.append_data_and_print(self,'Hello Capabilities Exchanged || Successful')
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
                Error = '{} : Call Home is not initiated, SSH Socket connection lost....'.format(e)
                PDF.STORE_DATA(self,Error, Format=True)
                exc_type, exc_obj, exc_tb = sys.exc_info()
                PDF.STORE_DATA(self,f"Error occured in line number {exc_tb.tb_lineno}", Format=False)
                return Error
                
            except RPCError as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                PDF.STORE_DATA(self,f"Error occured in line number {exc_tb.tb_lineno}", Format=False)
                rpc_error_element = etree.ElementTree(e.xml)
                rpc_error = etree.tostring(rpc_error_element).decode()
                rpc_error = xml.dom.minidom.parseString(rpc_error).toprettyxml()
                return rpc_error

            except Exception as e:
                PDF.STORE_DATA(self,'{}'.format(e), Format=True)
                exc_type, exc_obj, exc_tb = sys.exc_info()
                PDF.STORE_DATA(self,f"Error occured in line number {exc_tb.tb_lineno}", Format=False)
                return e
            
            finally:
                try:
                    self.session.close_session()
                except Exception as e:
                    print(e)
        return False


    def api_call(self):
        start_time = datetime.fromtimestamp(int(time.time()))
        Result = self.Main_Function()
        Configuration.Result_Declartion(self,'Transport_and_Handshake_in_IPv4_Environment_positive_case_3_1_1_1',Result, 'Transport_and_Handshake_in_IPv4_Environment_positive_case_3_1_1_1')
        end_time = datetime.fromtimestamp(int(time.time()))
        st_time = 'Start Time : {}'.format(start_time)
        en_time = 'End Time : {}'.format(end_time)
        execution_time = 'Execution Time is : {}'.format(end_time-start_time)
        print('-'*100)
        print(f'{st_time}\n{en_time}\n{execution_time}')
        self.summary.insert(0,'******* Result *******'.center(50))
        self.summary.insert(0,'='*100)
        notification('\n'.join(self.summary[:-1]))
        notification(f'{st_time}\n{en_time}\n{execution_time}')
        notification(f"{'='*100}\n{self.summary[-1]}\n{'='*100}")
        if Result !=True:
            sys.exit(1)
        else:
            return True




if __name__ == "__main__":
    try:
        num_iterations = 1
        start_time = datetime.fromtimestamp(int(time.time()))
        end_time = datetime.fromtimestamp(int(time.time()))
        Pass, Fail = 0, 0
        temp = start_time
        Test_procedure = [f"{'='*100}\nTest case *Transport_and_Handshake_in_IPv4_Environment_positive_case_3_1_1_1* Started!! Status: Running\n{'='*100}",'** Test Coverage **'.center(50),'Read Vlan tag comes from RU',
                    'Configure DHCP server','Create Vlan in test server','Restart DHCP Server','Ping the DHCP IP assign to Vlan',
                    'Perform Call Home','Capability exchange', 'Start Time : {}'.format(start_time)]
        notification('\n'.join(Test_procedure))
        if len(sys.argv) > 1:
            num_iterations = int(sys.argv[1])
        for _ in range(num_iterations):
            Obj = Transport_and_Handshake_in_IPv4_Environment_positive_case_3_1_1_1()
            Result = Obj.api_call()
            if Result == True:
                Pass+=1
            else:
                Fail+=1
    except Exception as e:
        Fail+=1
        notification(f'Fail_Reason : {e}')
        notification(f"{'='*100}\nVlan Scan\t\t || \t\tFail\n{'='*100}")
        sys.exit(1)

    finally:
        notification(f'Total Iteration : {num_iterations}\nPass : {Pass}\nFail : {Fail}\nSkip : {num_iterations-Pass-Fail}\nTotal Execution Time : {end_time-start_time}')
        pass


