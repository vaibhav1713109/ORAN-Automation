###############################################################################
##@ FILE NAME:      M_CTC_ID_026
##@ TEST SCOPE:     M PLANE O-RAN CONFORMANCE
##@ Version:        V_1.0.0
##@ Support:        @Ramiyer, @VaibhavDhiman, @PriyaSharma
###############################################################################

###############################################################################
## Package Imports 
###############################################################################

import sys, os, time, xmltodict, xml.dom.minidom, lxml.etree, ifcfg
from lxml import etree
from ncclient import manager
from ncclient.operations.rpc import RPC, RPCError
from ncclient.transport import errors
from paramiko.ssh_exception import NoValidConnectionsError
from ncclient.operations.errors import TimeoutExpiredError
from ncclient.transport.errors import SessionCloseError
from ncclient.xml_ import to_ele
from configparser import ConfigParser

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



class M_CTC_ID_026(PDF,Configuration,netopeer_connection,genrate_pdf_report):
    # init method or constructor 
    def __init__(self):
        PDF.__init__(self)
        netopeer_connection.__init__(self)
        Configuration.__init__(self)
        genrate_pdf_report.__init__(self)
        PDF.PDF_CAP(self)
        self.summary = []
        self.ru_mac = ''
        self.tx_arfcn = configur.get('INFO','tx_arfcn')
        self.rx_arfcn = configur.get('INFO','rx_arfcn')
        self.bandwidth = configur.get('INFO','bandwidth')
        self.tx_center_freq = configur.get('INFO','tx_center_frequency')
        self.rx_center_freq = configur.get('INFO','rx_center_frequency')
        self.duplex_scheme = configur.get('INFO','duplex_scheme')
        self.interface_ru = configur.get('INFO','fh_interface')
        self.scs_val = configur.get('INFO','scs_value')
        self.element_name = configur.get('INFO','element_name')
        self.interface_ru = configur.get('INFO','fh_interface')
        print(self.interface_ru)
        self.uplane_filter = '''
                <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <user-plane-configuration xmlns="urn:o-ran:uplane-conf:1.0">
                </user-plane-configuration>
                </filter>
                '''



    ###############################################################################
    ## Login with sudo user for getting user details
    ###############################################################################
    def fetch_mac_of_ru(self):
        try:
            v_name1 = '''
                    <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                    <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
                    </interfaces>
                    </filter>
            '''
            interface_name = self.session.get_config('running', v_name1).data_xml
            dict_interface = xmltodict.parse(str(interface_name))
            Interfaces = dict_interface['data']['interfaces']['interface']
            d = {}
            macs = {}
            for i in Interfaces:
                name = i['name']
                mac = i['mac-address']['#text']
                try:
                    IP_ADD = i['ipv4']['address']['ip']
                    if name:
                        d[name] = IP_ADD
                        macs[name] = mac
                except:
                    pass
            self.ru_mac = macs[self.interface_ru]
            print(self.ru_mac)
            return True
        except RPCError as e:
            return e
        


    ###############################################################################
    ## Test Procedure
    ###############################################################################
    def test_execution(self,cmd,ethtool_out,ping_output):
        try:
            netopeer_connection.session_login(self,timeout=60,username=self.username,password=self.password)
            if self.session :
                Configuration.append_data_and_print(self,'Netopeer Connection || Successful')
                Test_Desc = '''Test Description : This scenario is MANDATORY.
                        This test validates eAxC configuration and validation. The test scenario is intentionally limited in scope to be applicable to any O-RU hardware design.
                        This scenario corresponds to the following chapters in [3]:
                        Chapter 6 Configuration Management
                        Chapter 12.2 User plane message routing'''
                Result = netopeer_connection.add_test_description(self,Test_Description=Test_Desc, Test_Case_name='M_CTC_ID_026')
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
                
                Configuration.append_data_and_print(self,"Configuring o-ran-user-plane yang || Started")
                xml_1 = open('{0}/{1}/{2}'.format(root_dir,configur.get('INFO','ru_name_rev'),configur.get('INFO','uplane_xml'))).read()
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
                if rpc_reply != True:
                    Configuration.append_data_and_print(self,"Configured User Plane Yang || Fail")
                    return rpc_reply
                Configuration.append_data_and_print(self,"Configured User Plane Yang || Success")

                ###############################################################################
                ## Check_Notifications
                ###############################################################################   
                while True:
                    n = self.session.take_notification(timeout=10)
                    if n == None:
                        break
                    notify = n.notification_xml
                    dict_n = xmltodict.parse(str(notify))
                    try:
                        sid = dict_n['notification']['netconf-config-change']['changed-by']['session-id']
                        if sid == self.session.session_id:
                            PDF.STORE_DATA(self,"*********** NOTIFICATIONS *************",Format=True)
                            x = xml.dom.minidom.parseString(notify)
                            xml_pretty_str = x.toprettyxml()
                            PDF.STORE_DATA(self,xml_pretty_str,Format='XML')
                            Configuration.append_data_and_print(self,"Uplane Change Notification Captured || Successful")
                            break
                    except:
                        pass
                                        
                
                ###############################################################################
                ## Post Get Filter
                ###############################################################################   
                xml_pretty_str, dict_data = netopeer_connection.get(self,filter=self.uplane_filter,cmd=cmd)
                PDF.STORE_DATA(self,xml_pretty_str, Format='XML')
                ARFCN_RX1 = dict_data['data']['user-plane-configuration']['rx-array-carriers']['absolute-frequency-center']
                ARFCN_TX1 = dict_data['data']['user-plane-configuration']['tx-array-carriers']['absolute-frequency-center']

                ################# Check the ARFCN #################
                if (ARFCN_RX1 == self.rx_arfcn) and (ARFCN_TX1 == self.tx_arfcn):
                    PDF.STORE_DATA(self,xml_pretty_str,Format='XML')
                    Configuration.append_data_and_print(self,"o-ran-user-plane yang configured || Success")
                    return True
                else:
                    return "o-ran-uplane configuration didn't configure in O-RU"
                

        except RPCError as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
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
        Test_procedure = [f"{'='*100}\nTest case *UPlane Configuration* Started!! Status: Running\n{'='*100}",'** Test Coverage **'.center(50),'DHCP/Static IP Ping',
                'Netopeer Connection','Capability exchange','Create-subscription','UPlane Configuration', 'Start Time : {}'.format(start_time),'='*100]
        notification('\n'.join(Test_procedure))
        Result = self.Main_Function()
        Configuration.Result_Declartion(self,'O-RU configurability test (positive case)',Result, 'M_CTC_ID_026')
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
    obj = M_CTC_ID_026()
    obj.api_call()

