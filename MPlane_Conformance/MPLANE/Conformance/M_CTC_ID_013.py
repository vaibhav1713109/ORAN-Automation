###############################################################################
##@ FILE NAME:      M_CTC_ID_013
##@ TEST SCOPE:     M PLANE O-RAN CONFORMANCE
##@ Version:        V_1.0.0
##@ Support:        @Ramiyer, @VaibhavDhiman, @PriyaSharma
###############################################################################

###############################################################################
## Package Imports 
###############################################################################

import socket, sys, os, warnings, time, xmltodict, xml.dom.minidom, paramiko, lxml.etree
from ncclient import manager
from ncclient.operations.rpc import RPC, RPCError
from ncclient.transport import errors
from paramiko.ssh_exception import NoValidConnectionsError
from ncclient.operations.errors import TimeoutExpiredError
from ncclient.transport.errors import SessionCloseError
from configparser import ConfigParser
from scapy.all import *

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
configur.read('{}/require/inputs.ini'.format(parent))

###############################################################################
## Related Imports
###############################################################################
from require.Notification import *
from require.Configuration import *
from require.calnexRest import calnexInit, calnexGet, calnexSet, calnexCreate, calnexDel,calnexGetVal


class M_CTC_ID_013(PDF,Configuration,netopeer_connection,genrate_pdf_report):
   
    # init method or constructor 
    def __init__(self):
        PDF.__init__(self)
        netopeer_connection.__init__(self)
        Configuration.__init__(self)
        genrate_pdf_report.__init__(self)
        PDF.PDF_CAP(self)
        self.ptp_port = configur.get('INFO','PTP_SyncE_Port')
        self.P_NEO_IP = configur.get('INFO','P_NEO_IP')
        self.summary = []
        self.fm_filter = '''
                        <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                        <active-alarm-list xmlns="urn:o-ran:fm:1.0">
                        </active-alarm-list>
                        </filter>
                        '''
    ###############################################################################
    ## Test Procedure
    ###############################################################################
    def test_execution(self,cmd,ethtool_out,ping_output):
        try:
            netopeer_connection.session_login(self,timeout=60,username=self.username, password=self.password)
            if self.session:
                Test_Desc = 'Test Description : The minimum functions of the TER described in section 2.1 that support validation of the M-Plane are operational, configured and connected to the O-RU'
                Configuration.append_data_and_print(self,'Netopeer Connection || Successful')
                Test_Desc = '''Test Description : This scenario is MANDATORY for an O-RU supporting the Hybrid M-plane architecture model.
                        This test validates that the O-RU correctly implements NETCONF Access Control user privileges.
                        The scenario corresponds to the following chapters in [3]:
                        3.4 NETCONF Access Control '''   
                
                Result = netopeer_connection.add_test_description(self,Test_Description=Test_Desc, Test_Case_name='M_CTC_ID_013')
                if len(Result) > 2:
                    self.running_sw, self.running_false_sw, self.inactive_slot = Result[0], Result[1], Result[2]

                print(self.username,self.password)
                PDF.STORE_DATA(self,'{}'.format(cmd).center(100),Format=True,)
                PDF.STORE_DATA(self,ethtool_out,Format=False)
                PDF.STORE_DATA(self,'{}'.format("ping -c 5 {}".format(self.hostname)).center(100),Format=True,)
                PDF.STORE_DATA(self,ping_output,Format=False)

                netopeer_connection.add_netopeer_connection_details(self)
                netopeer_connection.hello_capability(self)
                ###############################################################################
                ## Create_subscription
                ###############################################################################
                filter = """<filter type="xpath" xmlns="urn:ietf:params:xml:ns:netconf:notification:1.0" xmlns:notf_c="urn:ietf:params:xml:ns:yang:ietf-netconf-notifications" select="/notf_c:*"/>"""
                cmd = '> subscribe --filter-xpath /ietf-netconf-notifications:*'
                netopeer_connection.create_subscription(self,filter=filter,cmd=cmd)
        
                ###############################################################################
                ## Get_Filter_Alarm
                ###############################################################################
                PDF.add_page(self)
                cmd = "> get --filter-xpath /o-ran-fm:active-alarm-list/active-alarms"
                xml_pretty_fm, dict_data_fm = netopeer_connection.get(self,filter=self.fm_filter,cmd=cmd)

                ###############################################################################
                ## Test Procedure 1
                ###############################################################################
                Test_Step1 = '\t\tStep 1 The TER NETCONF Client sends the O-RU NETCONF Server a command to get the active-alarm-list.'
                PDF.STORE_DATA(self,"{}".format(Test_Step1),Format='TEST_STEP')
                alrm_name = list(dict_data_fm['data']['active-alarm-list']['active-alarms'])
                list_alrm = {}
                fault_id = []
                fault_text = []
                print(xml_pretty_fm)
                for i in alrm_name:
                    if "fault-id" in i.keys() and "fault-text" in i.keys():
                        fault_id.append(i["fault-id"])
                        fault_text.append(i["fault-text"])
                if 'No external sync source' in fault_text:
                    PDF.STORE_DATA(self,xml_pretty_fm,Format='XML')
                else:
                    PDF.STORE_DATA(self,xml_pretty_fm,Format='XML')
                    return 'Fault_text : {}'.format(fault_text)
                Configuration.append_data_and_print(self,'"No external sync source" captured || Success')
                return True
        ###############################################################################
        ## Check Access Denied
        ###############################################################################
        except RPCError as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            PDF.STORE_DATA(self,f"Error occured in line number {exc_tb.tb_lineno}", Format=False)
            rpc_error_element = etree.ElementTree(e.xml)
            rpc_error = etree.tostring(rpc_error_element).decode()
            rpc_error = xml.dom.minidom.parseString(rpc_error).toprettyxml()
            print(rpc_error)
            return rpc_error
        except Exception as e:
            PDF.STORE_DATA(self,'Test_execution Error : {}'.format(e), Format=True)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            PDF.STORE_DATA(self,f"Error occured in line number {exc_tb.tb_lineno}", Format=False)
            return e

        finally:
            try:
                self.session.close_session()
            except Exception as e:
                print('Test_execution Error : {}'.format(e))
    
    
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
            Result1 = self.test_execution(Output[2],Output[0],Output[1])
            return Result1


        ###############################################################################
        ## Exception
        ###############################################################################
        except Exception as e:
            PDF.STORE_DATA(self,'Main_Function Error : {}'.format(e), Format=True)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            PDF.STORE_DATA(self,f"Error occured in line number {exc_tb.tb_lineno}", Format=False)
            return e
        

    def api_call(self):
        start_time = datetime.fromtimestamp(int(time.time()))
        Test_procedure = [f"{'='*100}\nTest case *M_CTC_ID_013* Started!! Status: Running\n{'='*100}",'** Test Coverage **'.center(50),'DHCP/STATIC IP Ping',
                    'Netopeer Connection', 'Capability exchange','Create-subscription filter', 'Get Filter Active Alarm List', 
                    'Start Time : {}'.format(start_time),'='*100]
        notification('\n'.join(Test_procedure))
        Result = self.Main_Function()
        Configuration.Result_Declartion(self,'Retrieval of Active Alarm List',Result, 'M_CTC_ID_013')
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
    obj = M_CTC_ID_013()
    obj.api_call()
