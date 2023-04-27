###############################################################################
##@ FILE NAME:      M_CTC_ID_027
##@ TEST SCOPE:     M PLANE O-RAN CONFORMANCE
##@ Version:        V_1.0.0
##@ Support:        @Ramiyer, @VaibhavDhiman, @PriyaSharma
###############################################################################

###############################################################################
## Package Imports 
###############################################################################

import sys, os, time, xmltodict, xml.dom.minidom, lxml.etree, ifcfg, socket
from lxml import etree
from ncclient import manager
from ncclient.operations.rpc import RPC, RPCError
from ncclient.transport import errors
from paramiko.ssh_exception import NoValidConnectionsError
from ncclient.operations.errors import TimeoutExpiredError
from ncclient.transport.errors import SessionCloseError
from ncclient.xml_ import to_ele
from configparser import ConfigParser
from scapy.all import *

###############################################################################
## Directory Path
###############################################################################
dir_name = os.path.dirname(os.path.abspath(__file__))
parent = os.path.dirname(dir_name)
# print(parent)
root_dir = parent.rsplit('/',1)[0]
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
from require.Genrate_User_Pass import *
from Single_iteration.M_CTC_ID_026 import *


class M_CTC_ID_027(M_CTC_ID_026):
    # init method or constructor 
    def __init__(self):
        super().__init__()

    
    ###############################################################################
    ## Test Procedure
    ###############################################################################
    def test_execution(self,cmd,ethtool_out,ping_output):
        try:
            netopeer_connection.session_login(self,timeout=60,username=self.username,password=self.password)
            if self.session :
                Configuration.append_data_and_print(self,'Netopeer Connection || Successful')
                Test_Desc = '''Test Description : This scenario is MANDATORY.
                            The test scenario is intentionally limited to scope that shall be testable without a need to modify test scenario
                            according O-RU's hardware design.
                            This test verifies that the O-RU NETCONF Server supports configurability with validation.
                            This scenario corresponds to the following chapters in [3]:
                            6 Configuration Management
                            12.2 User plane message routing'''
                Result = netopeer_connection.add_test_description(self,Test_Description=Test_Desc, Test_Case_name='M_CTC_ID_027')
                if len(Result) > 2:
                    self.running_sw, self.running_false_sw, self.inactive_slot = Result[0], Result[1], Result[2]

                self.STORE_DATA('{}'.format(cmd).center(100),Format=True,)
                self.STORE_DATA(ethtool_out,Format=False)
                self.STORE_DATA('{}'.format("ping -c 5 {}".format(self.hostname)).center(100),Format=True,)
                self.STORE_DATA(ping_output,Format=False)

                result = self.fetch_mac_of_ru()
                if result != True:
                    return result
                netopeer_connection.add_netopeer_connection_details(self)
                netopeer_connection.hello_capability(self)

                ###############################################################################
                ## Create_subscription
                ###############################################################################
                filter = """<filter type="xpath" xmlns="urn:ietf:params:xml:ns:netconf:notification:1.0" xmlns:notf_c="urn:ietf:params:xml:ns:yang:ietf-netconf-notifications" select="/notf_c:*"/>"""
                cmd = '> subscribe --filter-xpath /ietf-netconf-notifications:*'
                netopeer_connection.create_subscription(self,filter=filter,cmd=cmd)
                
                ###############################################################################
                ## Configure Interface Yang
                ###############################################################################
                n = self.interface_ru[3]
                xml_data = open('{}/require/Yang_xml/interface.xml'.format(parent)).read()
                xml_data = xml_data.format(interface_name= self.interface_ru,mac = self.ru_mac, number= n)
                interface_xml =f'''
                        <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                        {xml_data}
                        </config>'''
                rpc_reply = netopeer_connection.edit_config(self,interface_xml,'merge')
                if rpc_reply != True:
                    Configuration.append_data_and_print(self,"Merging interface xml || Fail")
                    return rpc_reply
                Configuration.append_data_and_print(self,"Merging interface xml || Successful")
                ###############################################################################
                ## Configure Processing Yang
                ###############################################################################
                xml_data1 = open('{}/require/Yang_xml/processing.xml'.format(parent)).read()
                xml_data1 = xml_data1.format(int_name= self.interface_ru,ru_mac = self.ru_mac, du_mac = self.du_mac, element_name= self.element_name)
                processing_xml =f'''
                        <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                        {xml_data1}
                        </config>'''
                rpc_reply = netopeer_connection.edit_config(self,processing_xml,'merge')
                if rpc_reply != True:
                    Configuration.append_data_and_print(self,"Merging processing xml || Fail")
                    return rpc_reply
                Configuration.append_data_and_print(self,"Merging processing xml || Successful")

                ###############################################################################
                ## Pre get filter
                ###############################################################################
                PDF.add_page(self)
                cmd = "> get --filter-xpath /o-ran-uplane-conf:user-plane-configuration"
                xml_pretty_str, dict_data = netopeer_connection.get(self,filter=self.uplane_filter,cmd=cmd)
                PDF.STORE_DATA(self,xml_pretty_str, Format='XML')
                
                ###############################################################################
                ## Test Procedure 1 : Configure Uplane Yang
                ###############################################################################   
                PDF.add_page(self)          
                Test_Step1 = "STEP 1 The TER NETCONF Client assigns unique eAxC_IDs to low-level-rx-endpoints. The same set of eAxC_IDs is also assigned to low-level-tx-endpoints. The TER NETCONF Client uses <rpc><editconfig>."
                PDF.STORE_DATA(self,'{}'.format(Test_Step1),Format='TEST_STEP')
            
                xml_1 = open('{0}/{1}/{2}'.format(root_dir,configur.get('INFO','ru_name_rev'),configur.get('INFO','tc_27_xml'))).read()
                xml_1 = xml_1.format(tx_arfcn = self.tx_arfcn, rx_arfcn = self.rx_arfcn, bandwidth = int(float(self.bandwidth)*(10**6)), tx_center_freq = int(float(self.tx_center_freq)*(10**9)), 
                        rx_center_freq = int(float(self.rx_center_freq)*(10**9)), duplex_scheme = self.duplex_scheme,element_name= self.element_name, scs_val = self.scs_val)
                user_plane_xml = f"""
                            <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                            {xml_1}
                            </config>"""
                ###############################################################################
                ## Test Procedure 2 : Get RPC Reply
                ###############################################################################   
                PDF.add_page(self)            
                Test_Step2 = "STEP 2 The O-RU NETCONF Sever responds with the <rpc-reply> message indicating compeletion of the requested procedure."
                PDF.STORE_DATA(self,'{}'.format(Test_Step2),Format='TEST_STEP')
                rpc_reply = netopeer_connection.edit_config(self,user_plane_xml,'merge')
                if rpc_reply == True:
                    print(rpc_reply)
                    return 'Addition of user-plane yang is successful...'
                    
                ###############################################################################
                ## Check Access Denied
                ###############################################################################
                elif "Duplicate value '1' found for eaxc-id" in str(rpc_reply):
                    Test_Step3 = 'Step 3 NETCONF server replies rejecting the protocol operation with an \'access-denied\' error'
                    PDF.STORE_DATA(self,'{}'.format(Test_Step3), Format='TEST_STEP')
                    PDF.STORE_DATA(self,'RPC ERROR'.center(100), Format=True)
                    PDF.STORE_DATA(self,rpc_reply, Format=False)
                    Configuration.append_data_and_print(self,'Duplicate e-axcid found || Successful')
                    return True
                else:
                    PDF.STORE_DATA(self,'RPC ERROR'.center(100), Format=True)
                    PDF.STORE_DATA(self,rpc_reply, Format=False)
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    if exc_tb:
                        PDF.STORE_DATA(self,f"Error occured in line number {exc_tb.tb_lineno}", Format=False)
                    return rpc_reply

        ###############################################################################
        ## Check Access Denied
        ###############################################################################
        except RPCError as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            if exc_tb:
                PDF.STORE_DATA(self,f"Error occured in line number {exc_tb.tb_lineno}", Format=False)
            rpc_error_element = etree.ElementTree(e.xml)
            rpc_error = etree.tostring(rpc_error_element).decode()
            rpc_error = xml.dom.minidom.parseString(rpc_error).toprettyxml()
            print(rpc_error)
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
            
        

    ###############################################################################
    ## Main Function
    ###############################################################################
    def Main_Function(self):
        Output = Configuration.Link_detction_and_check_ping(self)
        if Output[-1]!=True:
            return Output[0]
        self.hostname = Output[-2]

        try:
            time.sleep(10)
            netopeer_connection.delete_system_log(self,host= self.hostname)
            self.du_mac = ifcfg.interfaces()[self.INTERFACE_NAME]['ether']
            Result = self.test_execution(Output[2],Output[0],Output[1])
            return Result
        ###############################################################################
        ## Exception
        ###############################################################################
        except Exception as e:
            PDF.STORE_DATA(self,'{}'.format(e), Format=True)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            PDF.STORE_DATA(self,f"Error occured in line number {exc_tb.tb_lineno}", Format=False)
            return e

    def api_call(self):
        start_time = datetime.fromtimestamp(int(time.time()))
        Test_procedure = [f"{'='*100}\nTest case *M_CTC_ID_27* Started!! Status: Running\n{'='*100}",'** Test Coverage **'.center(50),'DHCP/Static IP Ping',
                'Netopeer Connection','Capability exchange','Create-subscription','Configuring UPlane.yang with same eaxcid', 'Start Time : {}'.format(start_time),'='*100]
        notification('\n'.join(Test_procedure))
        Result = self.Main_Function()
        Configuration.Result_Declartion(self,'O-RU Configurability Test (negative case)',Result, 'M_CTC_ID_027')
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
        pass        


if __name__ == "__main__":
    obj = M_CTC_ID_027()
    obj.api_call()

