###############################################################################
##@ FILE NAME:      M_CTC_ID_023
##@ TEST SCOPE:     M PLANE O-RAN CONFORMANCE
##@ Version:        V_1.0.0
##@ Support:        @Ramiyer, @VaibhavDhiman, @PriyaSharma
###############################################################################

###############################################################################
## Package Imports 
###############################################################################

import sys, os, time, xmltodict, xml.dom.minidom, lxml.etree, paramiko, socket
from lxml import etree
from ncclient import manager
from ncclient.operations.rpc import RPC, RPCError
from ncclient.transport import errors
from paramiko.ssh_exception import NoValidConnectionsError
from ncclient.operations.errors import TimeoutExpiredError
from ncclient.transport.errors import SessionCloseError
from ncclient.xml_ import to_ele
from binascii import hexlify
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


class M_CTC_ID_023(PDF,Configuration,netopeer_connection,genrate_pdf_report):
    # init method or constructor 
    def __init__(self):
        PDF.__init__(self)
        netopeer_connection.__init__(self)
        Configuration.__init__(self)
        genrate_pdf_report.__init__(self)
        PDF.PDF_CAP(self)
        self.summary = []
        self.new_user = genrate_username()
        self.new_pswrd = genrate_password()
        self.user_filter = '''
                <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <users xmlns="urn:o-ran:user-mgmt:1.0">	
                </users>
                </filter>
                '''
        self.nacm_filter = '''
            <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            <nacm xmlns="urn:ietf:params:xml:ns:yang:ietf-netconf-acm">
                <groups>
                </groups>
            </nacm>
            </filter>
            '''

    ###############################################################################
    ## Create new user with sudo permission
    ###############################################################################
    def Create_new_user_with_sudo_permission(self,cmd,ethtool_out,ping_output):
        try:
            Test_Step1 = "Step 1 and 2: The TER NETCONF Client establishes connection and creates an account for new user using o-ran-user9 mgmt.yang"
            PDF.STORE_DATA(self,'{}'.format(Test_Step1),Format='TEST_STEP')
            netopeer_connection.session_login(self,timeout=60,username=self.username,password=self.password)
            if self.session :
                Configuration.append_data_and_print(self,'Netopeer Connection || Successful')
                Test_Desc = '''Test Description : This scenario is MANDATORY for an O-RU supporting the Hierarchical M-plane architecture model.
                        This test validates that the O-RU can successfully start up with activated software.
                        This scenario corresponds to the following chapters in [3]:
                        3.3 SSH Connection Establishment
                        3.4 NETCONF Access Control
                        3.7 closing a NETCONF Session'''
                Result = netopeer_connection.add_test_description(self,Test_Description=Test_Desc, Test_Case_name='M_CTC_ID_023')
            
                if len(Result) > 2:
                    self.running_sw, self.running_false_sw, self.inactive_slot = Result[0], Result[1], Result[2]

                self.STORE_DATA('{}'.format(cmd).center(100),Format=True,)
                self.STORE_DATA(ethtool_out,Format=False)
                self.STORE_DATA('{}'.format("ping -c 5 {}".format(self.hostname)).center(100),Format=True,)
                self.STORE_DATA(ping_output,Format=False)

                netopeer_connection.add_netopeer_connection_details(self)
                netopeer_connection.hello_capability(self)
                
                ###############################################################################
                ## Create_subscription
                ###############################################################################
                filter = """<filter type="xpath" xmlns="urn:ietf:params:xml:ns:netconf:notification:1.0" xmlns:notf_c="urn:ietf:params:xml:ns:yang:ietf-netconf-notifications" select="/notf_c:*"/>"""
                cmd = '> subscribe --filter-xpath /ietf-netconf-notifications:*'
                netopeer_connection.create_subscription(self,filter=filter,cmd=cmd)
                
                ###############################################################################
                ## Initial get filter
                ###############################################################################
                PDF.add_page(self)        
                cmd = "> get --filter-xpath /o-ran-usermgmt:users/user"
                xml_pretty_str, dict_data = netopeer_connection.get(self,filter=self.user_filter,cmd=cmd)
                PDF.STORE_DATA(self,xml_pretty_str, Format='XML')
                Configuration.append_data_and_print(self,'Pre User-mgmt get-filter || Successful')

                ###############################################################################
                ## Merge New User
                ###############################################################################
                user_xml = f"""<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                                <users xmlns="urn:o-ran:user-mgmt:1.0">
                                    <user>
                                        <name>{self.new_user}</name>
                                        <account-type>PASSWORD</account-type>
                                        <password>{self.new_pswrd}</password>
                                        <enabled>true</enabled>
                                    </user>
                                </users>
                                </config>"""

                        
                rpc_reply = netopeer_connection.edit_config(self,user_xml,'merge')
                if rpc_reply != True:
                    Configuration.append_data_and_print(self,"Merging new user || Fail")
                    return rpc_reply
                Configuration.append_data_and_print(self,"Merging new user || Successful")                

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
                        # PDF.STORE_DATA(self,sid,OUTPUT_LIST=OUTPUT_LIST)
                        if sid == self.session.session_id:
                            PDF.STORE_DATA(self,"******* NOTIFICATIONS *******",Format=True)
                            x = xml.dom.minidom.parseString(notify)
                            xml_pretty_str = x.toprettyxml()
                            PDF.STORE_DATA(self,xml_pretty_str,Format='XML')
                            Configuration.append_data_and_print(self,"Merge Notification Captured || Successful")
                            break
                    except:
                        pass
                    
                PDF.add_page(self)
                ###############################################################################
                ## post get filter
                ###############################################################################
                ###############################################################################
                ## Test Procedure 3 and 4 : NETCONF Client retrieves a list of users
                ###############################################################################        
                xml_pretty_str, dict_data = netopeer_connection.get(self,filter=self.user_filter,cmd=cmd)
                PDF.STORE_DATA(self,xml_pretty_str, Format='XML')
                Configuration.append_data_and_print(self,'Post User-mgmt get-filter || Successful')

                ###############################################################################
                ## Check whether users is merge
                ###############################################################################
                USERs_info = dict_data['data']['users']['user']
                User_list = []
                for user in USERs_info:
                    User_list.append(user['name'])
                if  self.new_user not in User_list:
                    PDF.STORE_DATA(self,xml_pretty_str,Format='XML')
                    return "Users didn't merge..."
                else:
                    PDF.STORE_DATA(self,xml_pretty_str,Format='XML')
                Configuration.append_data_and_print(self,'New User merged || Successful')
                

                ###############################################################################
                ## Configure New User In NACM
                ###############################################################################
                ad_us = f'<user-name>{self.new_user}</user-name>'
                nacm_file = open('{}/require/Yang_xml/nacm_sudo.xml'.format(parent)).read()
                nacm_file = nacm_file.format(add_sudo = ad_us)
                

                rpc_reply = netopeer_connection.edit_config(self,nacm_file,'merge')
                if rpc_reply != True:
                    Configuration.append_data_and_print(self,"Give sudo privilege || Fail")
                    return rpc_reply
                Configuration.append_data_and_print(self,'Give sudo privilege || Successful')

                ###############################################################################
                ## Notifications
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
                            PDF.STORE_DATA(self,"******* NOTIFICATIONS *******",Format=True)
                            x = xml.dom.minidom.parseString(notify)
                            xml_pretty_str = x.toprettyxml()
                            PDF.STORE_DATA(self,xml_pretty_str,Format='XML')
                            Configuration.append_data_and_print(self,'Captured required notification || Successful')
                            break
                    except:
                        pass
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
    ## Perform Call Home with new User
    ###############################################################################
    def Call_Home_with_new_user(self):
        try:
            ###############################################################################
            ## Tetst Procedure 5 and 6 : Perform Call Home with new User
            ###############################################################################
            PDF.add_page(self)
            Test_Step3 = 'Step 5 and 6: NETCONF Server establishes a TCP connection and performs the Call Home procedure to the TER NETCONF Client using the same IP and VLAN.'
            PDF.STORE_DATA(self,'{}'.format(Test_Step3),Format='TEST_STEP')
            new_session = netopeer_connection.call_home(self,host = '', port=4334, hostkey_verify=False,username = self.new_user, password = self.new_pswrd, timeout = 60, allow_agent = False , look_for_keys = False)
            hostname, port = new_session._session._transport.sock.getpeername()   #['ip_address', 'TCP_Port']
            server_key_obj = new_session._session._transport.get_remote_server_key()
            fingerprint = netopeer_connection.colonify(self,hexlify(server_key_obj.get_fingerprint()))
            LISTEN = f'''> listen --ssh --login {self.new_user}
            Waiting 60s for an SSH Call Home connection on port 4334...'''
            PDF.STORE_DATA(self,LISTEN,Format=False)
            Configuration.append_data_and_print(self,'Netconf Session ENew stablished w|| Successful')

            if new_session:
                query = 'yes'
                Authenticity =f'''The authenticity of the host '::ffff:{hostname}' cannot be established.
                ssh-rsa key fingerprint is {fingerprint}.
                '''
                PDF.STORE_DATA(self,Authenticity,Format=False)
                if query == 'yes':
                    PDF.STORE_DATA(self,f'''\n{self.new_user}@::ffff:{hostname} password: \n''',Format=False)
                    Test_Step4 = "Step 7: TER NETCONF Client and O-RU NETCONF Server exchange capabilities through the NETCONF <hello> messages"
                    PDF.STORE_DATA(self,'{}'.format(Test_Step4),Format='TEST_STEP')
                    STATUS = PDF.STATUS(self,hostname,new_session.session_id,port)
                    PDF.STORE_DATA(self,STATUS,Format=False)
                    for i in new_session.server_capabilities:
                        PDF.STORE_DATA(self,i,Format=False)
                    Configuration.append_data_and_print(self,'Hello Capabilities || Successful')
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
            Result = self.Create_new_user_with_sudo_permission(Output[2],Output[0],Output[1])
            if Result!=True:
                return Result
            Result1 = self.Call_Home_with_new_user()
            return Result1
        except Exception as e:
            PDF.STORE_DATA(self,'{}'.format(e), Format=True)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            PDF.STORE_DATA(self,f"Error occured in line number {exc_tb.tb_lineno}", Format=False)
            return e
    def api_call(self):
        start_time = datetime.fromtimestamp(int(time.time()))
        Test_procedure = [f"{'='*100}\nTest case *M_CTC_ID_023* Started!! Status: Running\n{'='*100}",'** Test Coverage **'.center(50),'DHCP/STATIC IP Ping',
                    'Pre Get Filter User Management', 'Netopeer Connection','Capability exchange','Create-subscription filter','Merge new user and give sudo privilege',
                    'Call home with new user','Capabilities Exchange', 'Start Time : {}'.format(start_time),'='*100]
        notification('\n'.join(Test_procedure))
        Result = self.Main_Function()
        Configuration.Result_Declartion(self,'Sudo on Hierarchical M-plane architecture (positive case)',Result, 'M_CTC_ID_023')
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
    obj = M_CTC_ID_023()
    obj.api_call()
                       
                        
        

