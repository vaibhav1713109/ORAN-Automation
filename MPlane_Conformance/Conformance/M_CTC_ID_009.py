###############################################################################
##@ FILE NAME:      M_CTC_ID_009
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
from Notification import *

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
from require import STARTUP, Config
from require.Vlan_Creation import *



###############################################################################
## Initiate PDF
###############################################################################
pdf = STARTUP.PDF_CAP()

class M_CTC_ID_009(vlan_Creation):
    def __init__(self) -> None:
        super().__init__()
        self.interface_name = ''
        self.hostname, self.call_home_port = '',''
        self.USER_N = ''
        self.PSWRD = ''
        self.P_NEO_IP = ''
        self.P_NEO_PORT = ''
        self.session = ''
        self.s_n_i = randint(1,5)
        self.g_t = randint(1,5)
            
    
    ###############################################################################
    ## Test Execution and Procedure
    ###############################################################################
    def test_procedure(self):
        try:
            STARTUP.STORE_DATA('\n\n\t\t********** Connect to the NETCONF Server ***********\n\n',Format='TEST_STEP',PDF = pdf)
            STATUS = STARTUP.STATUS(self.hostname,self.USER_N,self.session.session_id,830)
            STARTUP.STORE_DATA(STATUS,Format=False,PDF = pdf)


            ###############################################################################
            ## Server Capabilities
            ###############################################################################
            for cap in self.session.server_capabilities:
                STARTUP.STORE_DATA("\t{}".format(cap),Format=False,PDF = pdf)
                

            pdf.add_page()
            ###############################################################################
            ## Test Procedure 1
            ###############################################################################
            Test_Step1 = '\t\t***********step 1 and 2 Retrival of ru information with filter **********'
            STARTUP.STORE_DATA('{}'.format(Test_Step1),Format='TEST_STEP',PDF = pdf)
            notification("Netconf Session Established")
            
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
            
            
            ###############################################################################
            ## Append Changes in XML
            ###############################################################################
            xml_data = open("{}/require/Yang_xml/supervision.xml".format(parent)).read()
            xml_data = xml_data.format(super_n_i= self.s_n_i, guard_t_o= self.g_t)
            Test_Step1 = '\t\t TER NETCONF Client responds with <rpc supervision-watchdog-reset></rpc> to the O-RU NETCONF Server'
            STARTUP.STORE_DATA('{}'.format(Test_Step1),Format='TEST_STEP', PDF=pdf)
            STARTUP.STORE_DATA('> user-rpc',Format=True, PDF=pdf)
            STARTUP.STORE_DATA('******* Replace with below xml ********',Format=True, PDF=pdf)
            STARTUP.STORE_DATA('{}\n'.format(xml_data),Format='XML', PDF=pdf)
            d = self.session.dispatch(to_ele(xml_data))
            
            Test_Step2 = '\t\t O-RU NETCONF Server sends a reply to the TER NETCONF Client <rpc-reply><next-update-at>date-time</next-update-at></rpc-reply>'
            STARTUP.STORE_DATA('{}'.format(Test_Step2),Format='TEST_STEP', PDF=pdf)
            STARTUP.STORE_DATA('{}'.format(d),Format='XML', PDF=pdf)

            return True

        ###############################################################################
        ## Exception
        ###############################################################################
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
            
    ###############################################################################
    ## Main Function
    ###############################################################################
    def test_Main(self):
        notification("Starting Test Case M_CTC_ID_009 !!! ")
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
            self.session = STARTUP.call_home(host = '0.0.0.0', port=4334, hostkey_verify=False,username = self.USER_N, password = self.PSWRD,timeout = 60,allow_agent = False , look_for_keys = False)
            self.hostname, self.call_home_port = self.session._session._transport.sock.getpeername()   #['ip_address', 'TCP_Port']
            
            if self.session:
                RU_Details = STARTUP.demo(session = self.session,host= self.hostname, port= 830)
                
                for key, val in RU_Details[1].items():
                    if val[0] == 'true' and val[1] == 'true':
                        ###############################################################################
                        ## Test Description
                        ###############################################################################
                        Test_Desc = 'Test Description : This test validates that the O-RU manages the connection supervision process correctly.'
                        CONFIDENTIAL = STARTUP.ADD_CONFIDENTIAL('09',SW_R = val[2]) 
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
                time.sleep(self.s_n_i+self.g_t+2)
            except Exception as e:
                print(e)

def test_m_ctc_id_009():
    tc009_obj = M_CTC_ID_009()
    Check = tc009_obj.test_Main()           
    if Check == False:
            STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
            STARTUP.STORE_DATA('SFP link not detected...',Format=False,PDF= pdf)
            STARTUP.ACT_RES(f"{'M-Plane Connection Supervision (negative case)' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(235, 52, 52))
            return False
    ###############################################################################
    ## Expected/Actual Result
    ###############################################################################
    STARTUP.GET_SYSTEM_LOGS(tc009_obj.hostname,tc009_obj.USER_N,tc009_obj.PSWRD,pdf) 
    Exp_Result = 'Expected Result : TER NETCONF Client can change the value of the supervision timer in the supervision watchdog reset message. The O-RU NETCONF server must adjust the timer accordingly if this optional test is performed.'
    STARTUP.STORE_DATA(Exp_Result,Format='DESC',PDF= pdf)
    STARTUP.STORE_DATA('\t\t{}'.format('****************** Actual Result ******************'),Format=True,PDF= pdf)
    try:
        if Check == True:
            STARTUP.ACT_RES(f"{'M-Plane Connection Supervision (negative case)' : <50}{'=' : ^20}{'SUCCESS' : ^20}",PDF= pdf,COL=(105, 224, 113))
            notification("Test Case is PASS")
            return True

        elif type(Check) == list:
            STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
            Error_Info = '''ERROR\n\terror-type \t: \t{}\n\terror-tag \t: \t{}\n\terror-severity \t: \t{}\n\tmessage' \t: \t{}'''.format(*map(str,Check))
            STARTUP.STORE_DATA(Error_Info,Format=False,PDF= pdf)
            STARTUP.ACT_RES(f"{'M-Plane Connection Supervision (negative case)' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(235, 52, 52))
            notification("Error Info : {}".format(Error_Info))
            return False
        else:
            STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
            STARTUP.STORE_DATA('{}'.format(Check),Format=False,PDF= pdf)
            STARTUP.ACT_RES(f"{'M-Plane Connection Supervision (negative case)' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(235, 52, 52))
            notification("Test Case is FAIL")
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
        STARTUP.CREATE_LOGS('M_CTC_ID_009',PDF=pdf)
        notification("Successfully completed Test Case M_CTC_ID_009. Logs captured !!")   
if __name__ == "__main__":
    test_m_ctc_id_009()
    pass
