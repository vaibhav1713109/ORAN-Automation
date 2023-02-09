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

class M_CTC_ID_018(vlan_Creation):
    # init method or constructor 
    def __init__(self):
        super().__init__()
        self.hostname, self.call_home_port = '',''
        self.USER_N = ''
        self.PSWRD = ''
        self.session = ''
        self.RU_Details = ''


    ###############################################################################
    ## Test Procedure
    ###############################################################################
    def test_procedure(self):
        ###############################################################################
        ## Test Procedure 1 : Connect to netopeer server
        ###############################################################################
        Test_Step1 = 'STEP 1. The TER NETCONF Client establishes a connection with the O-RU NETCONF Server.'
        STARTUP.STORE_DATA("{}".format(Test_Step1), Format='TEST_STEP', PDF=pdf)
        STARTUP.STORE_DATA('\n\n\t\t********** Connect to the NETCONF Server ***********\n\n',Format='TEST_STEP',PDF = pdf)
        STARTUP.STORE_DATA(self.login_info,Format=False,PDF = pdf)
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
        ## Initial Get Filter
        ###############################################################################
        pdf.add_page()
        u_name = '''
                <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <users xmlns="urn:o-ran:user-mgmt:1.0">	
                </users>
                </filter>
                '''

        user_name = self.session.get(u_name).data_xml
        STARTUP.STORE_DATA("######### Initial Get #########", Format=True, PDF=pdf)
        STARTUP.STORE_DATA("> get --filter-xpath /o-ran-usermgmt:users/user", Format=True, PDF=pdf)
        x = xml.dom.minidom.parseString(user_name)
        xml_pretty_str = x.toprettyxml()
        STARTUP.STORE_DATA(xml_pretty_str, Format='XML', PDF=pdf)

        ###############################################################################
        ## Test Procedure 2 : Configure 3 users
        ###############################################################################
        Test_Step2 = 'STEP 2. The TER NETCONF Client configures three new user accounts in addition to the default sudo account already present and passwords these three accounts using o-ran-user.mgmt.yang'
        STARTUP.STORE_DATA('{}'.format(Test_Step2),Format='TEST_STEP', PDF=pdf)

        ###############################################################################
        ## Genrate Random Username & Password with ORAN credential
        ###############################################################################    
        usrs = {}
        for i in range(1, 4):

            nam = genrate_username()
            pas = genrate_password()
            usrs[nam] = pas
        added_users = list(usrs.items())
        snippet = f"""
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
        summary.append('Mearging 3 new user!!')
        STARTUP.STORE_DATA('> edit-config  --target running --config --defop merge', Format=True, PDF=pdf)
        STARTUP.STORE_DATA('******* Replace with below xml ********', Format=True, PDF=pdf)
        STARTUP.STORE_DATA(snippet, Format='XML', PDF=pdf)
        data1 = self.session.edit_config(target="running", config=snippet)
        dict_data1 = xmltodict.parse(str(data1))
        STARTUP.STORE_DATA('''######### RPC Reply #########''', Format=True, PDF=pdf)
        if dict_data1['nc:rpc-reply']['nc:ok'] == None:
            STARTUP.STORE_DATA('\nOk\n', Format=False, PDF=pdf)

        ###############################################################################
        ## Check_Notifications
        ############################################################################### 
        while True:
            n = self.session.take_notification(timeout=5)
            if n == None:
                break
            notify = n.notification_xml
            dict_n = xmltodict.parse(str(notify))
            try:
                sid = dict_n['notification']['netconf-config-change']['changed-by']['session-id']
                # STARTUP.STORE_DATA(sid,OUTPUT_LIST=OUTPUT_LIST)
                if sid == self.session.session_id:
                    STARTUP.STORE_DATA(" ############# NOTIFICATIONS #############", Format=True, PDF=pdf)
                    x = xml.dom.minidom.parseString(notify)
                    xml_pretty_str = x.toprettyxml()
                    STARTUP.STORE_DATA(xml_pretty_str, Format='XML', PDF=pdf)
                    break
            except:
                pass
        summary.append('Configuraion chenged notification captured!!')

        ###############################################################################
        ## Test Procedure 3 : Give Configured 3 users diffrent privilege
        ###############################################################################
        summary.append('Configured users privilege for above 3 users!!')
        pdf.add_page()
        Test_Step3 = '''######### STEP 3. The TER NETCONF Client configures user account to group mappings for the three
        new accounts using ietf-netconf-acm.yang respectively one with "nms", one with "fm-pm" and one 
        with "swm" privilege. #########'''
        STARTUP.STORE_DATA('{}'.format(Test_Step3),Format='TEST_STEP', PDF=pdf)
        STARTUP.STORE_DATA('> edit-config  --target running --config --defop merge', Format=True, PDF=pdf)
        STARTUP.STORE_DATA('******* Replace with below xml ********', Format=True, PDF=pdf)

        add_fm = f'<user-name>{added_users[0][0]}</user-name>'
        add_nms = f'<user-name>{added_users[1][0]}</user-name>'
        add_swm = f'<user-name>{added_users[2][0]}</user-name>'

        nacm_file = open('{}/require/Yang_xml/M_CTC_ID_18.xml'.format(parent)).read()
        nacm_file = nacm_file.format(add_swm=add_swm, add_fm=add_fm, add_nms=add_nms)
        STARTUP.STORE_DATA(nacm_file, Format='XML', PDF=pdf)
        data2 = self.session.edit_config(target="running", config=nacm_file, default_operation='merge')
        dict_data2 = xmltodict.parse(str(data2))

        ###############################################################################
        ## Test Procedure 4 : Check the RPC Reply
        ###############################################################################
        Test_Step4 = 'STEP 4. The O-RU NETCONF Server confirms the operations for the above transactions.'
        STARTUP.STORE_DATA(
            '{}'.format(Test_Step4), Format='TEST_STEP', PDF=pdf)
        if dict_data2['nc:rpc-reply']['nc:ok'] == None:
            STARTUP.STORE_DATA('\nOk\n', Format=False, PDF=pdf)


        ###############################################################################
        ## Check_Notifications
        ############################################################################### 
        summary.append('Configuraion chenged notification captured!!')
        while True:
            n = self.session.take_notification(timeout=30)
            if n == None:
                break
            notify = n.notification_xml
            dict_n = xmltodict.parse(str(notify))
            try:
                sid = dict_n['notification']['netconf-config-change']['changed-by']['session-id']
                if sid == self.session.session_id:
                    STARTUP.STORE_DATA(" ############# NOTIFICATIONS #############", Format=True, PDF=pdf)
                    x = xml.dom.minidom.parseString(notify)
                    xml_pretty_str = x.toprettyxml()
                    STARTUP.STORE_DATA(
                        xml_pretty_str, Format='XML', PDF=pdf)
                    break
            except:
                pass

        ###############################################################################
        ## Post Get Filter of NACM
        ###############################################################################
        STARTUP.STORE_DATA("> get --filter-xpath /ietf-netconf-acm:nacm/groups", Format=True, PDF=pdf)
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


        ###############################################################################
        ## Check whether users add in nacm or not
        ###############################################################################
        ADDED_USERS = list(usrs.keys())
        group_n = xmltodict.parse(str(user_name))
        group_name = group_n['data']['nacm']['groups']['group']
        j = 0
        for i in group_name:
            if i['name'] == 'sudo':
                pass
            elif i['name'] in ['fm-pm', 'nms', 'swm']:
                if ADDED_USERS[j] not in i['user-name']:
                    STARTUP.STORE_DATA(
                        xml_pretty_str, Format='XML', PDF=pdf)
                    return f"User didn't merge in {i['name']} privilege"
                j += 1
                added_users[True]
            else:
                STARTUP.STORE_DATA(xml_pretty_str, Format='XML', PDF=pdf)
                return "User didn't merge in except these privilege ['sudo', 'fm-pm', 'nms', 'swm'] privilege"

        STARTUP.STORE_DATA(xml_pretty_str, Format='XML', PDF=pdf)
        
        

        ###############################################################################
        ## Test Procedure 4 : Post Get Filter of USERS
        ###############################################################################  
        Test_Step5 = 'STEP 5. The TER NETCONF Client retrieves a list of users from O-RU NETCONF Server. The newly created user accounts and mappings are validated.'
        STARTUP.STORE_DATA(
            '{}'.format(Test_Step5), Format='TEST_STEP', PDF=pdf)
        u_name = '''
                <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <users xmlns="urn:o-ran:user-mgmt:1.0">	
                </users>
                </filter>
                '''
        user_name = self.session.get_config('running', u_name).data_xml

        STARTUP.STORE_DATA("> get --filter-xpath /o-ran-usermgmt:users/user", Format=True, PDF=pdf)
        s = xml.dom.minidom.parseString(user_name)
        xml_pretty_str = s.toprettyxml()


        ###############################################################################
        ## Test Procedure 4 : Check whether users are merge
        ###############################################################################  
        user_n = xmltodict.parse(str(user_name))
        USERs_info = user_n['data']['users']['user']
        ADDED_USERS_R = ADDED_USERS[::-1]  # Reeverse of added_users
        LIST_User = []
        for _ in range(3):
            user1 = USERs_info.pop()
            LIST_User.append(user1['name'])

        if LIST_User != ADDED_USERS_R:
            STARTUP.STORE_DATA(xml_pretty_str, Format='XML', PDF=pdf)
            return "Users didn't merge..."
        else:
            STARTUP.STORE_DATA(xml_pretty_str, Format='XML', PDF=pdf)
        summary.append('All 3 user merged and got privileges successfully!!')

        return True

        
    ###############################################################################
    ## Main Function
    ###############################################################################
    def test_Main_018(self):
        summary.append("Test Case M_CTC_ID_018 is under process...")
        Check1 = self.linked_detected()
        
        
        ###############################################################################
        ## Read User Name and password from Config.INI of Config.py
        ############################################################################### 
        self.USER_N = configur.get('INFO','sudo_user')
        self.PSWRD = configur.get('INFO','sudo_pass')
        if Check1 == False or Check1 == None:
            return Check1

        sniff(iface = self.interface, stop_filter = self.check_tcp_ip,timeout = 100)
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
                        This test validates that user management model can be used to add users to the O-RU
                        This scenario corresponds to the following chapters in [3]:
                        3.3 SSH Connection Establishment
                        3.4 NETCONF Access Control'''
                        CONFIDENTIAL = STARTUP.ADD_CONFIDENTIAL('18', SW_R=val[2])
                        STARTUP.STORE_DATA(CONFIDENTIAL, Format='CONF', PDF=pdf)
                        STARTUP.STORE_DATA(Test_Desc, Format='DESC', PDF=pdf)
                        pdf.add_page()
            


                result = self.test_procedure()
                time.sleep(5)
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



        

def test_m_ctc_id_018():
    tc018_obj = M_CTC_ID_018()
    Check = tc018_obj.test_Main_018()
    if Check == False:
        STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
        STARTUP.STORE_DATA('SFP link not detected...',Format=False,PDF= pdf)
        STARTUP.ACT_RES(f"{'Sudo on Hybrid M-plane Architecture (positive case)' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(255,0,0))
        summary.append('FAIL_REASON : SFP link not detected...')
        summary.append(f"{'Sudo on Hybrid M-plane Architecture (positive case)' : <50}{'=' : ^20}{'FAIL' : ^20}")
        return False
    
    ###############################################################################
    ## Expected/Actual Result
    ###############################################################################
    STARTUP.GET_SYSTEM_LOGS(tc018_obj.hostname,tc018_obj.USER_N,tc018_obj.PSWRD,pdf)
    Exp_Result = 'Expected Result : The TER NETCONF Client retrieves a list of users from O-RU NETCONF Server. The newly created user accounts and mappings are validated.'
    STARTUP.STORE_DATA(Exp_Result, Format='DESC', PDF=pdf)

    STARTUP.STORE_DATA('\t\t{}'.format('****************** Actual Result ******************'), Format=True, PDF=pdf)
    try:
        if Check == True:
            STARTUP.ACT_RES(f"{'Sudo on Hybrid M-plane Architecture (positive case)' : <50}{'=' : ^20}{'SUCCESS' : ^20}",PDF= pdf,COL=(0,255,0))
            summary.append(f"{'Sudo on Hybrid M-plane Architecture (positive case)' : <50}{'=' : ^20}{'PASS' : ^20}")
            return True

        elif type(Check) == list:
            STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
            Error_Info = '''ERROR\n\terror-type \t: \t{}\n\terror-tag \t: \t{}\n\terror-severity \t: \t{}\n\tmessage' \t: \t{}'''.format(*map(str,Check))
            STARTUP.STORE_DATA(Error_Info,Format=False,PDF= pdf)
            STARTUP.ACT_RES(f"{'Sudo on Hybrid M-plane Architecture (positive case)' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(255,0,0))
            summary.append("FAIL_REASON : {}".format(Error_Info))
            summary.append(f"{'Sudo on Hybrid M-plane Architecture (positive case)' : <50}{'=' : ^20}{'FAIL' : ^20}")
            return False
        else:
            STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
            STARTUP.STORE_DATA('{}'.format(Check),Format=False,PDF= pdf)
            STARTUP.ACT_RES(f"{'Sudo on Hybrid M-plane Architecture (positive case)' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(255,0,0))
            summary.append("FAIL_REASON : {}".format(Check))
            summary.append(f"{'Sudo on Hybrid M-plane Architecture (positive case)' : <50}{'=' : ^20}{'FAIL' : ^20}")
            return False


    except Exception as e:
            STARTUP.STORE_DATA('{}'.format(e), Format=True,PDF=pdf)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
            summary.append("FAIL_REASON : {}".format(e))
            summary.append(f"{'Sudo on Hybrid M-plane Architecture (positive case)' : <50}{'=' : ^20}{'FAIL' : ^20}")
            return False

    ###############################################################################
    ## For Capturing the logs
    ###############################################################################
    finally:
        STARTUP.CREATE_LOGS('M_CTC_ID_018',PDF=pdf)
        summary.append("Successfully completed Test Case M_CTC_ID_018. Logs captured !!") 
        notification('\n'.join(summary))


if __name__ == "__main__":
    start_time = time.time()
    test_m_ctc_id_018()
    end_time = time.time()
    print('Execution Time is : {}'.format(int(end_time-start_time)))
    pass

