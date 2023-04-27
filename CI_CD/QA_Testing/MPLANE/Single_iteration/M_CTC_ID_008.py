###############################################################################
##@ FILE NAME:      M_CTC_ID_008
##@ TEST SCOPE:     M PLANE O-RAN CONFORMANCE
##@ Version:        V_1.0.0
##@ Support:        @Ramiyer, @VaibhavDhiman, @PriyaSharma
###############################################################################

###############################################################################
## Package Imports 
###############################################################################


from distutils import errors
from random import randint
import socket, os, sys, lxml.etree, time, xmltodict, xml.dom.minidom, paramiko
from lxml import etree
from ncclient import manager
from ncclient.operations.rpc import RPCError
from ncclient.transport import errors
from ncclient.xml_ import to_ele
from paramiko.ssh_exception import NoValidConnectionsError
from ncclient.operations.errors import TimeoutExpiredError
from ncclient.transport.errors import SessionCloseError
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
configur.read('{}/require/inputs.ini'.format(parent))

###############################################################################
## Related Imports
###############################################################################
from require.Notification import *
from require.Configuration import *
from require.Genrate_User_Pass import *

class M_CTC_ID_008(PDF,Configuration,netopeer_connection,genrate_pdf_report):
    # init method or constructor 
    def __init__(self):
        PDF.__init__(self)
        netopeer_connection.__init__(self)
        Configuration.__init__(self)
        genrate_pdf_report.__init__(self)
        PDF.PDF_CAP(self)
        self.summary = []
        self.s_n_i = randint(10,15)
        self.g_t = randint(10,12)

    ###############################################################################
    ## Test Procedure
    ###############################################################################
    def test_execution(self,ethtool_cmd,ethtool_out,ping_output):
        try:
            netopeer_connection.session_login(self,timeout=60,username=self.username,password=self.password)
            if self.session :
                Configuration.append_data_and_print(self,'Netopeer Connection || Successful')
                Test_Desc = '''Test Description : This scenario is MANDATORY.
                        This test validates eAxC configuration and validation. The test scenario is intentionally limited in scope to be applicable to any O-RU hardware design.
                        This scenario corresponds to the following chapters in [3]:
                        Chapter 6 Configuration Management
                        Chapter 12.2 User plane message routing'''
                Result = netopeer_connection.add_test_description(self,Test_Description=Test_Desc, Test_Case_name='M_CTC_ID_008')
                if len(Result) > 2:
                    self.running_sw, self.running_false_sw, self.inactive_slot = Result[0], Result[1], Result[2]

                self.STORE_DATA('{}'.format(ethtool_cmd).center(100),Format=True,)
                self.STORE_DATA(ethtool_out,Format=False)
                self.STORE_DATA('{}'.format("ping -c 5 {}".format(self.hostname)).center(100),Format=True,)
                self.STORE_DATA(ping_output,Format=False)
        
                netopeer_connection.add_netopeer_connection_details(self)
                netopeer_connection.hello_capability(self)

                filter = """<filter type="xpath" xmlns="urn:ietf:params:xml:ns:netconf:notification:1.0" xmlns:supervision="urn:o-ran:supervision:1.0" select="/supervision:*"/>"""
                cmd = '> subscribe --filter-xpath /o-ran-supervision:*'
                netopeer_connection.create_subscription(self,filter=filter,cmd=cmd)

                ###############################################################################
                ## Configure Supervision RPC
                ###############################################################################
                Configuration.append_data_and_print(self,'Configure Supervision RPC || Started')
                xml_data = open("{}/require/Yang_xml/supervision.xml".format(parent)).read()
                xml_data = xml_data.format(super_n_i= self.s_n_i, guard_t_o= self.g_t)
                Test_Step1 = '\t\t TER NETCONF Client responds with <rpc supervision-watchdog-reset></rpc> to the O-RU NETCONF Server and NETCONF Server sends a reply to the TER NETCONF Client <rpc-reply><next-update-at>date-time</next-update-at></rpc-reply>'
                PDF.STORE_DATA(self,'{}'.format(Test_Step1),Format='TEST_STEP')

                rpc_reply = netopeer_connection.send_rpc(self,rpc_data=xml_data)
                if rpc_reply != True:
                    return rpc_reply

                PDF.STORE_DATA(self,'{}'.format(rpc_reply),Format='XML')
                t = int(self.s_n_i) + ((int(self.g_t))/3)

                ###############################################################################
                ## Iterating 30 Times
                ###############################################################################
                PDF.STORE_DATA(self,'\t\t******** Looped for 30 iterations ***********',Format=True)
                for i in range(1,31,1):
                #for i in range(1,3,1):
                    PDF.STORE_DATA(self,"{}th iteration".format(i),Format=True)
                    rpc_reply = self.send_rpc(rpc_data=xml_data)
                    if rpc_reply != True:
                        return rpc_reply
                    PDF.STORE_DATA(self,'{}'.format(rpc_reply),Format='XML')
                    
                    # next_up_time = dict_data['nc:rpc-reply']['next-update-at']['#text']
                    # PDF.STORE_DATA(self,next_up_time,OUTPUT_LIST=OUTPUT_LIST)
                    time.sleep(t)
                Configuration.append_data_and_print(self,'All 30 iteration completed || Successful')
                return True

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
        Test_procedure = [f"{'='*100}\nTest case *M_CTC_ID_008* Started!! Status: Running\n{'='*100}",'** Test Coverage **'.center(50),'DHCP/STATIC IP Ping',
                    'Netopeer Connection','Capability exchange','Create-subscription filter','Configure supervision rpc 30 iteration',
                    'Start Time : {}'.format(start_time),'='*100]
        notification('\n'.join(Test_procedure))
        Result = self.Main_Function()
        Configuration.Result_Declartion(self,'M-Plane Connection Supervision (positive case)',Result, 'M_CTC_ID_008')
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
    obj = M_CTC_ID_008()
    obj.api_call()
    time.sleep(20)
