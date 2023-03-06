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
# from require.Vlan_Creation import *
from require.LINK_DETECTED import *



class notification_subscription(PDF,netopeer_connection,Configuration,genrate_pdf_report):
    def __init__(self) -> None:
        ###############################################################################
        ## Call the Constructor of all four class
        ###############################################################################
        PDF.__init__(self)
        netopeer_connection.__init__(self)
        Configuration.__init__(self)
        genrate_pdf_report.__init__(self)
        PDF.PDF_CAP(self)
        self.summary = []
            
        

    ###############################################################################
    ## Test Procedure
    ###############################################################################
    def Test_Execcution(self):
        ###############################################################################
        ## Test Procedure 1
        ###############################################################################
        PDF.add_page(self)
        Test_Step1 = "STEP 1 and 2 subscribe and check for the <rpc> reply."
        PDF.STORE_DATA(self,'{}'.format(Test_Step1),Format='TEST_STEP') 
            
        ###############################################################################
        ## Create_subscription
        ###############################################################################
        cmd = '> subscribe'
        netopeer_connection.create_subscription(self,filter=None,cmd=cmd)
        Configuration.append_and_print(self,'Global Subscription || Successful')


        ###############################################################################
        ## Genrate Notification and alarm
        ############################################################################### 
        pub_k = subprocess.getoutput('cat /etc/ssh/ssh_host_rsa_key.pub')
        pk = pub_k.split()
        pub_key = pk[1]       
        PDF.STORE_DATA(self,'{}'.format(Test_Step1), Format='TEST_STEP')
        xml_data2 = open("{}/require/Yang_xml/sw_download.xml".format(parent)).read()
        xml_data2 = xml_data2.format(rmt_path=self.rmt, password=self.sftp_pass, public_key=pub_key)
        rpc_reply = netopeer_connection.send_rpc(self,rpc_data=xml_data2)
        if rpc_reply != True:
            return rpc_reply

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
        
        Configuration.append_and_print(self,'Alarm Notification captured || Successful')
        Configuration.append_and_print(self,'All relevent notifications captured || Successful')
        return True 
    
    ###############################################################################
    ## Main Function
    ###############################################################################
    def Main_Function(self):
        Output = Configuration.Link_detction_and_check_ping(self,self.hostname)
        if Output[-1]!=True:
            return Output[0]
        
        self.sftp_user = configur.get('INFO','sftp_user')
        self.sftp_pass = configur.get('INFO','sftp_pass')
        self.interface_ip = ifcfg.interfaces()[self.INTERFACE_NAME]['inet']
        self.rmt = 'sftp://{0}@{1}:22/home'.format(self.sftp_user,self.interface_ip)

        try:
            time.sleep(5)
            netopeer_connection.delete_system_log(self,host= self.hostname)
            ###############################################################################
            ## Perform call home to get ip_details
            ###############################################################################
            self.session, self.login_info = netopeer_connection.session_login(self,timeout=20)
            # print(self.session, self.login_info)
            if self.session:
                Configuration.append_and_print(self,'Netopeer Connection || Successful')
                ###############################################################################
                ## Test Description
                ###############################################################################
                Test_Desc = '''Test Description : This scenario is MANDATORY.
                This test validates that the O-RU properly handles a NETCONF subscription to notifications.
                This scenario corresponds to the following chapters in [3]:
                8.2 Manage Alarm Requests'''
                Result = netopeer_connection.add_test_description(self,Test_Description=Test_Desc, Test_Case_name='Slot_Switch')
                if len(Result) > 2:
                    self.slot_name = Result[2]
                    pass
                else:
                    return Result

                PDF.STORE_DATA(self,'{}'.format(Output[2]).center(100),Format=True)
                PDF.STORE_DATA(self,Output[0],Format=False)
                PDF.STORE_DATA(self,'{}'.format("ping -c 5 {}".format(self.hostname)).center(100),Format=True)
                PDF.STORE_DATA(self,Output[1],Format=False)
                result = self.Test_Execcution()
                if result == True:
                    return True
                else:
                    return result
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
            return [e.type, e.tag, e.severity, e.path, e.message, exc_tb.tb_lineno]

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

    def Api_Call(self):
        start_time = datetime.fromtimestamp(int(time.time()))
        Test_procedure = [f"{'='*100}\nTest case *Subscription to Notifications* Started!! Status: Running\n{'='*100}",'** Test Coverage **'.center(50),'Static IP Ping',
                    'Netopeer Connection','Capability exchange','Global create-subscription','Captured Alarm Notification', 'Start Time : {}'.format(start_time),'='*100]
        notification('\n'.join(Test_procedure))
        Result = self.Main_Function()
        Configuration.Result_Declartion(self,'Subscription Notifications',Result, 'Subscription_Notification')
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
        pass

if __name__ == "__main__":
    obj = notification_subscription()
    obj.Api_Call()
    pass

