###############################################################################
##@ FILE NAME:      M_CTC_ID_013
##@ TEST SCOPE:     M PLANE O-RAN CONFORMANCE
##@ Version:        V_1.0.0
##@ Support:        @Ramiyer, @VaibhavDhiman, @PriyaSharma
###############################################################################

###############################################################################
## Package Imports 
###############################################################################

import socket, sys, os, warnings, time, xmltodict, xml.dom.minidom, paramiko, lxml.etree
from ncclient import manager
from ncclient.operations.rpc import RPC, RPCError
from ncclient.transport import errors
from paramiko.ssh_exception import NoValidConnectionsError
from ncclient.operations.errors import TimeoutExpiredError
from ncclient.transport.errors import SessionCloseError
from configparser import ConfigParser
from scapy.all import *

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
from require.calnexRest import calnexInit, calnexGet, calnexSet, calnexCreate, calnexDel,calnexGetVal

###############################################################################
## Initiate PDF
###############################################################################
pdf = STARTUP.PDF_CAP()

class M_CTC_ID_013(vlan_Creation):
    # init method or constructor 
    def __init__(self):
        super().__init__()
        self.hostname, self.call_home_port = '',''
        self.USER_N = ''
        self.PSWRD = ''
        self.session = ''
        self.P_NEO_IP = ''
        self.P_NEO_PORT = ''

    ###############################################################################
    ## Test Procedure
    ###############################################################################
    def test_procedure(self):
        STARTUP.STORE_DATA('\n\n\t\t********** Connect to the NETCONF Server ***********\n\n',Format='TEST_STEP',PDF = pdf)
        STARTUP.STORE_DATA(self.login_info,Format=False,PDF = pdf)
        STATUS = STARTUP.STATUS(self.hostname,self.USER_N,self.session.session_id,830)
        STARTUP.STORE_DATA(STATUS,Format=False,PDF = pdf)
        notification("Netconf Session Established")


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
        ## Get_Filter_Alarm
        ###############################################################################
        pdf.add_page()
        alarm_filter = '''
                <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <active-alarm-list xmlns="urn:o-ran:fm:1.0">
                </active-alarm-list>
                </filter>
                '''
        alrm = self.session.get(alarm_filter).data_xml
        dict_alarm = xmltodict.parse(str(alrm))

        ###############################################################################
        ## Test Procedure 1
        ###############################################################################
        Test_Step1 = '\t\tStep 1 The TER NETCONF Client sends the O-RU NETCONF Server a command to get the active-alarm-list.'
        STARTUP.STORE_DATA("{}".format(Test_Step1),Format='TEST_STEP',PDF=pdf)
        STARTUP.STORE_DATA("\n> get --filter-xpath /o-ran-fm:active-alarm-list/active-alarms\n",Format=True,PDF=pdf)
        s = xml.dom.minidom.parseString(alrm)
        xml_pretty_str = s.toprettyxml()
        alrm_name = dict_alarm['data']['active-alarm-list']['active-alarms']
        list_alrm = []
        for i in alrm_name:
            if "fault-id" in i.keys() and "fault-text" in i.keys():
                list_alrm.append(i["fault-id"])
                list_alrm.append(i["fault-text"])
        if 'No external sync source' in list_alrm:
            STARTUP.STORE_DATA(xml_pretty_str,Format='XML',PDF=pdf)
        else:
            STARTUP.STORE_DATA(xml_pretty_str,Format='XML',PDF=pdf)
            return '{}'.format(xml_pretty_str)
        return True


    ###############################################################################
    ## Main Function
    ###############################################################################
    def test_Main_013(self):
        notification("Starting Test Case M_CTC_ID_013 !!! ")
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
                RU_Details = STARTUP.demo(session = self.session,host= self.hostname, port= 830)
                for key, val in RU_Details[1].items():
                    if val[1] == 'true':
                        ###############################################################################
                        ## Test Description
                        ###############################################################################
                        Test_Desc = 'Test Description : The minimum functions of the TER described in section 2.1 that support validation of the M-Plane are operational, configured and connected to the O-RU'
                        CONFIDENTIAL = STARTUP.ADD_CONFIDENTIAL('13',SW_R = val[2]) 
                        STARTUP.STORE_DATA(CONFIDENTIAL,Format='CONF',PDF= pdf)
                        STARTUP.STORE_DATA(Test_Desc,Format='DESC',PDF= pdf)
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

        
def test_m_ctc_id_013():
    tc013_obj = M_CTC_ID_013()
    Check = tc013_obj.test_Main_013()
    if Check == False:
        STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
        STARTUP.STORE_DATA('SFP link not detected...',Format=False,PDF= pdf)
        STARTUP.ACT_RES(f"{'Retrieval of Active Alarm List' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(255,0,0))
        return False
    
    ###############################################################################
    ## Expected/Actual Result
    ###############################################################################
    STARTUP.GET_SYSTEM_LOGS(tc013_obj.hostname,tc013_obj.USER_N,tc013_obj.PSWRD,pdf)
    Exp_Result = 'Expected Result : The O-RU NETCONF Server responds with <rpc-reply><data> where <data> contains at least the same alarm as reported in measurement atleast alarm 17: No external sync source'
    STARTUP.STORE_DATA(Exp_Result,Format='DESC',PDF= pdf)

    STARTUP.STORE_DATA('\t\t{}'.format('****************** Actual Result ******************'),Format=True,PDF= pdf)
    try:
        if Check == True:
            STARTUP.ACT_RES(f"{'Retrieval of Active Alarm List' : <50}{'=' : ^20}{'SUCCESS' : ^20}",PDF= pdf,COL=(0,255,0))
            notification("Test Case is PASS")
            return True

        elif type(Check) == list:
            STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
            Error_Info = '''ERROR\n\terror-type \t: \t{}\n\terror-tag \t: \t{}\n\terror-severity \t: \t{}\n\tmessage' \t: \t{}'''.format(*map(str,Check))
            STARTUP.STORE_DATA(Error_Info,Format=False,PDF= pdf)
            STARTUP.ACT_RES(f"{'Retrieval of Active Alarm List' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(255,0,0))
            notification("Error Info : {}".format(Error_Info))
            return False
        else:
            STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
            STARTUP.STORE_DATA('{}'.format(Check),Format=False,PDF= pdf)
            STARTUP.ACT_RES(f"{'Retrieval of Active Alarm List' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(255,0,0))
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
        STARTUP.CREATE_LOGS('M_CTC_ID_013',PDF=pdf)
        notification("Successfully completed Test Case M_CTC_ID_013. Logs captured !!")    



if __name__ == "__main__":
    test_m_ctc_id_013()
    pass

