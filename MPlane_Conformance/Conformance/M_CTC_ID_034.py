###############################################################################
##@ FILE NAME:      M_CTC_ID_034
##@ TEST SCOPE:     M PLANE O-RAN CONFORMANCE
##@ Version:        V_1.0.0
##@ Support:        @Ramiyer, @VaibhavDhiman, @PriyaSharma
###############################################################################

###############################################################################
## Package Imports 
###############################################################################

import sys, os, time, xmltodict, xml.dom.minidom, subprocess, socket
from ncclient import manager
from ncclient.operations.rpc import RPC, RPCError
from ncclient.transport import errors
from paramiko.ssh_exception import NoValidConnectionsError
from ncclient.operations.errors import TimeoutExpiredError
from ncclient.transport.errors import SessionCloseError
from ncclient.xml_ import to_ele


###############################################################################
## Directory Path
###############################################################################
dir_name = os.path.dirname(os.path.abspath(__file__))
parent = os.path.dirname(dir_name)
# print(parent)
sys.path.append(parent)

###############################################################################
## Related Imports
###############################################################################
from require import STARTUP, Config

###############################################################################
## Initiate PDF
###############################################################################
pdf = STARTUP.PDF_CAP()

class M_CTC_ID_034():
    # init method or constructor 
    def __init__(self):
        self.hostname, self.call_home_port = '',''
        self.USER_N = ''
        self.PSWRD = ''
        self.session = ''
        self.rmt = ''
        self.du_pswrd = ''
        self.RU_Details = ''

    ###############################################################################
    ## Test Procedure
    ###############################################################################
    def test_procedure(self):
        STARTUP.STORE_DATA('\n\n\t\t********** Connect to the NETCONF Server ***********\n\n',Format='TEST_STEP',PDF = pdf)
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
        ## Test Procedure 1 : Send troubleshooting RPC.
        ###############################################################################
        pdf.add_page()
        Test_Step1 = '\t\tStep 1 : TER NETCONF Client sends <rpc><start-troubleshooting-logs> to the O-RU NETCONF Server'
        STARTUP.STORE_DATA('{}'.format(Test_Step1), Format='TEST_STEP',PDF=pdf)
        xml_data = open("{}/require/Yang_xml/troubleshooting_start.xml".format(parent)).read()
        STARTUP.STORE_DATA('\n> user-rpc\n', Format=True,PDF=pdf)
        
        STARTUP.STORE_DATA('\t\t******* Replace with below xml ********', Format=True,PDF=pdf)
        STARTUP.STORE_DATA(xml_data, Format='XML',PDF=pdf)
        rpc_command = to_ele(xml_data)
        d = self.session.rpc(rpc_command)

        STARTUP.STORE_DATA('******* RPC Reply ********',Format=True,PDF=pdf)
        STARTUP.STORE_DATA('{}'.format(d), Format='XML',PDF=pdf)

        ###############################################################################
        ## Test Procedure 2 : Capture_The_Notifications
        ###############################################################################
        Test_Step2 = '\t\tStep 2 : O-RU NETCONF Server starts generating one or more file(s) containing troubleshooting logs  and send <notification><troubleshooting-log-generated>'
        STARTUP.STORE_DATA('{}'.format(Test_Step2), Format='TEST_STEP',PDF=pdf)
        timeout = time.time() + 60
        while time.time() < timeout:
            n = self.session.take_notification()
            notify = n.notification_xml
            dict_n = xmltodict.parse(str(notify))
            
            try:
                notf = dict_n['notification']['troubleshooting-log-generated']
                file_name = dict_n['notification']['troubleshooting-log-generated']['log-file-name']
                if notf:
                    x = xml.dom.minidom.parseString(notify)
                    xml_pretty_str = x.toprettyxml()

                    print(xml_pretty_str)
                    print('-'*100)
                    break
            
            except:
                pass

        ###############################################################################
        ## Fetch Public Key of Linux PC
        ###############################################################################
        pub_k = subprocess.getoutput('cat /etc/ssh/ssh_host_rsa_key.pub')
        pk = pub_k.split()
        pub_key = pk[1]

        xml_data1 = open("{}/require/Yang_xml/TC_34.xml".format(parent)).read()
        xml_data = xml_data1.format(rmt_path=self.rmt,password=self.du_pswrd,pub_key= pub_key,t_logs = file_name)

        ###############################################################################
        ## Test Procedure 3 : Configure fileupload RPC
        ###############################################################################
        Test_Step3 = '\t\tStep 3 : Configuring File upload rpc toward Netconf'
        STARTUP.STORE_DATA('{}'.format(Test_Step3), Format='TEST_STEP',PDF=pdf)
        STARTUP.STORE_DATA('\n> user-rpc\n', Format=True,PDF=pdf)


        STARTUP.STORE_DATA('\t\t******* Replace with below xml ********', Format=True,PDF=pdf)
        STARTUP.STORE_DATA(xml_data1, Format='XML',PDF=pdf)
        rpc_command = to_ele(xml_data1)
        rpc2 = self.session.rpc(rpc_command)

        STARTUP.STORE_DATA('******* RPC Reply ********',Format=True,PDF=pdf)
        STARTUP.STORE_DATA('{}'.format(rpc2), Format='XML',PDF=pdf)
        ###############################################################################
        ## Test Procedure 4 : Capture fileupload Notification
        ###############################################################################
        Test_Step4 = '\t\tStep 4 : When file upload is completed, the O-RU NETCONF Server sends <notification><upload-notification> with status SUCCESS.'
        STARTUP.STORE_DATA('{}'.format(Test_Step4), Format='TEST_STEP',PDF=pdf)
        timeout = time.time() + 30
        while time.time() < timeout:
        
            n = self.session.take_notification()
            notify = n.notification_xml
            dict_n = xmltodict.parse(str(notify))
            try:
                notf = dict_n['notification']['file-upload-notification']
                if notf:
                    x = xml.dom.minidom.parseString(notify)
                    #xml = xml.dom.minidom.parseString(user_name)

                    xml_pretty_str = x.toprettyxml()

                    print(xml_pretty_str)
                    print('-'*100)
                    status = dict_n['notification']['file-upload-notification']['status']
                    if status != 'SUCCESS':
                        return f'File-upload-status {status}'
                    break
                
            except:
                pass
                



    ###############################################################################
    ## Main Function
    ###############################################################################
    def test_Main_034(self):
        Check1 = STARTUP.sfp_Linked()
        

        ###############################################################################
        ## Read User Name and password from Config.INI of Config.py
        ###############################################################################
        self.rmt = Config.details['remote_path']
        self.du_pswrd = Config.details['DU_PASS'] 
        self.USER_N = Config.details['SUDO_USER'] 
        self.PSWRD = Config.details['SUDO_PASS']
        if Check1 != True:
            return Check1
        
        try:
            ###############################################################################
            ## Perform call home to get ip_details
            ###############################################################################
            self.session = manager.call_home(host = '0.0.0.0', port=4334, hostkey_verify=False,username = self.USER_N, password = self.PSWRD,timeout = 60,allow_agent = False , look_for_keys = False)
            self.hostname, self.call_home_port = self.session._session._transport.sock.getpeername()   #['ip_address', 'TCP_Port']
            
            if self.session:
                self.RU_Details = STARTUP.demo(session = self.session,host= self.hostname, port= 830)
                for key, val in self.RU_Details[1].items():
                    if val[0] == 'true' and val[1] == 'true':
                        ###############################################################################
                        ## Test Description
                        ###############################################################################
                        Test_Desc = 'Test Description :  This test validates that the O-RU can successfully perform a troubleshooting log genration and file upload procedure.'
                        CONFIDENTIAL = STARTUP.ADD_CONFIDENTIAL('34',SW_R = val[2]) 
                        STARTUP.STORE_DATA(CONFIDENTIAL,Format='CONF',PDF= pdf)
                        STARTUP.STORE_DATA(Test_Desc,Format='DESC',PDF= pdf)
                        pdf.add_page()
                
                result = self.test_procedure()
                time.sleep(5)
                self.session.close_session()
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
            print(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
            self.session.close_session()
            return [e.type, e.tag, e.severity, e.path, e.message, exc_tb.tb_lineno]

        except Exception as e:
            STARTUP.STORE_DATA('{}'.format(e), Format=True,PDF=pdf)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
            # self.session.close_session()
            return e 

        
def test_m_ctc_id_034():
    tc034_obj = M_CTC_ID_034()
    Check = tc034_obj.test_Main_034()
    if Check == False:
        STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
        STARTUP.STORE_DATA('SFP link not detected...',Format=False,PDF= pdf)
        STARTUP.ACT_RES(f"{'O-RU troubleshoot log genration and file upload' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(0,255,0))
        return False
    ###############################################################################
    ## Expected/Actual Result
    ###############################################################################
    STARTUP.GET_SYSTEM_LOGS(tc034_obj.hostname,tc034_obj.USER_N,tc034_obj.PSWRD,pdf)
    Exp_Result = 'Expected Result : The O-RU NETCONF Server sends <notification><file-upload><status> to the TER NETCONF Client. Field <status> contains the value COMPLETED to indicate the successful upload of file to the desired location.'
    STARTUP.STORE_DATA(Exp_Result,Format='DESC',PDF= pdf)

    STARTUP.STORE_DATA('\t\t{}'.format('****************** Actual Result ******************'),Format=True,PDF= pdf)
    try:
        if Check == True:
            STARTUP.ACT_RES(f"{'O-RU troubleshoot log genration and file upload' : <50}{'=' : ^20}{'SUCCESS' : ^20}",PDF= pdf,COL=(0,255,0))
            return True

        elif type(Check) == list:
            STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
            Error_Info = '''ERROR\n\terror-type \t: \t{}\n\terror-tag \t: \t{}\n\terror-severity \t: \t{}\n\tmessage' \t: \t{}'''.format(*map(str,Check))
            STARTUP.STORE_DATA(Error_Info,Format=False,PDF= pdf)
            STARTUP.ACT_RES(f"{'O-RU troubleshoot log genration and file upload' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(0,255,0))
            return False
        else:
            STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
            STARTUP.STORE_DATA('{}'.format(Check),Format=False,PDF= pdf)
            STARTUP.ACT_RES(f"{'O-RU troubleshoot log genration and file upload' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(0,255,0))
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
        STARTUP.CREATE_LOGS('M_CTC_ID_034',PDF=pdf)


if __name__ == "__main__":
    test_m_ctc_id_034()
    pass