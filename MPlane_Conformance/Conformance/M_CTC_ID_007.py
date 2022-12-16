###############################################################################
##@ FILE NAME:      M_CTC_ID_007
##@ TEST SCOPE:     M PLANE O-RAN CONFORMANCE
##@ Version:        V_1.0.0
##@ Support:        @Ramiyer, @VaibhavDhiman, @PriyaSharma
###############################################################################

###############################################################################
## Package Imports 
###############################################################################

import sys, os, time, socket, xmltodict, xml.dom.minidom, lxml.etree, lxml.etree
from ncclient import manager
from ncclient.operations import errors
from ncclient.operations.rpc import RPCError
from ncclient.transport import errors
from paramiko.ssh_exception import NoValidConnectionsError
from ncclient.operations.errors import TimeoutExpiredError
from ncclient.transport.errors import SessionCloseError
from configparser import ConfigParser
from ncclient.xml_ import to_ele

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
from require.calnexRest import calnexInit, calnexGet, calnexSet, calnexCreate, calnexDel,calnexGetVal
from require.Vlan_Creation import *

###############################################################################
## Initiate PDF
###############################################################################
pdf = STARTUP.PDF_CAP()

class M_CTC_ID_007(vlan_Creation):
    def __init__(self) -> None:
        super().__init__()
        self.interface_name = ''
        self.hostname, self.call_home_port = '',''
        self.USER_N = ''
        self.PSWRD = ''
        self.P_NEO_IP = ''
        self.P_NEO_PORT = ''
        self.session = ''
            
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
    ## Test Procedure
    ###############################################################################
    def test_procedure(self):
        STARTUP.STORE_DATA('\n\n\t\t********** Connect to the NETCONF Server ***********\n\n',Format='TEST_STEP',PDF = pdf)
        STATUS = STARTUP.STATUS(self.hostname,self.USER_N,self.session.session_id,830)
        STARTUP.STORE_DATA(self.login_info,Format=False,PDF = pdf)
        STARTUP.STORE_DATA(STATUS,Format=False,PDF = pdf)

        ###############################################################################
        ## Server Capabilities
        ###############################################################################
        for cap in self.session.server_capabilities:
            STARTUP.STORE_DATA("\t{}".format(cap),Format=False,PDF = pdf)
            
        ###############################################################################
        ## Test Procedure 1
        ###############################################################################
        pdf.add_page()
        Test_Step1 = "STEP 1 and 2 subscribe and check for the <rpc> reply."
        STARTUP.STORE_DATA('{}'.format(Test_Step1),Format='TEST_STEP',PDF = pdf) 
            
        ###############################################################################
        ## Create_subscription
        ###############################################################################
        cap=self.session.create_subscription()
        STARTUP.STORE_DATA('> subscribe', Format=True, PDF=pdf)
        dict_data = xmltodict.parse(str(cap))
        if dict_data['nc:rpc-reply']['nc:ok'] == None:
            STARTUP.STORE_DATA('\nOk\n', Format=False, PDF=pdf)
        


        ###############################################################################
        ## Genrate Notification and alarm
        ###############################################################################        
        STARTUP.STORE_DATA('{}'.format(Test_Step1), Format='TEST_STEP', PDF=pdf)
        xml_data2 = open("{}/require/Yang_xml/sw_install.xml".format(parent)).read()
        if '1' in self.slot_name:
            self.slot_name = self.slot_name[:-1]+'2'
        else:
            self.slot_name = self.slot_name[:-1]+'1'
        xml_data2 = xml_data2.format(slot_name=self.slot_name,File_name = '')
        STARTUP.STORE_DATA('******* Replace with below xml ********', Format=True, PDF=pdf)
        STARTUP.STORE_DATA(xml_data2, Format='XML', PDF=pdf)
        d3 = self.session.dispatch(to_ele(xml_data2))

        ###############################################################################
        ## Check_Notification
        ###############################################################################
        STARTUP.STORE_DATA('{}'.format('################## Check_Notification ##################'),Format=True, PDF=pdf)
        while True:
            n = self.session.take_notification(timeout=30)
            if n == None:
                break
            notify=n.notification_xml
            dict_n = xmltodict.parse(str(notify))
            s = xml.dom.minidom.parseString(notify)
            xml_pretty_str = s.toprettyxml()
            STARTUP.STORE_DATA(xml_pretty_str,Format='XML', PDF=pdf)
            STARTUP.STORE_DATA('{}\n'.format('-'*100),Format=False, PDF=pdf)
        return True 
    
    ###############################################################################
    ## Main Function
    ###############################################################################
    def test_Main(self):
        notification("Starting Test Case M_CTC_ID_007")
        Check1 = self.sfp_Linked()
        
        
        ###############################################################################
        ## Read User Name and password from Config.INI of Config.py
        ###############################################################################
        self.USER_N = configur.get('INFO','sudo_user')
        self.PSWRD = configur.get('INFO','sudo_pass')
        #self.P_NEO_IP = configur.get('INFO','paragon_ip')
        #self.P_NEO_PORT = configur.get('INFO','ptpsynceport')
        # Check2 = STARTUP.ping_status(self.P_NEO_IP)
        if (Check1 == False or Check1 == None):
            return False

        pkt = sniff(iface = self.interface, stop_filter = self.check_tcp_ip,timeout = 100)
        
        # sys.path.append(f'//{self.P_NEO_IP}/calnex100g/RemoteControl/')
        # calnexInit(f"{self.P_NEO_IP}")

        try:
            STARTUP.delete_system_log(host= self.hostname)
            time.sleep(2)
            ###############################################################################
            ## Perform call home to get ip_details
            ###############################################################################
            self.session, self.login_info = STARTUP.session_login(host = self.hostname,USER_N = self.USER_N,PSWRD = self.PSWRD)

            if self.session:
                RU_Details = STARTUP.demo(session = self.session,host= self.hostname, port= 830)

                ###############################################################################
                ## Start PTP & SYNCE
                ###############################################################################
                # calnexSet(f"app/mse/master/Master{self.P_NEO_PORT}/start")
                # calnexSet(f"app/generation/synce/esmc/Port{self.P_NEO_PORT}/start")

                
                for key, val in RU_Details[1].items():
                    if val[0] == 'true' and val[1] == 'true':
                        self.slot_name = key
                        ###############################################################################
                        ## Test Description
                        ###############################################################################
                        Test_Desc = '''Test Description : This scenario is MANDATORY.
This test validates that the O-RU properly handles a NETCONF subscription to notifications.
This scenario corresponds to the following chapters in [3]:
8.2 Manage Alarm Requests'''
                        CONFIDENTIAL = STARTUP.ADD_CONFIDENTIAL('07',SW_R = val[2]) 
                        STARTUP.STORE_DATA(CONFIDENTIAL,Format='CONF',PDF= pdf)
                        STARTUP.STORE_DATA(Test_Desc,Format='DESC',PDF= pdf)
                        pdf.add_page()

                
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
notification("Netconf Session Established")

           
    
def test_m_ctc_id_007():
    tc007_obj = M_CTC_ID_007()
    Check = tc007_obj.test_Main()
    if Check == False:
        STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
        STARTUP.STORE_DATA('SFP link not detected/Paragon Ip not Pinging...',Format=False,PDF= pdf)
        STARTUP.ACT_RES(f"{'Subscription to Notifications' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(235, 52, 52))
        return False
    ###############################################################################
    ## Expected/Actual Result
    ###############################################################################
    STARTUP.GET_SYSTEM_LOGS(tc007_obj.hostname,tc007_obj.USER_N,tc007_obj.PSWRD,pdf)
    Exp_Result = 'Expected Result : The O-RU NETCONF Server responds with <rpc-reply><ok/></rpc-reply> to the TER NETCONF Client.'
    STARTUP.STORE_DATA(Exp_Result,Format='DESC',PDF= pdf)

    STARTUP.STORE_DATA('\t\t{}'.format('****************** Actual Result ******************'),Format=True,PDF= pdf)

    try:
        if Check == True:
            STARTUP.ACT_RES(f"{'Subscription to Notifications' : <50}{'=' : ^20}{'SUCCESS' : ^20}",PDF= pdf,COL=(105, 224, 113))
            notification("Test Case is PASS")
            return True

        elif type(Check) == list:
            STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
            Error_Info = '''\terror-tag \t: \t{}\n\terror-type \t: \t{}\n\terror-severity \t: \t{}\n\tDescription' \t: \t{}'''.format(*map(str,Check))
            STARTUP.STORE_DATA(Error_Info,Format=False,PDF= pdf)
            STARTUP.ACT_RES(f"{'Subscription to Notifications' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(235, 52, 52))
            notification("Error Info : {}".format(Error_Info))
            return False
        else:
            STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
            STARTUP.STORE_DATA('{}'.format(Check),Format=False,PDF= pdf)
            STARTUP.ACT_RES(f"{'Subscription to Notifications' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(235, 52, 52))
            notification("Test Case is FAIL")
            return False

            
    except Exception as e:
            STARTUP.STORE_DATA('{}'.format(e), Format=True,PDF=pdf)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
            notification("Test Case is FAIL")
            return False

    ###############################################################################
    ## For Capturing the logs
    ###############################################################################
    finally:
        STARTUP.CREATE_LOGS('M_CTC_ID_007',PDF=pdf)
        notification("Test Completed For M_CTC_ID_007 and Logs saved !")   

if __name__ == "__main__":
    test_m_ctc_id_007()

