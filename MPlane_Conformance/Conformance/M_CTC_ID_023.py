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
configur.read('{}/inputs.ini'.format(dir_name))

###############################################################################
## Related Imports
###############################################################################
from require.Vlan_Creation import *
from require import STARTUP, Config
from require.Genrate_User_Pass import *



###############################################################################
## Initiate PDF
###############################################################################
pdf = STARTUP.PDF_CAP()

class M_CTC_ID_023(vlan_Creation):
    # init method or constructor 
    def __init__(self):
        super().__init__()
        self.hostname, self.call_home_port = '',''
        self.USER_N = ''
        self.PSWRD = ''
        self.new_user = ''
        self.new_pswrd = ''
        self.session = ''
        self.RU_Details = ''

    ###############################################################################
    ## Create new user with sudo permission
    ###############################################################################
    def Create_user(self):
        ###############################################################################
        ## Test Procedure 1 and 2 : Connect to netopeer server and merge new user
        ###############################################################################        
        STARTUP.STORE_DATA(
            '\t\t********** Connect to the NETCONF Server ***********', Format='TEST_STEP', PDF=pdf)
        Test_Step1 = "Step 1 and 2: The TER NETCONF Client establishes connection and creates an account for new user using o-ran-user9 mgmt.yang"
        STARTUP.STORE_DATA('{}'.format(Test_Step1),Format='TEST_STEP', PDF=pdf)
        STATUS = STARTUP.STATUS(self.hostname, self.USER_N, self.session.session_id, 830)
        STARTUP.STORE_DATA(STATUS, Format=False, PDF=pdf)

        ###############################################################################
        ## Server Capabilities
        ###############################################################################
        for cap in self.session.server_capabilities:
            STARTUP.STORE_DATA("\t{}".format(cap),Format=False,PDF = pdf)
            
        ###############################################################################
        ## Create_subscription
        ###############################################################################
        cap=self.session.create_subscription()
        STARTUP.STORE_DATA('> subscribe', Format=True, PDF=pdf)
        dict_data = xmltodict.parse(str(cap))
        if dict_data['nc:rpc-reply']['nc:ok'] == None:
            STARTUP.STORE_DATA('\nOk\n', Format=False, PDF=pdf)
        
        ###############################################################################
        ## Merge New User
        ###############################################################################
        snippet = f"""
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

                
        STARTUP.STORE_DATA('> edit-config  --target running --config --defop merge',Format=True, PDF=pdf)
        STARTUP.STORE_DATA('******* Replace with below xml ********',Format=True, PDF=pdf)
        STARTUP.STORE_DATA(snippet,Format='XML', PDF=pdf)
        data1 = self.session.edit_config(target="running" , config=snippet)
        dict_data1 = xmltodict.parse(str(data1))
        if dict_data1['nc:rpc-reply']['nc:ok']== None:
            STARTUP.STORE_DATA('\nOk\n',Format=True, PDF=pdf)
                

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
                # STARTUP.STORE_DATA(sid,OUTPUT_LIST=OUTPUT_LIST)
                if sid == self.session.session_id:
                    STARTUP.STORE_DATA("******* NOTIFICATIONS *******",Format=True, PDF=pdf)
                    x = xml.dom.minidom.parseString(notify)
                    xml_pretty_str = x.toprettyxml()
                    STARTUP.STORE_DATA(xml_pretty_str,Format='XML', PDF=pdf)
                    break
            except:
                pass
            
        ###############################################################################
        ## post get filter
        ###############################################################################
        pdf.add_page()
        u_name = '''
                <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <users xmlns="urn:o-ran:user-mgmt:1.0">	
                </users>
                </filter>
                '''

        ###############################################################################
        ## Test Procedure 3 and 4 : NETCONF Client retrieves a list of users
        ###############################################################################        
        user_name = self.session.get_config('running', u_name).data_xml
        Test_Step2 = "Step 3 and 4: The TER NETCONF Client retrieves a list of users"
        STARTUP.STORE_DATA('{}'.format(Test_Step2),Format='TEST_STEP', PDF=pdf)
        STARTUP.STORE_DATA("> get --filter-xpath /o-ran-usermgmt:users/user",Format=True, PDF=pdf)
        x = xml.dom.minidom.parseString(user_name)
        xml_pretty_str = x.toprettyxml()



        ###############################################################################
        ## Check whether users is merge
        ###############################################################################
        user_n = xmltodict.parse(str(user_name))
        USERs_info = user_n['data']['users']['user']
        User_list = []
        for user in USERs_info:
            User_list.append(user['name'])
        if  self.new_user not in User_list:
            STARTUP.STORE_DATA(xml_pretty_str,Format='XML', PDF=pdf)
            return "Users didn't merge..."
        else:
            STARTUP.STORE_DATA(xml_pretty_str,Format='XML', PDF=pdf)

                

        ###############################################################################
        ## Configure New User In NACM
        ###############################################################################
        ad_us = f'<user-name>{self.new_user}</user-name>'
        nacm_file = open('{}/require/Yang_xml/nacm_sudo.xml'.format(parent)).read()
        nacm_file = nacm_file.format(add_sudo = ad_us)
        

        STARTUP.STORE_DATA('> edit-config  --target running --config --defop merge',Format=True, PDF=pdf)
        STARTUP.STORE_DATA('******* Replace with below xml ********',Format=True, PDF=pdf)
        STARTUP.STORE_DATA(nacm_file,Format='XML', PDF=pdf)
        data2 = self.session.edit_config(target="running" , config=nacm_file, default_operation = 'merge')
        dict_data2 = xmltodict.parse(str(data2))
        if dict_data2['nc:rpc-reply']['nc:ok']== None:
            STARTUP.STORE_DATA('\nOk\n',Format=True, PDF=pdf)

        ###############################################################################
        ## Create_subscription
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
                    STARTUP.STORE_DATA("******* NOTIFICATIONS *******",Format=True, PDF=pdf)
                    x = xml.dom.minidom.parseString(notify)
                    xml_pretty_str = x.toprettyxml()
                    STARTUP.STORE_DATA(xml_pretty_str,Format='XML', PDF=pdf)
                    break
            except:
                pass
        return True
                    
                
        

    ###############################################################################
    ## Perform Call Home with new User
    ###############################################################################
    def Call_Home(self):
        
        try:
            ###############################################################################
            ## Tetst Procedure 5 and 6 : Perform Call Home with new User
            ###############################################################################
            pdf.add_page()
            Test_Step3 = 'Step 5 and 6: NETCONF Server establishes a TCP connection and performs the Call Home procedure to the TER NETCONF Client using the same IP and VLAN.'
            STARTUP.STORE_DATA('{}'.format(Test_Step3),Format='TEST_STEP', PDF=pdf)
            new_session = STARTUP.call_home(host = '', port=4334, hostkey_verify=False,username = self.new_user, password = self.new_pswrd, timeout = 60, allow_agent = False , look_for_keys = False)
            hostname, port = new_session._session._transport.sock.getpeername()   #['ip_address', 'TCP_Port']
            LISTEN = f'''> listen --ssh --login {self.new_user}
            Waiting 60s for an SSH Call Home connection on port 4334...'''
            STARTUP.STORE_DATA(LISTEN,Format=False, PDF=pdf)

            if new_session:
                query = 'yes'
                Authenticity =f'''The authenticity of the host '::ffff:{hostname}' cannot be established.
                ssh-rsa key fingerprint is 59:9e:90:48:f1:d7:6e:35:e8:d1:f6:1e:90:aa:a3:83:a0:6b:98:5a.
                Are you sure you want to continue connecting (yes/no)? yes'''
                STARTUP.STORE_DATA(Authenticity,Format=False, PDF=pdf)
                if query == 'yes':
                    STARTUP.STORE_DATA(f'''\n{self.new_user}@::ffff:{hostname} password: \n''',Format=False, PDF=pdf)
                    Test_Step4 = "Step 7: TER NETCONF Client and O-RU NETCONF Server exchange capabilities through the NETCONF <hello> messages"
                    STARTUP.STORE_DATA('{}'.format(Test_Step4),Format='TEST_STEP', PDF=pdf)
                    STATUS = f'''
                        > status
                        Current NETCONF session:
                        ID          : {new_session.session_id}
                        Host        : ::ffff:{hostname}
                        Port        : {port}
                        Transport   : SSH
                        Capabilities:
                        '''
                    STARTUP.STORE_DATA(STATUS,Format=False, PDF=pdf)
                    for i in new_session.server_capabilities:
                        STARTUP.STORE_DATA(i,Format=False, PDF=pdf)
                    return True
            new_session.close_session()


        ########################### Known Exceptions ############################
        except RPCError as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            new_session.close_session()
            return [e.type, e.tag, e.severity, e.message, exc_tb.tb_lineno]

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA("\t\tError : {}".format(e), Format=False, PDF=pdf)
            new_session.close_session()
            return f"{e} \nError occured in line number {exc_tb.tb_lineno}"


            


    ###############################################################################
    ## Main Function
    ###############################################################################
    def test_Main_023(self):
        Check1 = self.linked_detected()

        
        ###############################################################################
        ## Read User Name and password from Config.INI of Config.py
        ############################################################################### 
        self.USER_N = configur.get('INFO','sudo_user')
        self.PSWRD = configur.get('INFO','sudo_pass')
        if Check1 == False or Check1 == None:
            return Check1
        sniff(iface = self.interface, stop_filter = self.check_tcp_ip, timeout = 100)
        try:

            STARTUP.delete_system_log(host= self.hostname)
            ###############################################################################
            ## Perform call home to get ip_details
            ###############################################################################
            self.session = STARTUP.call_home(host = '0.0.0.0', port=4334, hostkey_verify=False,username = self.USER_N, password = self.PSWRD,timeout = 60,allow_agent = False , look_for_keys = False)
            self.hostname, self.call_home_port = self.session._session._transport.sock.getpeername()   #['ip_address', 'TCP_Port']
            
            if self.session:
                self.RU_Details = STARTUP.demo(session = self.session,host= self.hostname, port= 830)
                for key, val in self.RU_Details[1].items():
                    if val[0] == 'true' and val[1] == 'true':
                        ###############################################################################
                        ## Test Description
                        ###############################################################################
                        Test_Desc = '''Test Description : This scenario is MANDATORY for an O-RU supporting the Hierarchical M-plane architecture model.
                        This test validates that the O-RU can successfully start up with activated software.
                        This scenario corresponds to the following chapters in [3]:
                        3.3 SSH Connection Establishment
                        3.4 NETCONF Access Control
                        3.7 closing a NETCONF Session'''
                        CONFIDENTIAL = STARTUP.ADD_CONFIDENTIAL('23', SW_R=val[2])
                        STARTUP.STORE_DATA(CONFIDENTIAL, Format='CONF', PDF=pdf)
                        STARTUP.STORE_DATA(Test_Desc, Format='DESC', PDF=pdf)
                        pdf.add_page()


                    

                self.new_user = genrate_username()
                self.new_pswrd = genrate_password()
                time.sleep(5)
                result = self.Create_user()
                # self.session.close_session()
                if result == True:
                    return True
                else:
                    return result
        ###############################################################################
        ## Exception
        ###############################################################################
        except socket.timeout as e:
            Error = '{} : Call Home is not initiated, SSH Socket connection lost....'.format(
                e)
            STARTUP.STORE_DATA(Error, Format=True,PDF=pdf)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
            return Error

        except RPCError as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
            # self.session.close_session()
            return [e.type, e.tag, e.severity, e.path, e.message, exc_tb.tb_lineno]

        except Exception as e:
            STARTUP.STORE_DATA('{}'.format(e), Format=True,PDF=pdf)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
            # self.session.close_session()
            return e
        
        finally:
            try:
                self.session.close_session()
            except Exception as e:
                print(e)

                            
                        
        
def test_m_ctc_id_023():
    tc023_obj = M_CTC_ID_023()
    Check1 = tc023_obj.test_Main_023()
    if Check1 == False:
        STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
        STARTUP.STORE_DATA('SFP link not detected...',Format=False,PDF= pdf)
        STARTUP.ACT_RES(f"{'Sudo on Hierarchical M-plane architecture (positive case)' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=[255,0,0])
        return False
    try:
        if Check1 == True:
            Check2 = tc023_obj.Call_Home()
            if Check2 == True:
                STARTUP.GET_SYSTEM_LOGS(tc023_obj.hostname,tc023_obj.USER_N,tc023_obj.PSWRD,pdf)
                ###############################################################################
                ## Expected/Actual Result
                ###############################################################################
                Exp_Result = 'Expected Result : The TER NETCONF Client establishes a Call Home & SSH session towards the NETCONF Server with new user created above.'
                STARTUP.STORE_DATA(Exp_Result, Format='DESC', PDF=pdf)

                STARTUP.STORE_DATA('\t\t{}'.format('****************** Actual Result ******************'), Format=True, PDF=pdf)
                STARTUP.ACT_RES(f"{'Sudo on Hierarchical M-plane architecture (positive case)' : <50}{'=' : ^20}{'SUCCESS' : ^20}",PDF= pdf,COL=[0,255,0])
                return True
            
            else:
                if type(Check2) == list:
                    STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
                    Error_Info = '''ERROR\n\terror-type \t: \t{}\n\terror-tag \t: \t{}\n\terror-severity \t: \t{}\n\tmessage' \t: \t{}'''.format(*map(str,Check2))
                    STARTUP.STORE_DATA(Error_Info,Format=False,PDF= pdf)
                    STARTUP.ACT_RES(f"{'Sudo on Hierarchical M-plane architecture (positive case)' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=[255,0,0])
                    return False

                else:
                    STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
                    STARTUP.STORE_DATA(Check2,Format=False,PDF= pdf)
                    STARTUP.ACT_RES(f"{'Sudo on Hierarchical M-plane architecture (positive case)' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=[255,0,0])
                    return False
        else:
            Exp_Result = 'Expected Result : The TER NETCONF Client establishes a Call Home & SSH session towards the NETCONF Server with new user created above.'
            STARTUP.STORE_DATA(Exp_Result, Format='DESC', PDF=pdf)

            STARTUP.STORE_DATA('\t\t{}'.format('****************** Actual Result ******************'), Format=True, PDF=pdf)
            if type(Check1) == list:
                STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
                Error_Info = '''ERROR\n\terror-type \t: \t{}\n\terror-tag \t: \t{}\n\terror-severity \t: \t{}\n\tmessage' \t: \t{}'''.format(*map(str,Check1))
                STARTUP.STORE_DATA(Error_Info,Format=False,PDF= pdf)
                STARTUP.ACT_RES(f"{'Sudo on Hierarchical M-plane architecture (positive case)' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=[255,0,0])
                return False

    except Exception as e:
            STARTUP.STORE_DATA('{}'.format(e), Format=True,PDF=pdf)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
            return False

    ###############################################################################
    ## For Capturing the logs
    ###############################################################################
    finally:
        STARTUP.CREATE_LOGS('M_CTC_ID_023',PDF=pdf)


if __name__ == "__main__":
    test_m_ctc_id_023()
    pass
