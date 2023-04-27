###############################################################################
##@ FILE NAME:      M_CTC_ID_020
##@ TEST SCOPE:     M PLANE O-RAN CONFORMANCE
##@ Version:        V_1.0.0
##@ Support:        @Ramiyer, @VaibhavDhiman, @PriyaSharma
###############################################################################

###############################################################################
## Package Imports 
###############################################################################

import sys, os, time, xmltodict, xml.dom.minidom, socket
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


class M_CTC_ID_020(PDF,Configuration,netopeer_connection,genrate_pdf_report):
    # init method or constructor 
    def __init__(self):
        PDF.__init__(self)
        netopeer_connection.__init__(self)
        Configuration.__init__(self)
        genrate_pdf_report.__init__(self)
        PDF.PDF_CAP(self)
        self.summary = []
        self.new_user = ''
        self.new_pswrd = ''
        self.u_name = '''
                <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <users xmlns="urn:o-ran:user-mgmt:1.0">	
                </users>
                </filter>
                '''


    ###############################################################################
    ## Login with sudo user for getting user details
    ###############################################################################
    def pre_get_filter_user_mgmt(self,cmd,ethtool_out,ping_output):
        # Fetching all the interface
        try:
            self.session =  manager.connect(host=self.hostname, port=830, username=self.username, hostkey_verify=False, password=self.password, allow_agent=False, look_for_keys=False)
            if self.session:
                Configuration.append_data_and_print(self,'Netopeer Connection || Successful')
                Test_Desc = '''Test Description : This scenario is MANDATORY for an O-RU supporting the Hybrid M-plane architecture model.
                        This test validates that the O-RU correctly implements NETCONF Access Control user privileges.
                        The scenario corresponds to the following chapters in [3]:
                        3.4 NETCONF Access Control'''
                Result = netopeer_connection.add_test_description(self,Test_Description=Test_Desc, Test_Case_name='M_CTC_ID_022')
                if len(Result) > 2:
                    self.running_sw, self.running_false_sw, self.inactive_slot = Result[0], Result[1], Result[2]

                print(self.username,self.password)
                PDF.STORE_DATA(self,'{}'.format(cmd).center(100),Format=True,)
                PDF.STORE_DATA(self,ethtool_out,Format=False)
                PDF.STORE_DATA(self,'{}'.format("ping -c 5 {}".format(self.hostname)).center(100),Format=True,)
                PDF.STORE_DATA(self,ping_output,Format=False)

                ###############################################################################
                ## Initial Get Filter
                ###############################################################################
                PDF.STORE_DATA(self,'********** Initial Get ***********', Format='TEST_STEP')
                PDF.STORE_DATA(self,f'''> connect --ssh --host {self.hostname} --port 830 --login {self.username}
                        Interactive SSH Authentication
                        Type your password:
                        Password: 
                        ''', Format=False)
                cmd = "> get --filter-xpath /o-ran-usermgmt:users/user"
                xml_pretty_str, dict_data = netopeer_connection.get(self,filter=self.u_name,cmd=cmd)
                PDF.STORE_DATA(self,xml_pretty_str, Format='XML')
                Configuration.append_data_and_print(self,'Pre User-mgmt get-filter || Successful')
                return True

        except RPCError as e:
            rpc_error_element = etree.ElementTree(e.xml)
            rpc_error = etree.tostring(rpc_error_element).decode()
            rpc_error = xml.dom.minidom.parseString(rpc_error).toprettyxml()
            print(rpc_error)
            Configuration.append_data_and_print(self,'Pre User-mgmt get-filter || Fail')
            return 'Pre User-mgmt get-filter failed'
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
    ## Test Procedure
    ###############################################################################
    def test_execution(self):
        try:
            netopeer_connection.session_login(self,timeout=60,username=self.nms_user,password=self.nms_pawrd)
            if self.session :


                ###############################################################################
                ## Test Procedure 1 : Connect to netopeer server with NMS user
                ###############################################################################
                Test_Step1 = 'STEP 1 TER NETCONF client establishes a connection using a user account with nms privileges.'
                PDF.STORE_DATA(self,"{}".format(Test_Step1), Format='TEST_STEP')
                netopeer_connection.add_netopeer_connection_details(self)
                netopeer_connection.hello_capability(self)

                ###############################################################################
                ## Create_subscription
                ###############################################################################
                filter = """<filter type="xpath" xmlns="urn:ietf:params:xml:ns:netconf:notification:1.0" xmlns:notf_c="urn:ietf:params:xml:ns:yang:ietf-netconf-notifications" select="/notf_c:*"/>"""
                cmd = '> subscribe --filter-xpath /ietf-netconf-notifications:*'
                netopeer_connection.create_subscription(self,filter=filter,cmd=cmd)

        
        
                ###############################################################################
                ## Test Procedure 2 : Configure new user\password.
                ###############################################################################
                PDF.add_page(self)
                Test_Step2 = 'Step 2 TER NETCONF client attempts to configure a new user/password.'
                PDF.STORE_DATA(self,'{}'.format(Test_Step2), Format='TEST_STEP')
                Configuration.append_data_and_print(self,"Try to configure new user || In progress")

                ###############################################################################
                ## Merge New User
                ###############################################################################
                user_xml = f"""
                        <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
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
                if rpc_reply == True:
                    print(rpc_reply)
                    return 'Addition of new user is successful...'
                    
                ###############################################################################
                ## Check Access Denied
                ###############################################################################
                elif 'access-denied' in str(rpc_reply):
                    Test_Step3 = 'Step 3 NETCONF server replies rejecting the protocol operation with an \'access-denied\' error'
                    PDF.STORE_DATA(self,'{}'.format(Test_Step3), Format='TEST_STEP')
                    PDF.STORE_DATA(self,'RPC ERROR'.center(100), Format=True)
                    PDF.STORE_DATA(self,rpc_reply, Format=False)
                    Configuration.append_data_and_print(self,'Access-denied error captured || Successful')
                    return True
                else:
                    PDF.STORE_DATA(self,'RPC ERROR'.center(100), Format=True)
                    PDF.STORE_DATA(self,rpc_reply, Format=False)
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    PDF.STORE_DATA(self,f"Error occured in line number {exc_tb.tb_lineno}", Format=False)
                    return rpc_reply

        
        except RPCError as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            PDF.STORE_DATA(self,f"Error occured in line number {exc_tb.tb_lineno}", Format=False)
            rpc_error_element = etree.ElementTree(e.xml)
            rpc_error = etree.tostring(rpc_error_element).decode()
            rpc_error = xml.dom.minidom.parseString(rpc_error).toprettyxml()
            print(rpc_error)
            return rpc_error

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            PDF.STORE_DATA(self,"\t\tError : {}".format(e), Format=False)
            # new_session.close_session()
            return f"{e} \nError occured in line number {exc_tb.tb_lineno}"

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
        
        
        ###############################################################################
        ## Read User Name and password from Config.INI of Config.py
        ############################################################################### 
        self.new_user = genrate_username()
        self.new_pswrd = genrate_password()
        self.nms_user = configur.get('INFO','nms_user')
        self.nms_pawrd = configur.get('INFO','nms_pass')
        # print(self.nms_user,self.nms_pawrd)
        try:
            time.sleep(10)
            netopeer_connection.delete_system_log(self,host= self.hostname)
            result = self.pre_get_filter_user_mgmt(Output[2],Output[0],Output[1])
            if result != True:
                return result
            Result1 = self.test_execution()
            return Result1


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
        Test_procedure = [f"{'='*100}\nTest case *M_CTC_ID_020* Started!! Status: Running\n{'='*100}",'** Test Coverage **'.center(50),'DHCP/STATIC IP Ping',
                    'Pre Get Filter User Management', 'Netopeer Connection','Capability exchange','Create-subscription filter','Try to Merge new user with nms privilege',
                    'Access denied error', 'Start Time : {}'.format(start_time),'='*100]
        notification('\n'.join(Test_procedure))
        Result = self.Main_Function()
        Configuration.Result_Declartion(self,'Access Control NMS (negative case)',Result, 'M_CTC_ID_020')
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
    obj = M_CTC_ID_020()
    obj.api_call()

