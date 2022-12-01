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

class M_CTC_ID_020(vlan_Creation):
    # init method or constructor 
    def __init__(self):
        super().__init__()
        self.hostname, self.call_home_port = '',''
        self.USER_SUDO = ''
        self.PSWRD_SUDO = ''
        self.USER_N = ''
        self.PSWRD = ''
        self.new_user = ''
        self.new_pswrd = ''
        self.session = ''
        self.RU_Details = ''


    ###############################################################################
    ## Login with sudo user for getting user details
    ###############################################################################
    def FETCH_DATA(self):
        # Fetching all the interface
        with manager.connect(host=self.hostname, port=830, username=self.USER_SUDO, hostkey_verify=False, password=self.PSWRD_SUDO, allow_agent=False, look_for_keys=False) as session:
            u_name = '''
            <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <users xmlns="urn:o-ran:user-mgmt:1.0">	
                </users>
            </filter>'''

            get_u = session.get(u_name).data_xml
            dict_u = xmltodict.parse(str(get_u))
            # STARTUP.STORE_DATA(user_name,OUTPUT_LIST=OUTPUT_LIST)
            s = xml.dom.minidom.parseString(get_u)
            #xml = xml.dom.minidom.parseString(user_name)

            xml_pretty_str = s.toprettyxml()
            # session.close_session()
            return xml_pretty_str


    ###############################################################################
    ## Test Procedure
    ###############################################################################
    def test_procedure(self):
        ###############################################################################
        ## Test Procedure 1 : Connect to netopeer server with NMS user
        ###############################################################################
        STARTUP.STORE_DATA(
            '\t\t********** Connect to the NETCONF Server ***********', Format='TEST_STEP', PDF=pdf)
        
        Test_Step1 = 'STEP 1 TER NETCONF client establishes a connection using a user account with nms privileges.'
        STARTUP.STORE_DATA('\n\n\t\t********** Connect to the NETCONF Server ***********\n\n',Format='TEST_STEP',PDF = pdf)
        STARTUP.STORE_DATA(self.login_info,Format=False,PDF = pdf)
        STATUS = STARTUP.STATUS(self.hostname,self.USER_N,self.session.session_id,830)
        STARTUP.STORE_DATA(STATUS,Format=False,PDF = pdf)


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
        ## Test Procedure 2 : Configure new user\password.
        ###############################################################################
        pdf.add_page()
        Test_Step2 = 'Step 2 TER NETCONF client attempts to configure a new user/password.'
        STARTUP.STORE_DATA('{}'.format(Test_Step2), Format='TEST_STEP', PDF=pdf)
        STARTUP.STORE_DATA('> edit-config  --target running --config --defop merge', Format=True, PDF=pdf)
        STARTUP.STORE_DATA('******* Replace with below xml ********', Format=True, PDF=pdf)
        notification("Netconf Session Established")

        ###############################################################################
        ## Merge New User
        ###############################################################################
        snip = f"""
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

        STARTUP.STORE_DATA(snip, Format='XML', PDF=pdf)
        try:
            data3 = self.session.edit_config(
                target="running", config=snip, default_operation='merge')
            dict_data1 = xmltodict.parse(str(data3))
            STARTUP.STORE_DATA('''######### RPC Reply #########''', Format=True, PDF=pdf)
            if dict_data1['nc:rpc-reply']['nc:ok'] == None:
                return data3, 'Addition of new is complete...'

        ###############################################################################
        ## Check Access Denied
        ###############################################################################
        except RPCError as e:
            if e.tag == 'access-denied':
                Test_Step3 = 'Step 3 NETCONF server replies rejecting the protocol operation with an \'access-denied\' error'
                STARTUP.STORE_DATA('{}'.format(Test_Step3), Format='TEST_STEP', PDF=pdf)
                STARTUP.STORE_DATA('ERROR\n', Format=False, PDF=pdf)
                STARTUP.STORE_DATA(
                    f"{'type' : ^20}{':' : ^10}{e.type: ^10}\n", Format=False, PDF=pdf)
                STARTUP.STORE_DATA(
                    f"{'tag' : ^20}{':' : ^10}{e.tag: ^10}\n", Format=False, PDF=pdf)
                STARTUP.STORE_DATA(
                    f"{'severity' : ^20}{':' : ^10}{e.severity: ^10}\n", Format=False, PDF=pdf)
                STARTUP.STORE_DATA(
                    f"{'path' : ^20}{':' : ^10}{e.path: ^10}\n", Format=False, PDF=pdf)
                STARTUP.STORE_DATA(
                    f"{'message' : ^20}{':' : ^10}{e.message: ^10}\n", Format=False, PDF=pdf)
                return True
            else:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                return [e.type, e.tag, e.severity, e.message, exc_tb.tb_lineno]


    ###############################################################################
    ## Main Function
    ###############################################################################
    def test_Main_020(self):
        
        Check1 = self.linked_detected()
        
        
        ###############################################################################
        ## Read User Name and password from Config.INI of Config.py
        ############################################################################### 
        self.new_user = genrate_username()
        self.new_pswrd = genrate_password()
        self.USER_N = configur.get('INFO','nms_user')
        self.PSWRD = configur.get('INFO','nms_pass')
        self.USER_SUDO = configur.get('INFO','sudo_user')
        self.PSWRD_SUDO = configur.get('INFO','sudo_pass')
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
                        CONFIDENTIAL = STARTUP.ADD_CONFIDENTIAL('20', SW_R=val[2])
                        STARTUP.STORE_DATA(CONFIDENTIAL, Format='CONF', PDF=pdf)
                        STARTUP.STORE_DATA(Test_Desc, Format='DESC', PDF=pdf)
                        pdf.add_page()

                ###############################################################################
                ## Initial Get Filter
                ###############################################################################
                STARTUP.STORE_DATA('********** Initial Get ***********', Format='TEST_STEP',PDF=pdf)
                STARTUP.STORE_DATA(f'''> connect --ssh --host {self.hostname} --port 830 --login {self.USER_SUDO}
                        Interactive SSH Authentication
                        Type your password:
                        Password: 
                        ''', Format=False,PDF=pdf)
                STARTUP.STORE_DATA("> get --filter-xpath /o-ran-usermgmt:users/user", Format=True,PDF=pdf)
                get_filter = self.FETCH_DATA()
                STARTUP.STORE_DATA(get_filter, Format='XML',PDF=pdf)
                pdf.add_page()
                
                time.sleep(5)
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


def test_m_ctc_id_020():
    tc020_obj = M_CTC_ID_020()
    Check = tc020_obj.test_Main_020()
    if Check == False:
        STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
        STARTUP.STORE_DATA('SFP link not detected...',Format=False,PDF= pdf)
        STARTUP.ACT_RES(f"{'Access Control NMS (negative case)' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(255,0,0))
        return False
    ###############################################################################
    ## Expected/Actual Result
    ###############################################################################
    STARTUP.GET_SYSTEM_LOGS(tc020_obj.hostname,tc020_obj.USER_N,tc020_obj.PSWRD,pdf)
    Exp_Result = 'Expected Result : The NETCONF server replies rejecting the protocol operation with an "access-denied" error.'
    STARTUP.STORE_DATA(Exp_Result, Format='DESC', PDF=pdf)

    STARTUP.STORE_DATA('\t\t{}'.format('****************** Actual Result ******************'), Format=True, PDF=pdf)
    try:
        if Check == True:
            STARTUP.ACT_RES(f"{'Access Control NMS (negative case)' : <50}{'=' : ^20}{'SUCCESS' : ^20}",PDF= pdf,COL=(0,255,0))
            return True

        elif type(Check) == list:
            STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
            Error_Info = '''ERROR\n\terror-type \t: \t{}\n\terror-tag \t: \t{}\n\terror-severity \t: \t{}\n\tmessage' \t: \t{}'''.format(*map(str,Check))
            STARTUP.STORE_DATA(Error_Info,Format=False,PDF= pdf)
            STARTUP.ACT_RES(f"{'Access Control NMS (negative case)' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(255,0,0))
            return False
        else:
            STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
            STARTUP.STORE_DATA('{}'.format(Check),Format=False,PDF= pdf)
            STARTUP.ACT_RES(f"{'Access Control NMS (negative case)' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(255,0,0))
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
        STARTUP.CREATE_LOGS('M_CTC_ID_020',PDF=pdf)
        notification("M_CTC_ID_020 is finished!")  

if __name__ == "__main__":
    test_m_ctc_id_020()
    pass
