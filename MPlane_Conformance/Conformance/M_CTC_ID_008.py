###############################################################################
##@ FILE NAME:      M_CTC_ID_008
##@ TEST SCOPE:     M PLANE O-RAN CONFORMANCE
##@ Version:        V_1.0.0
##@ Support:        @Ramiyer, @VaibhavDhiman, @PriyaSharma
###############################################################################

###############################################################################
## Package Imports 
###############################################################################


from distutils import errors
from random import randint
import socket, os, sys, lxml.etree, time, xmltodict, xml.dom.minidom, paramiko
from ncclient import manager
from ncclient.operations.rpc import RPCError
from ncclient.transport import errors
from ncclient.xml_ import to_ele
from paramiko.ssh_exception import NoValidConnectionsError
from ncclient.operations.errors import TimeoutExpiredError
from ncclient.transport.errors import SessionCloseError
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
from require import STARTUP, Config
from require.Vlan_Creation import *

###############################################################################
## Initiate PDF
###############################################################################
pdf = STARTUP.PDF_CAP()
summary = []

class M_CTC_ID_008(vlan_Creation):
    def __init__(self) -> None:
        super().__init__()
        self.interface_name = ''
        self.hostname, self.call_home_port = '',''
        self.USER_N = ''
        self.PSWRD = ''
        self.session = ''
        self.s_n_i = randint(10,15)
        self.g_t = randint(10,12)
            
    ###############################################################################
    ## SFP Link Detection
    ###############################################################################
    def sfp_Linked(self):
        ## Check Point 1
        Check1 = True
        self.interface_name = self.linked_detected()
        if self.interface_name:
            print('SFP Link is Detected...')
        else:
            print('SFP Link is Detected...')
            Check1 = False
        return Check1

    ###############################################################################
    ## Check Ping and DHCP Status
    ###############################################################################
    def ping_status(self, ip_address):
        response = os.system("ping -c 5 " + ip_address)
        # self.ping = subprocess.getoutput(f'ping {ip_address} -c 5')
        return response

    ###############################################################################
    ## Test Procedure
    ###############################################################################
    def test_procedure(self):
        STARTUP.STORE_DATA('\n\n\t\t********** Connect to the NETCONF Server ***********\n\n',Format='TEST_STEP',PDF = pdf)
        STATUS = STARTUP.STATUS(self.hostname,self.USER_N,self.session.session_id,830)
        STARTUP.STORE_DATA(self.login_info,Format=False,PDF = pdf)
        STARTUP.STORE_DATA(STATUS,Format=False,PDF = pdf)
        summary.append('Netconf Session Established!!')


        ###############################################################################
        ## Server Capabilities
        ###############################################################################
        for cap in self.session.server_capabilities:
            STARTUP.STORE_DATA("\t{}".format(cap),Format=False,PDF = pdf)
        summary.append('Hello Capabilities Exchanged!!')

        pdf.add_page()
        ###############################################################################
        ## Test Procedure 1
        ###############################################################################
        Test_Step1 = '\t\t***********step 1 and 2 Retrival of ru information with filter **********'
        STARTUP.STORE_DATA('{}'.format(Test_Step1),Format='TEST_STEP',PDF = pdf)

        
        ###############################################################################
        ## Create_subscription
        ###############################################################################
        sub = """<create-subscription xmlns="urn:ietf:params:xml:ns:netconf:notification:1.0">
                    <filter type="subtree">
                            <supervision-notification xmlns="urn:o-ran:supervision:1.0"></supervision-notification>                            
                    </filter>
                </create-subscription>
        """
        cap = self.session.dispatch(to_ele(sub))
        
        STARTUP.STORE_DATA('> subscribe', Format=True, PDF=pdf)
        dict_data = xmltodict.parse(str(cap))
        if dict_data['nc:rpc-reply']['nc:ok'] == None:
            STARTUP.STORE_DATA('\nOk\n', Format=False, PDF=pdf)
        summary.append('Subscription with supervision filter Performed!!')
        
        
        ###############################################################################
        ## Append Changes in XML
        ###############################################################################
        summary.append('Configure Supervision RPC!!')
        xml_data = open("{}/require/Yang_xml/supervision.xml".format(parent)).read()
        xml_data = xml_data.format(super_n_i= self.s_n_i, guard_t_o= self.g_t)
        Test_Step1 = '\t\t TER NETCONF Client responds with <rpc supervision-watchdog-reset></rpc> to the O-RU NETCONF Server'
        STARTUP.STORE_DATA('{}'.format(Test_Step1),Format='TEST_STEP', PDF=pdf)
        STARTUP.STORE_DATA('> user-rpc',Format=True, PDF=pdf)
        STARTUP.STORE_DATA('******* Replace with below xml ********',Format=True, PDF=pdf)
        STARTUP.STORE_DATA(xml_data,Format='XML', PDF=pdf)


        d = self.session.dispatch(to_ele(xml_data))
        Test_Step2 = '\t\t O-RU NETCONF Server sends a reply to the TER NETCONF Client <rpc-reply><next-update-at>date-time</next-update-at></rpc-reply>'
        STARTUP.STORE_DATA('{}'.format(Test_Step2),Format='TEST_STEP', PDF=pdf)
        STARTUP.STORE_DATA('{}'.format(d),Format='XML', PDF=pdf)
        t = int(self.s_n_i) + ((int(self.g_t))/3)

        ###############################################################################
        ## Iterating 30 Times
        ###############################################################################
        STARTUP.STORE_DATA('\t\t******** Looped for 30 iterations ***********',Format=True, PDF=pdf)
        for i in range(1,31,1):
        # for i in range(1,5,1):
            STARTUP.STORE_DATA("{}th iteration".format(i),Format=True, PDF=pdf)
            d1 = self.session.dispatch(to_ele(xml_data))
            STARTUP.STORE_DATA('{}'.format(d1),Format='XML', PDF=pdf)
            dict_data = xmltodict.parse(str(d1))
            
            # next_up_time = dict_data['nc:rpc-reply']['next-update-at']['#text']
            # STARTUP.STORE_DATA(next_up_time,OUTPUT_LIST=OUTPUT_LIST)
            time.sleep(t)
        summary.append('All 30 iteration completed!!')
        return True

    ###############################################################################
    ## Main Function
    ###############################################################################
    def test_Main(self):
        summary.append("Test Case M_CTC_ID_008 is under process...")
        Check1 = self.linked_detected()
        
        if Check1 == False or Check1 == None:
            return Check1

        sniff(iface = self.interface, stop_filter = self.check_tcp_ip, timeout = 100)
        ###############################################################################
        ## Read User Name and password from Config.INI of Config.py
        ###############################################################################
        self.USER_N = configur.get('INFO','sudo_user')
        self.PSWRD = configur.get('INFO','sudo_pass')
        try:
            STARTUP.delete_system_log(host= self.hostname)
            time.sleep(2)
            ###############################################################################
            ## Perform call home to get ip_details
            ###############################################################################
            self.session, self.login_info = STARTUP.session_login(host = self.hostname,USER_N = self.USER_N,PSWRD = self.PSWRD)

            if self.session:
                RU_Details = STARTUP.demo(session = self.session,host= self.hostname, port= 830)
                
                for key, val in RU_Details[1].items():
                    if val[0] == 'true' and val[1] == 'true':
                        ###############################################################################
                        ## Test Description
                        ###############################################################################
                        Test_Desc = 'Test Description : This test validates that the O-RU manages the connection supervision process correctly.'
                        CONFIDENTIAL = STARTUP.ADD_CONFIDENTIAL('08',SW_R = val[2]) 
                        STARTUP.STORE_DATA(CONFIDENTIAL,Format='CONF',PDF= pdf)
                        STARTUP.STORE_DATA(Test_Desc,Format='DESC',PDF= pdf)
                        pdf.add_page()
                
                
                
                time.sleep(5)
                result = self.test_procedure()
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

def test_M_ctc_id_008():
    tc008_obj = M_CTC_ID_008()
    Check = tc008_obj.test_Main() 
    # print(type(Check), Check)
    if Check == False:
        STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
        STARTUP.STORE_DATA('SFP link not detected...',Format=False,PDF= pdf)
        STARTUP.ACT_RES(f"{'M-Plane Connection Supervision (positive case)' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(235, 52, 52))           
        summary.append('FAIL_REASON :SFP link not detected...')
        summary.append(f"{'M-Plane Connection Supervision (positive case)' : <50}{'=' : ^20}{'FAIL' : ^20}")
        return False

    STARTUP.STORE_DATA('\t\t{}'.format('****************** Actual Result ******************'),Format=True,PDF= pdf)
    try:
        if Check == True:
            pdf.add_page()
            STARTUP.STORE_DATA('########## SYSTEM LOGS #########',Format=True,PDF= pdf)

            command = "cat {} | grep supervision;".format(configur.get('INFO','syslog_path'))
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            # print(tc008_obj.hostname, 22 ,tc008_obj.USER_N,tc008_obj.PSWRD)
            ssh.connect(tc008_obj.hostname, 22 ,tc008_obj.USER_N,tc008_obj.PSWRD)
            stdin, stdout, stderr = ssh.exec_command(command)
            lines = stdout.readlines()
            for i in lines:
                STARTUP.STORE_DATA(i,Format=False,PDF= pdf)
            pdf.add_page()
            ###############################################################################
            ## Expected/Actual Result
            ###############################################################################
            Exp_Result = 'Expected Result : TER NETCONF Client can change the value of the supervision timer in the supervision watchdog reset message. The O-RU NETCONF server must adjust the timer accordingly if this optional test is performed.'
            STARTUP.STORE_DATA(Exp_Result,Format='DESC',PDF= pdf)
            STARTUP.ACT_RES(f"{'M-Plane Connection Supervision (positive case)' : <50}{'=' : ^20}{'SUCCESS' : ^20}",PDF= pdf,COL=(105, 224, 113))
            summary.append(f"{'M-Plane Connection Supervision (positive case)' : <50}{'=' : ^20}{'PASS' : ^20}")
            return True

        
        else:
            ###############################################################################
            ## Expected/Actual Result
            ###############################################################################
            Exp_Result = 'Expected Result : TER NETCONF Client can change the value of the supervision timer in the supervision watchdog reset message. The O-RU NETCONF server must adjust the timer accordingly if this optional test is performed.'
            STARTUP.STORE_DATA(Exp_Result,Format='DESC',PDF= pdf)
            STARTUP.GET_SYSTEM_LOGS(tc008_obj.hostname,tc008_obj.USER_N,tc008_obj.PSWRD,pdf)
            if type(Check) == list:
                STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
                Error_Info = '''ERROR\n\terror-type \t: \t{}\n\terror-tag \t: \t{}\n\terror-severity \t: \t{}\n\tmessage' \t: \t{}'''.format(*map(str,Check))
                STARTUP.STORE_DATA(Error_Info,Format=False,PDF= pdf)
                STARTUP.ACT_RES(f"{'M-Plane Connection Supervision (positive case)' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(235, 52, 52))
                summary.append("FAIL_REASON : {}".format(Error_Info))
                summary.append(f"{'M-Plane Connection Supervision (positive case)' : <50}{'=' : ^20}{'FAIL' : ^20}")
            else:
                STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
                STARTUP.STORE_DATA('{}'.format(Check),Format=False,PDF= pdf)
                STARTUP.ACT_RES(f"{'M-Plane Connection Supervision (positive case)' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(235, 52, 52))           
                summary.append("FAIL_REASON : {}".format(Check))
                summary.append(f"{'M-Plane Connection Supervision (positive case)' : <50}{'=' : ^20}{'FAIL' : ^20}")
                return False

    except Exception as e:
            STARTUP.STORE_DATA('{}'.format(e), Format=True,PDF=pdf)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
            summary.append("FAIL_REASON : {}".format(e))
            summary.append(f"{'M-Plane Connection Supervision (positive case)' : <50}{'=' : ^20}{'FAIL' : ^20}")
            return False

    ###############################################################################
    ## For Capturing the logs
    ###############################################################################
    finally:
        STARTUP.CREATE_LOGS('M_CTC_ID_008',PDF=pdf)
        summary.append("Successfully completed Test Case M_CTC_ID_008. Logs captured !!")  
        notification('\n'.join(summary)) 

if __name__ == "__main__":
    start_time = time.time()
    test_M_ctc_id_008()
    end_time = time.time()
    print('Execution Time is : {}'.format(int(end_time-start_time)))
    pass

