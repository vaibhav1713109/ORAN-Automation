###############################################################################
##@ FILE NAME:      Subscription to Notifications
##@ TEST SCOPE:     M PLANE O-RAN CONFORMANCE
##@ Version:        V_1.0.0
##@ Support:        @Ramiyer, @VaibhavDhiman, @PriyaSharma
###############################################################################

###############################################################################
## Package Imports 
###############################################################################

import sys, os, time, socket, xmltodict, xml.dom.minidom, lxml.etree, lxml.etree
from ncclient import manager
from datetime import datetime
from ncclient.operations import errors
from ncclient.operations.rpc import RPCError
from ncclient.transport import errors
from paramiko.ssh_exception import NoValidConnectionsError
from ncclient.operations.errors import TimeoutExpiredError
from ncclient.transport.errors import SessionCloseError
from configparser import ConfigParser
from ncclient.xml_ import to_ele

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

class Subscription_to_Notifications_3_1_2_1(PDF,Configuration,netopeer_connection,genrate_pdf_report):
    # init method or constructor 
    def __init__(self):
        PDF.__init__(self)
        netopeer_connection.__init__(self)
        Configuration.__init__(self)
        genrate_pdf_report.__init__(self)
        PDF.PDF_CAP(self)
        self.summary = []
            


    ###############################################################################
    ## Test Procedure
    ###############################################################################
    def Test_Execcution(self,ethtool_cmd,ethtool_out,ping_output):
        try:
            netopeer_connection.session_login(self,timeout=60,username=self.username,password=self.password)
            if self.session :
                Configuration.append_data_and_print(self,'Netopeer Connection || Successful')
                Test_Desc = '''Test Description : This scenario is MANDATORY.
                This test validates that the O-RU properly handles a NETCONF subscription to notifications.
                This scenario corresponds to the following chapters in [3]:
                8.2 Manage Alarm Requests'''
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
                ## Genrate Notification and alarm
                ###############################################################################        
                xml_data2 = open("{}/require/Yang_xml/sw_install.xml".format(parent)).read()
                if '1' in self.slot_name:
                    self.slot_name = self.slot_name[:-1]+'2'
                else:
                    self.slot_name = self.slot_name[:-1]+'1'
                xml_data2 = xml_data2.format(slot_name=self.slot_name,File_name = '')
                PDF.STORE_DATA(self,'******* Replace with below xml ********', Format=True)
                PDF.STORE_DATA(self,xml_data2, Format='XML')
                d3 = self.session.dispatch(to_ele(xml_data2))

                ###############################################################################
                ## Check_Notification
                ###############################################################################
                PDF.STORE_DATA(self,'{}'.format('################## Check_Notification ##################'),Format=True)
                while True:
                    n = self.session.take_notification(timeout=30)
                    if n == None:
                        break
                    notify=n.notification_xml
                    dict_n = xmltodict.parse(str(notify))
                    s = xml.dom.minidom.parseString(notify)
                    xml_pretty_str = s.toprettyxml()
                    PDF.STORE_DATA(self,xml_pretty_str,Format='XML')
                    PDF.STORE_DATA(self,'{}\n'.format('-'*100),Format=False)
                Configuration.append_data_and_print(self,'All relevent notifications captured || Successful')
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
            Result = self.Test_Execcution(Output[2],Output[0],Output[1])
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
        Test_procedure = [f"{'='*100}\nTest case *Subscription to Notifications* Started!! Status: Running\n{'='*100}",'** Test Coverage **'.center(50),'Static IP Ping',
                'Netopeer Connection','Capability exchange','Global create-subscription','Captured Alarm Notification', 'Start Time : {}'.format(start_time),'='*100]
        notification('\n'.join(Test_procedure))
        Result = self.Main_Function()
        Configuration.Result_Declartion(self,'Subscription to Notifications',Result, 'Subscription_to_Notifications_3_1_2_1')
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
    obj = Subscription_to_Notifications_3_1_2_1()
    obj.api_call()
    time.sleep(20)

  