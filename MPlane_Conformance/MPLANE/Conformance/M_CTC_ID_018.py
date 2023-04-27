###############################################################################
##@ FILE NAME:      M_CTC_ID_018
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



class M_CTC_ID_018(PDF,Configuration,netopeer_connection,genrate_pdf_report):
    # init method or constructor 
    def __init__(self):
        PDF.__init__(self)
        netopeer_connection.__init__(self)
        Configuration.__init__(self)
        genrate_pdf_report.__init__(self)
        PDF.PDF_CAP(self)
        self.summary = []
        self.u_name = '''
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
    ## Test Procedure
    ###############################################################################
    def test_execution(self):
        try:
            ###############################################################################
            ## Test Procedure 1 : Connect to netopeer server
            ###############################################################################
            Test_Step1 = 'STEP 1. The TER NETCONF Client establishes a connection with the O-RU NETCONF Server.'
            PDF.STORE_DATA(self,"{}".format(Test_Step1), Format='TEST_STEP')
            ###############################################################################
            ## Create_subscription
            ###############################################################################
            filter = """<filter type="xpath" xmlns="urn:ietf:params:xml:ns:netconf:notification:1.0" xmlns:notf_c="urn:ietf:params:xml:ns:yang:ietf-netconf-notifications" select="/notf_c:*"/>"""
            cmd = '> subscribe --filter-xpath /ietf-netconf-notifications:*'
            netopeer_connection.create_subscription(self,filter=filter,cmd=cmd)

            ###############################################################################
            ## Initial Get Filter
            ###############################################################################
            PDF.add_page(self)
            cmd = "> get --filter-xpath /o-ran-usermgmt:users/user"
            xml_pretty_str, dict_data = netopeer_connection.get(self,filter=self.u_name,cmd=cmd)
            PDF.STORE_DATA(self,xml_pretty_str, Format='XML')
            Configuration.append_data_and_print(self,'User-mgmt get-filter || Successful')

            ###############################################################################
            ## Test Procedure 2 : Configure 3 users
            ###############################################################################
            Test_Step2 = 'STEP 2. The TER NETCONF Client configures three new user accounts in addition to the default sudo account already present and passwords these three accounts using o-ran-user.mgmt.yang'
            PDF.STORE_DATA(self,'{}'.format(Test_Step2),Format='TEST_STEP')

            ###############################################################################
            ## Genrate Random Username & Password with ORAN credential
            ###############################################################################    
            usrs = {}
            for i in range(1, 4):

                nam = genrate_username()
                pas = genrate_password()
                usrs[nam] = pas
            added_users = list(usrs.items())
            user_xml = f"""
                    <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                    <users xmlns="urn:o-ran:user-mgmt:1.0">
                        <user>
                            <name>{added_users[0][0]}</name>
                            <account-type>PASSWORD</account-type>
                            <password>{added_users[0][1]}</password>
                            <enabled>true</enabled>
                        </user>
                        <user>
                            <name>{added_users[1][0]}</name>
                            <account-type>PASSWORD</account-type>
                            <password>{added_users[1][1]}</password>
                            <enabled>true</enabled>
                        </user>
                        <user>
                            <name>{added_users[2][0]}</name>
                            <account-type>PASSWORD</account-type>
                            <password>{added_users[2][1]}</password>
                            <enabled>true</enabled>
                        </user>
                    </users>
                    </config>"""
            
            ###############################################################################
            ## Merge 3 Users
            ###############################################################################
            rpc_reply = netopeer_connection.edit_config(self,user_xml,'merge')
            if rpc_reply!= True:
                Configuration.append_data_and_print(self,'Configure 3 new user || Fail')
                print(rpc_reply)
                return rpc_reply
            Configuration.append_data_and_print(self,'Configure 3 new user || Successful')
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
                        PDF.STORE_DATA(self," ############# NOTIFICATIONS #############", Format=True)
                        x = xml.dom.minidom.parseString(notify)
                        xml_pretty_str = x.toprettyxml()
                        PDF.STORE_DATA(self,xml_pretty_str, Format='XML')
                        Configuration.append_data_and_print(self,'Configuraion chenged notification captured || Successful')
                        break
                except:
                    pass

            ###############################################################################
            ## Test Procedure 3 : Give Configured 3 users diffrent privilege
            ###############################################################################
            PDF.add_page(self)
            Test_Step3 = '''######### STEP 3. The TER NETCONF Client configures user account to group mappings for the three
            new accounts using ietf-netconf-acm.yang respectively one with "nms", one with "fm-pm" and one 
            with "swm" privilege. #########'''
            PDF.STORE_DATA(self,'{}'.format(Test_Step3),Format='TEST_STEP')
            add_fm = f'<user-name>{added_users[0][0]}</user-name>'
            add_nms = f'<user-name>{added_users[1][0]}</user-name>'
            add_swm = f'<user-name>{added_users[2][0]}</user-name>'

            nacm_file = open('{}/require/Yang_xml/M_CTC_ID_18.xml'.format(parent)).read()
            nacm_file = nacm_file.format(add_swm=add_swm, add_fm=add_fm, add_nms=add_nms)
            rpc_reply1 = netopeer_connection.edit_config(self,nacm_file,'merge')

            ###############################################################################
            ## Test Procedure 4 : Check the RPC Reply
            ###############################################################################
            Test_Step4 = 'STEP 4. The O-RU NETCONF Server confirms the operations for the above transactions.'
            PDF.STORE_DATA(self,'{}'.format(Test_Step4), Format='TEST_STEP')
            if rpc_reply1!=True:
                Configuration.append_data_and_print(self,'Configured users privilege for above 3 users || Fail')
                print(rpc_reply1)
                return rpc_reply1
            Configuration.append_data_and_print(self,'Configured users privilege for above 3 users || Successful')

            ###############################################################################
            ## Check_Notifications
            ############################################################################### 
            while True:
                n = self.session.take_notification(timeout=30)
                if n == None:
                    break
                notify = n.notification_xml
                dict_n = xmltodict.parse(str(notify))
                try:
                    sid = dict_n['notification']['netconf-config-change']['changed-by']['session-id']
                    if sid == self.session.session_id:
                        PDF.STORE_DATA(self," ############# NOTIFICATIONS #############", Format=True)
                        x = xml.dom.minidom.parseString(notify)
                        xml_pretty_str = x.toprettyxml()
                        PDF.STORE_DATA(self,xml_pretty_str, Format='XML')
                        Configuration.append_data_and_print(self,'Configuraion chenged notification captured || Successful')
                        break
                except:
                    pass

            ###############################################################################
            ## Post Get Filter of NACM
            ###############################################################################
            cmd = "> get --filter-xpath /ietf-netconf-acm:nacm/groups"
            xml_pretty_str, group_n = netopeer_connection.get(self,filter=self.nacm_filter,cmd=cmd)
            # print(xml_pretty_str)

            ###############################################################################
            ## Check whether users add in nacm or not
            ###############################################################################
            ADDED_USERS = list(usrs.keys())
            group_name = group_n['data']['nacm']['groups']['group']
            j = 0
            for i in group_name:
                if i['name'] == 'sudo':
                    pass
                elif i['name'] in ['fm-pm', 'nms', 'swm']:
                    if ADDED_USERS[j] not in i['user-name']:
                        PDF.STORE_DATA(self,
                            xml_pretty_str, Format='XML')
                        return f"User didn't merge in {i['name']} privilege"
                    j += 1
                    added_users[True]
                else:
                    PDF.STORE_DATA(self,xml_pretty_str, Format='XML')
                    return "User didn't merge in except these privilege ['sudo', 'fm-pm', 'nms', 'swm'] privilege"

            PDF.STORE_DATA(self,xml_pretty_str, Format='XML')
            
            

            ###############################################################################
            ## Test Procedure 4 : Post Get Filter of USERS
            ###############################################################################  
            Test_Step5 = 'STEP 5. The TER NETCONF Client retrieves a list of users from O-RU NETCONF Server. The newly created user accounts and mappings are validated.'
            PDF.STORE_DATA(self,'{}'.format(Test_Step5), Format='TEST_STEP')
            xml_pretty_str, user_n = netopeer_connection.get(self,filter=self.u_name,cmd=cmd)

            ###############################################################################
            ## Test Procedure 4 : Check whether users are merge
            ###############################################################################  
            USERs_info = user_n['data']['users']['user']
            ADDED_USERS_R = ADDED_USERS[::-1]  # Reeverse of added_users
            LIST_User = []
            for _ in range(3):
                user1 = USERs_info.pop()
                LIST_User.append(user1['name'])

            if LIST_User != ADDED_USERS_R:
                PDF.STORE_DATA(self,xml_pretty_str, Format='XML')
                return "Users didn't merge..."
            else:
                PDF.STORE_DATA(self,xml_pretty_str, Format='XML')
            Configuration.append_data_and_print(self,'All 3 user merged and got privileges || Successful')

            return True
        except RPCError as e:
            rpc_error_element = etree.ElementTree(e.xml)
            rpc_error = etree.tostring(rpc_error_element).decode()
            rpc_error = xml.dom.minidom.parseString(rpc_error).toprettyxml()
            print(rpc_error)
            return rpc_error

        
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

            ###############################################################################
            ## Establishing netopeer connetion
            ###############################################################################
            self.session_login(timeout=60,username=self.username,password=self.password)

            if self.session:
                Configuration.append_data_and_print(self,'Netopeer Connection || Successful')
                Test_Desc = '''Test Description : This scenario is MANDATORY for an O-RU supporting the Hybrid M-plane architecture model.
                This test validates that user management model can be used to add users to the O-RU
                This scenario corresponds to the following chapters in [3]:
                3.3 SSH Connection Establishment
                3.4 NETCONF Access Control'''
                Result = netopeer_connection.add_test_description(self,Test_Description=Test_Desc, Test_Case_name='M_CTC_ID_018')
            
                if len(Result) > 2:
                    self.running_sw, self.running_false_sw, self.inactive_slot = Result[0], Result[1], Result[2]

                self.STORE_DATA('{}'.format(Output[2]).center(100),Format=True,)
                self.STORE_DATA(Output[0],Format=False)
                self.STORE_DATA('{}'.format("ping -c 5 {}".format(self.hostname)).center(100),Format=True,)
                self.STORE_DATA(Output[1],Format=False)

                time.sleep(5)
                netopeer_connection.add_netopeer_connection_details(self)
                netopeer_connection.hello_capability(self)
                result = self.test_execution()
                print(result)
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

    def api_call(self):
        start_time = datetime.fromtimestamp(int(time.time()))
        Test_procedure = [f"{'='*100}\nTest case *M_CTC_ID_018* Started!! Status: Running\n{'='*100}",'** Test Coverage **'.center(50),'DHCP/STATIC IP Ping',
                    'Netopeer Connection','Capability exchange','Create-subscription filter','Get Filter User Management','Merge new users','Give nacm privilege','Post get filter user-mgmt', 'Start Time : {}'.format(start_time),'='*100]
        notification('\n'.join(Test_procedure))
        Result = self.Main_Function()
        Configuration.Result_Declartion(self,'Sudo on Hybrid M-plane Architecture (positive case)',Result, 'M_CTC_ID_018')
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
    obj = M_CTC_ID_018()
    obj.api_call()

