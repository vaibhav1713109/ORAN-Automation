###############################################################################
##@ FILE NAME:      M_CTC_ID_022
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
from Conformance.Notification import *
from require.Vlan_Creation import *
from require import STARTUP, Config
from require.Genrate_User_Pass import *


###############################################################################
## Initiate PDF
###############################################################################
pdf = STARTUP.PDF_CAP() 
summary = []

class M_CTC_ID_022(vlan_Creation):
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
    ## ADD SWM User
    ########################################################from Notification import *#######################
    def add_swm_user(self):
        STARTUP.STORE_DATA('\n\n\t\t********** Connect to the NETCONF Server ***********\n\n',Format='TEST_STEP',PDF = pdf)
        STATUS = STARTUP.STATUS(self.hostname,self.USER_N,self.session.session_id,830)
        STARTUP.STORE_DATA(STATUS,Format=False,PDF = pdf)
        summary.append('Netconf Session Established!!')


        ###############################################################################
        ## Server Capabilities
        ###############################################################################
        for cap in self.session.server_capabilities:
            STARTUP.STORE_DATA("\t{}".format(cap),Format=False,PDF = pdf)
        summary.append('Hello Capabilities Exchanged!!')

        ###############################################################################
        ## Create_subscription
        ###############################################################################
        filter = """<filter type="xpath" xmlns="urn:ietf:params:xml:ns:netconf:notification:1.0" xmlns:notf_c="urn:ietf:params:xml:ns:yang:ietf-netconf-notifications" select="/notf_c:*"/>"""
        cap=self.session.create_subscription(filter=filter)
        STARTUP.STORE_DATA('> subscribe --filter-xpath /ietf-netconf-notifications:*', Format=True, PDF=pdf)
        dict_data = xmltodict.parse(str(cap))
        if dict_data['nc:rpc-reply']['nc:ok'] == None:
            STARTUP.STORE_DATA('\nOk\n', Format=False, PDF=pdf)
        summary.append('Subscription with netconf-config filter Performed!!')

        ###############################################################################
        ## Initial get filter
        ###############################################################################
        pdf.add_page()
        u_name = '''
                <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <users xmlns="urn:o-ran:user-mgmt:1.0">	
                </users>
                </filter>
                '''

        
        user_name = self.session.get_config('running', u_name).data_xml
        STARTUP.STORE_DATA("######### Initial Get Filter #########",Format=True, PDF=pdf)
        STARTUP.STORE_DATA("> get --filter-xpath /o-ran-usermgmt:users/user",Format=True, PDF=pdf)
        x = xml.dom.minidom.parseString(user_name)
        xml_pretty_str = x.toprettyxml()
        STARTUP.STORE_DATA(xml_pretty_str,Format='XML', PDF=pdf)


        ###############################################################################
        ## Merge New User
        ###############################################################################
        summary.append("Merge new user!!")
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
            STARTUP.STORE_DATA('\n{}\n'.format('-'*100),Format=False, PDF=pdf)
            STARTUP.STORE_DATA('Ok\n',Format=False, PDF=pdf)
            STARTUP.STORE_DATA('{}'.format('-'*100),Format=False, PDF=pdf)


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
                    STARTUP.STORE_DATA("******* NOTIFICATIONS *******",Format=True, PDF=pdf)
                    x = xml.dom.minidom.parseString(notify)
                    xml_pretty_str = x.toprettyxml()
                    STARTUP.STORE_DATA(xml_pretty_str,Format='XML', PDF=pdf)
                    break
            except:
                pass
        
        ###############################################################################
        ## Configure New User In NACM
        ###############################################################################
        summary.append("Give SWM privilege!!")
        ad_us = f'<user-name>{self.new_user}</user-name>'
        nacm_file = open('{}/require/Yang_xml/nacm_swm.xml'.format(parent)).read()
        nacm_file = nacm_file.format(add_swm = ad_us)
        
        STARTUP.STORE_DATA('> edit-config  --target running --config --defop merge',Format=True, PDF=pdf)
        STARTUP.STORE_DATA('******* Replace with below xml ********',Format=True, PDF=pdf)
        STARTUP.STORE_DATA(nacm_file,Format='XML', PDF=pdf)
    
        data2 = self.session.edit_config(target="running" , config=nacm_file, default_operation = 'merge')
        dict_data2 = xmltodict.parse(str(data2))
        if dict_data2['nc:rpc-reply']['nc:ok']== None:
            STARTUP.STORE_DATA('\n{}\n'.format('-'*100),Format=False, PDF=pdf)
            STARTUP.STORE_DATA('Ok\n',Format=False, PDF=pdf)
            STARTUP.STORE_DATA('{}'.format('-'*100),Format=False, PDF=pdf)

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
                    pdf.add_page()
                    STARTUP.STORE_DATA("******* NOTIFICATIONS *******",Format=True, PDF=pdf)
                    x = xml.dom.minidom.parseString(notify)
                    xml_pretty_str = x.toprettyxml()
                    STARTUP.STORE_DATA(xml_pretty_str,Format='XML', PDF=pdf)
                    break
            except:
                pass
                
        STARTUP.STORE_DATA("> get --filter-xpath /ietf-netconf-acm:nacm/groups",Format=True, PDF=pdf)
        u_name = '''
            <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            <nacm xmlns="urn:ietf:params:xml:ns:yang:ietf-netconf-acm">
                <groups>
                </groups>
            </nacm>
            </filter>
            '''
        user_name = self.session.get_config('running', u_name).data_xml
        s = xml.dom.minidom.parseString(user_name)

        xml_pretty_str = s.toprettyxml()

        ################# Check whether users add in nacm or not #################
        # group_n = xmltodict.parse(str(user_name))
        # group_name = group_n['data']['nacm']['groups']['group']
        # for i in group_name:
        #     STARTUP.STORE_DATA(i['name'],Format=False, PDF=pdf)
        #     if i['name'] == 'swm':
        #         if name not in i['user-name']:
        #             STARTUP.STORE_DATA(xml_pretty_str,Format='XML', PDF=pdf)
        #             return "User didn't merge in 'nms' privilege"
        #     else:
        #         return "User didn't merge in except these privilege ['sudo', 'fm-pm', 'nms', 'swm'] privilege"

        STARTUP.STORE_DATA(xml_pretty_str,Format='XML', PDF=pdf)
            
        ###############################################################################
        ## Get Filter of NACM
        ###############################################################################
        pdf.add_page()
        u_name = '''
                <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <users xmlns="urn:o-ran:user-mgmt:1.0">	
                </users>
                </filter>
                '''
        user_name = self.session.get_config('running', u_name).data_xml
        STARTUP.STORE_DATA("> get --filter-xpath /o-ran-usermgmt:users/user",Format=True, PDF=pdf)
        s = xml.dom.minidom.parseString(user_name)
        xml_pretty_str = s.toprettyxml()
        
        ###############################################################################
        ## Check whether users are merge
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
        # self.session.close_session()
        summary.append("User merge and give SWM privilage successfully!!")
        return True


    ###############################################################################
    ## Test Procedure
    ###############################################################################
    def test_procedure(self):
        ###############################################################################
        ## Test Procedure 1 : Connect to netopeer server with swm user
        ###############################################################################
        try:
            with manager.connect(host=self.hostname, port=830, username=self.new_user, hostkey_verify=False, password=self.new_pswrd, allow_agent = False , look_for_keys = False, timeout = 60) as new_session:
                pdf.add_page()
                Test_Step1 = 'STEP 1 TER NETCONF client establishes a connection using a user account with swm privileges.'
                STARTUP.STORE_DATA('{}'.format(Test_Step1),Format='TEST_STEP', PDF=pdf)
                STARTUP.STORE_DATA('\t\t********** Connect to the NETCONF Server ***********', Format='TEST_STEP', PDF=pdf)
                server_key_obj = new_session._session._transport.get_remote_server_key()
                fingerprint = STARTUP.colonify(STARTUP.hexlify(server_key_obj.get_fingerprint()))
                login_info = f'''> connect --ssh --host {self.hostname} --port 830 --login {self.new_user}
                        ssh-rsa key fingerprint is {fingerprint}
                        Interactive SSH Authentication done. 
                                '''
                STARTUP.STORE_DATA(login_info,Format=False,PDF = pdf)                
                STATUS = STARTUP.STATUS(self.hostname,self.new_user,new_session.session_id,830)       
                STARTUP.STORE_DATA(STATUS,Format=False,PDF = pdf)
                summary.append("Netconf Session Established with new SWM privilage user!!")


                ###############################################################################
                ## Server Capabilities
                ###############################################################################
                for cap in new_session.server_capabilities:
                    STARTUP.STORE_DATA("\t{}".format(cap),Format=False,PDF = pdf)
                summary.append('Hello Capabilities Exchanged!!')

                ###############################################################################
                ## Create_subscription
                ###############################################################################
                filter = """<filter type="xpath" xmlns="urn:ietf:params:xml:ns:netconf:notification:1.0" xmlns:notf_c="urn:ietf:params:xml:ns:yang:ietf-netconf-notifications" select="/notf_c:*"/>"""
                cap = new_session.create_subscription(filter=filter)
                STARTUP.STORE_DATA('> subscribe --filter-xpath /ietf-netconf-notifications:*', Format=True, PDF=pdf)
                dict_data = xmltodict.parse(str(cap))
                if dict_data['nc:rpc-reply']['nc:ok'] == None:
                    STARTUP.STORE_DATA('\nOk\n', Format=False, PDF=pdf)
                summary.append('Subscription with netconf-config filter Performed!!')
                
                ###############################################################################
                ## Test Procedure 2 : Configure a new o-ran-sync.yang
                ############################################################################### 
                summary.append('Try to configure o-ran-sync yang!!')
                proc_xml = open('{}/require/Yang_xml/sync.xml'.format(parent)).read() 
                Test_Step2 = 'Step 2 TER NETCONF client attempts to configure a new o-ran-sync.yang on the NETCONF server.'
                STARTUP.STORE_DATA("{}".format(Test_Step2), Format='TEST_STEP', PDF=pdf)
                pro = f'''
                <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                    {proc_xml}
                </config>
                '''
                STARTUP.STORE_DATA('> edit-config  --target running --config --defop replace',Format=True, PDF=pdf)
                STARTUP.STORE_DATA('******* Replace with below xml ********',Format=True, PDF=pdf)

                STARTUP.STORE_DATA(proc_xml,Format='XML', PDF=pdf)



                try:
                    data3 = new_session.edit_config(target="running" , config=pro, default_operation = 'replace')
                    if data3:
                        return f'\t*******Configuration are pushed*******\n{data3}'
                except RPCError as e:

                    ###############################################################################
                    ## Check Access Denied
                    ###############################################################################
                    if e.tag == 'access-denied':
                        Test_Step4 = 'Step 3 NETCONF server replies rejecting the protocol operation with an \'access-denied\' error.'
                        STARTUP.STORE_DATA('{}'.format(Test_Step4),Format='TEST_STEP', PDF=pdf)
                        STARTUP.STORE_DATA('ERROR\n',Format=False, PDF=pdf)
                        STARTUP.STORE_DATA(f"{'type' : ^20}{':' : ^10}{e.tag: ^10}\n",Format=False, PDF=pdf)
                        STARTUP.STORE_DATA(f"{'tag' : ^20}{':' : ^10}{e.type: ^10}\n",Format=False, PDF=pdf)
                        STARTUP.STORE_DATA(f"{'severity' : ^20}{':' : ^10}{e.severity: ^10}\n",Format=False, PDF=pdf)
                        STARTUP.STORE_DATA(f"{'path' : ^20}{':' : ^10}{e.path: ^10}\n",Format=False, PDF=pdf)
                        STARTUP.STORE_DATA(f"{'message' : ^20}{':' : ^10}{e.message: ^10}\n",Format=False, PDF=pdf)
                        summary.append('Access-denied error captured!!')
                        return True

                    else:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        return [e.type, e.tag, e.severity ,e.message,exc_tb.tb_lineno]
                    
                finally:
                    pass
                    # new_session.close_session()

        ########################### Known Exceptions ############################
        except RPCError as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            # new_session.close_session()
            return [e.type, e.tag, e.severity, e.message, exc_tb.tb_lineno]

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA("\t\tError : {}".format(e), Format=False, PDF=pdf)
            # new_session.close_session()
            return f"{e} \nError occured in line number {exc_tb.tb_lineno}"




    ###############################################################################
    ## Main Function
    ###############################################################################
    def test_Main_022(self):
        summary.append("Test Case M_CTC_ID_022 is under process...")
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
            time.sleep(2)
            ###############################################################################
            ## Perform call home to get ip_details
            ###############################################################################
            self.session, self.login_info = STARTUP.session_login(host = self.hostname,USER_N = self.USER_N,PSWRD = self.PSWRD)

            if self.session:
                self.RU_Details = STARTUP.demo(session = self.session,host= self.hostname, port= 830)
                for key, val in self.RU_Details[1].items():
                    if val[0] == 'true' and val[1] == 'true':
                        ###############################################################################
                        ## Test Description
                        ###############################################################################
                        Test_Desc = '''Test Description : This scenario is MANDATORY for an O-RU supporting the Hybrid M-plane architecture model.
This test validates that the O-RU correctly implements NETCONF Access Control user privileges.
The scenario corresponds to the following chapters in [3]:
3.4 NETCONF Access Control'''
                        CONFIDENTIAL = STARTUP.ADD_CONFIDENTIAL('22', SW_R=val[2])
                        STARTUP.STORE_DATA(CONFIDENTIAL, Format='CONF', PDF=pdf)
                        STARTUP.STORE_DATA(Test_Desc, Format='DESC', PDF=pdf)
                        pdf.add_page()


                
                self.new_user = genrate_username()
                self.new_pswrd = genrate_password()
                time.sleep(5)
                result = self.add_swm_user()
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
                
                
                    
                

        
def test_m_ctc_id_022():
    tc022_obj = M_CTC_ID_022()
    Check1 = tc022_obj.test_Main_022()
    if Check1 == False:
        STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
        STARTUP.STORE_DATA('SFP link not detected..',Format=False,PDF= pdf)
        STARTUP.ACT_RES(f"{'Access Control SWM (negative case)' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=[255,0,0])
        summary.append('FAIL_REASON : SFP link not detected...')
        summary.append(f"{'Access Control SWM (negative case)' : <50}{'=' : ^20}{'FAIL' : ^20}")
        return False
    try:
        if Check1 == True:
            Check2 = tc022_obj.test_procedure()
            ###############################################################################
            ## Expected/Actual Result
            ###############################################################################
            STARTUP.GET_SYSTEM_LOGS(tc022_obj.hostname,tc022_obj.USER_N,tc022_obj.PSWRD,pdf)
            Exp_Result = 'Expected Result : The NETCONF server replies rejecting the protocol operation with an "access-denied" error.'
            STARTUP.STORE_DATA(Exp_Result, Format='DESC', PDF=pdf)
            if Check2 == True:

                STARTUP.STORE_DATA('\t\t{}'.format('****************** Actual Result ******************'), Format=True, PDF=pdf)
                STARTUP.ACT_RES(f"{'Access Control SWM (negative case)' : <50}{'=' : ^20}{'SUCCESS' : ^20}",PDF= pdf,COL=[0,255,0])
                summary.append(f"{'Access Control SWM (negative case)' : <50}{'=' : ^20}{'PASS' : ^20}")
                return True
            
            else:
                if type(Check2) == list:
                    STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
                    Error_Info = '''ERROR\n\terror-type \t: \t{}\n\terror-tag \t: \t{}\n\terror-severity \t: \t{}\n\tmessage' \t: \t{}'''.format(*map(str,Check2))
                    STARTUP.STORE_DATA(Error_Info,Format=False,PDF= pdf)
                    STARTUP.ACT_RES(f"{'Access Control SWM (negative case)' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=[255,0,0])
                    summary.append("FAIL_REASON : {}".format(Error_Info))
                    summary.append(f"{'Access Control SWM (negative case)' : <50}{'=' : ^20}{'FAIL' : ^20}")
                    return False

                else:
                    STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
                    STARTUP.STORE_DATA(Check2,Format=False,PDF= pdf)
                    STARTUP.ACT_RES(f"{'Access Control SWM (negative case)' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=[255,0,0])
                    summary.append("FAIL_REASON : {}".format(Check2))
                    summary.append(f"{'Access Control SWM (negative case)' : <50}{'=' : ^20}{'FAIL' : ^20}")
                    return False
        else:
            if type(Check1) == list:
                STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
                Error_Info = '''ERROR\n\terror-type \t: \t{}\n\terror-tag \t: \t{}\n\terror-severity \t: \t{}\n\tmessage' \t: \t{}'''.format(*map(str,Check1))
                STARTUP.STORE_DATA(Error_Info,Format=False,PDF= pdf)
                STARTUP.ACT_RES(f"{'Access Control SWM (negative case)' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=[255,0,0])
                summary.append("FAIL_REASON : {}".format(Error_Info))
                summary.append(f"{'Access Control SWM (negative case)' : <50}{'=' : ^20}{'FAIL' : ^20}")
                return False

            else:
                STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
                STARTUP.STORE_DATA('{}'.format(Check1),Format=False,PDF= pdf)
                STARTUP.ACT_RES(f"{'Access Control SWM (negative case)' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=[255,0,0])
                summary.append("FAIL_REASON : {}".format(Check1))
                summary.append(f"{'Access Control SWM (negative case)' : <50}{'=' : ^20}{'FAIL' : ^20}")
                return False


    except Exception as e:
            STARTUP.STORE_DATA('{}'.format(e), Format=True,PDF=pdf)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
            summary.append("FAIL_REASON : {}".format(e))
            summary.append(f"{'Access Control SWM (negative case)' : <50}{'=' : ^20}{'FAIL' : ^20}")
            return False

    ###############################################################################
    ## For Capturing the logs
    ###############################################################################
    finally:
        STARTUP.CREATE_LOGS('M_CTC_ID_022',PDF=pdf)
        summary.append("Successfully completed Test Case M_CTC_ID_022. Logs captured !!") 
        notification('\n'.join(summary))


if __name__ == "__main__":
    start_time = time.time()
    test_m_ctc_id_022()
    end_time = time.time()
    print('Execution Time is : {}'.format(int(end_time-start_time)))
