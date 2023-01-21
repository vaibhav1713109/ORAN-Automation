###############################################################################
##@ FILE NAME:      M_CTC_ID_012
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


class M_CTC_ID_012(vlan_Creation):
   
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
        notification('Netconf Session Established!!')

        ###############################################################################
        ## Server Capabilities
        ###############################################################################
        for cap in self.session.server_capabilities:
            STARTUP.STORE_DATA("\t{}".format(cap),Format=False,PDF = pdf)
        notification('Hello Capabilities Exchanged!!')
            
        ###############################################################################
        ## Create_subscription
        ###############################################################################
        filter = """<filter type="xpath" xmlns="urn:ietf:params:xml:ns:netconf:notification:1.0" xmlns:fm="urn:o-ran:fm:1.0" select="/fm:*"/>"""
        cap=self.session.create_subscription(filter=filter)
        STARTUP.STORE_DATA('> subscribe --filter-xpath /o-ran-fm::*', Format=True, PDF=pdf)
        dict_data = xmltodict.parse(str(cap))
        if dict_data['nc:rpc-reply']['nc:ok'] == None:
            STARTUP.STORE_DATA('\nOk\n', Format=False, PDF=pdf)
        notification('Subscription with o-ran-fm filter performed!!')
        
        
        ###############################################################################
        ## Initial Get
        ###############################################################################
        pdf.add_page()
        STARTUP.STORE_DATA("\t\t########### Initial Get#####################",Format='TEST_STEP',PDF=pdf)
        STARTUP.STORE_DATA('\n>get --filter-xpath /o-ran-sync:sync',Format=True,PDF=pdf)
        SYNC = '''<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            <sync xmlns="urn:o-ran:sync:1.0">
            </sync>
            </filter>
            '''
        data  = self.session.get(SYNC).data_xml
        dict_Sync = xmltodict.parse(str(data))
        x = xml.dom.minidom.parseString(data)
        xml_pretty_str = x.toprettyxml()
        STARTUP.STORE_DATA(xml_pretty_str,Format='XML',PDF=pdf)

        
        ###############################################################################
        ## Test Procedure 1: get filter of Locked state
        ###############################################################################
        pdf.add_page()
        Test_Step1 = 'Step 1 The TER NETCONF Client periodically tests O-RU\'s sync-status until the LOCKED state is reached.'
        STARTUP.STORE_DATA("\t\t{}".format(Test_Step1),Format='TEST_STEP',PDF=pdf)
        STARTUP.STORE_DATA('\n>get --filter-xpath /o-ran-sync:sync',Format=True,PDF=pdf)
        start_time = time.time() + 1200
        while time.time() < start_time:
            SYNC = '''<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            <sync xmlns="urn:o-ran:sync:1.0">
            </sync>
            </filter>
            '''
            data  = self.session.get(SYNC).data_xml
            dict_Sync = xmltodict.parse(str(data))
            state = dict_Sync['data']['sync']['sync-status']['sync-state']
            if state == 'LOCKED':

                x = xml.dom.minidom.parseString(data)
                

                xml_pretty_str = x.toprettyxml()

                STARTUP.STORE_DATA(xml_pretty_str,Format='XML',PDF=pdf)
                break
        else:
            STARTUP.STORE_DATA(xml_pretty_str,Format='XML',PDF=pdf)
            return False
        notification('Sync-State "LOCKED" detected!!')

        ########################### Turn Off the PTP & SYNCE ############################
        calnexSet(f"app/mse/master/Master{Config.details['PORT']}/stop")
        calnexSet(f"app/generation/synce/esmc/Port{Config.details['PORT']}/stop")


        ########################### Check The Alarm No 17 ############################
        pdf.add_page()
        STARTUP.STORE_DATA('######## NOTIFICATIONS ########',Format=True,PDF=pdf)
        while True:
            n = self.session.take_notification()
            if n == None:
                return 1
            notify=n.notification_xml
            dict_n = xmltodict.parse(str(notify))
            try:
                notf = dict_n['notification']['alarm-notif']['fault-id']
                type(notf)
                if notf == '17':
                    ###############################################################################
                    ## Test Procedure 2
                    ###############################################################################
                    Test_Step2 = '\t\tStep 2 After a while (time depends on implementation) the O-RU NETCONF SERVER sends a notification for  alarm 17: No external sync source.'
                    STARTUP.STORE_DATA("{}".format(Test_Step2),Format='TEST_STEP',PDF=pdf)
                    x = xml.dom.minidom.parseString(notify)
                    xml_pretty_str = x.toprettyxml()
                    STARTUP.STORE_DATA(xml_pretty_str,Format='XML',PDF=pdf)
                    break
                else:
                    x = xml.dom.minidom.parseString(notify)
                    #xml = xml.dom.minidom.parseString(user_name)

                    xml_pretty_str = x.toprettyxml()
                    # STARTUP.STORE_DATA(xml_pretty_str,Format='XML',PDF=pdf)
                    pass
            except:
                pass
        notification('Alarm notification with "fault-id 17" captured!!')
        return True
        
    ###############################################################################
    ## Main Function
    ###############################################################################
    def test_Main_012(self):
        notification("Test Case M_CTC_ID_012 is under process...")
        Check1 = self.linked_detected()
        
        
        ###############################################################################
        ## Read User Name and password from Config.INI of Config.py
        ###############################################################################
        self.USER_N = configur.get('INFO','sudo_user')
        self.PSWRD = configur.get('INFO','sudo_pass')
        self.P_NEO_IP = configur.get('INFO','paragon_ip')
        self.P_NEO_PORT = configur.get('INFO','ptpsynceport')
        Check2 = STARTUP.ping_status(self.P_NEO_IP)
        # print(type(Check1 and Check2))
        if ((Check1 == False or Check1 == None) and Check2) == False:
            return Check1 and Check2
            
        sniff(iface = self.interface, stop_filter = self.check_tcp_ip, timeout = 100)
        sys.path.append(f'//{self.P_NEO_IP}/calnex100g/RemoteControl/')
        calnexInit(f"{self.P_NEO_IP}")
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
                ## Enable PTP & SYNCE
                ###############################################################################
                calnexSet(f"app/mse/master/Master{self.P_NEO_PORT}/start")
                calnexSet(f"app/generation/synce/esmc/Port{self.P_NEO_PORT}/start")

                for key, val in RU_Details[1].items():
                    if val[1] == 'true':
                        ###############################################################################
                        ## Test Description
                        ###############################################################################
                        Test_Desc = 'Test Description : The minimum functions of the TER described in section 2.1 that support validation of the M-Plane are operational, configured and connected to the O-RU.'
                        CONFIDENTIAL = STARTUP.ADD_CONFIDENTIAL('12',SW_R = val[2]) 
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


def test_m_ctc_id_012():
    tc012_obj = M_CTC_ID_012()
    Check = tc012_obj.test_Main_012()
    if Check == False:
        STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
        STARTUP.STORE_DATA('{}'.format('SFP link not detected/ paragon ip not ping..'),Format=False,PDF= pdf)
        STARTUP.ACT_RES(f"{'O-RU Alarm Notification Generation' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(255,0,0))
        notification('FAIL_REASON :SFP link not detected...')
        notification(f"{'Retrieval of Active Alarm List' : <50}{'=' : ^20}{'FAIL' : ^20}")
        return False

    ###############################################################################
    ## Expected/Actual Result
    ###############################################################################
    STARTUP.GET_SYSTEM_LOGS(tc012_obj.hostname,tc012_obj.USER_N,tc012_obj.PSWRD,pdf)
    Exp_Result = 'Expected Result : After a while (time depends on implementation) the O-RU NETCONF SERVER sends a notification for alarm 17: No external sync source.'
    STARTUP.STORE_DATA(Exp_Result,Format='DESC',PDF= pdf)

    STARTUP.STORE_DATA('\t\t{}'.format('****************** Actual Result ******************'),Format=True,PDF= pdf)
    try:
        if Check == True:
            STARTUP.ACT_RES(f"{'O-RU Alarm Notification Generation' : <50}{'=' : ^20}{'SUCCESS' : ^20}",PDF= pdf,COL=(0,255,0))
            notification(f"{'Retrieval of Active Alarm List' : <50}{'=' : ^20}{'PASS' : ^20}")
            return True

        elif type(Check) == list:
            STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
            Error_Info = '''ERROR\n\terror-type \t: \t{}\n\terror-tag \t: \t{}\n\terror-severity \t: \t{}\n\tmessage' \t: \t{}'''.format(*map(str,Check))
            STARTUP.STORE_DATA(Error_Info,Format=False,PDF= pdf)
            STARTUP.ACT_RES(f"{'O-RU Alarm Notification Generation' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(255,0,0))
            notification("FAIL_REASON : {}".format(Error_Info))
            notification(f"{'Retrieval of Active Alarm List' : <50}{'=' : ^20}{'FAIL' : ^20}")
            return False
        else:
            STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
            STARTUP.STORE_DATA('{}'.format(Check),Format=False,PDF= pdf)
            STARTUP.ACT_RES(f"{'O-RU Alarm Notification Generation' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(255,0,0))
            notification("FAIL_REASON : {}".format(Check))
            notification(f"{'Retrieval of Active Alarm List' : <50}{'=' : ^20}{'FAIL' : ^20}")
            return False


    except Exception as e:
            STARTUP.STORE_DATA('{}'.format(e), Format=True,PDF=pdf)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
            notification("FAIL_REASON : {}".format(e))
            notification(f"{'Retrieval of Active Alarm List' : <50}{'=' : ^20}{'FAIL' : ^20}")
            return False

    ###############################################################################
    ## For Capturing the logs
    ###############################################################################
    finally:
        STARTUP.CREATE_LOGS('M_CTC_ID_012',PDF=pdf)
        notification("Successfully completed Test Case M_CTC_ID_012. Logs captured !!")   


if __name__ == "__main__":
    start_time = time.time()
    test_m_ctc_id_012()
    end_time = time.time()
    print('Execution Time is : {}'.format(int(end_time-start_time)))
    pass
