###############################################################################
##@ FILE NAME:      M_CTC_ID_017
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


###############################################################################
## Initiate PDF
###############################################################################
pdf = STARTUP.PDF_CAP()
summary = []

class M_CTC_ID_017(vlan_Creation):
    # init method or constructor 
    def __init__(self):
        super().__init__()
        self.hostname, self.call_home_port = '',''
        self.USER_N = ''
        self.PSWRD = ''
        self.session, self.session2 = '', ''
        self.RU_Details = ''

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

        ###############################################################################
        ## Create_subscription
        ###############################################################################
        filter = """<filter type="xpath" xmlns="urn:ietf:params:xml:ns:netconf:notification:1.0" xmlns:swm="urn:o-ran:software-management:1.0" select="/swm:*"/>"""
        cap=self.session.create_subscription(filter=filter)
        STARTUP.STORE_DATA('> subscribe', Format=True, PDF=pdf)
        dict_data = xmltodict.parse(str(cap))
        if dict_data['nc:rpc-reply']['nc:ok'] == None:
            STARTUP.STORE_DATA('\nOk\n', Format=False, PDF=pdf)
        summary.append('Subscription with software-summary.append filter Performed!!')
        


        ###############################################################################
        ## Initial Get Filter
        ###############################################################################
        pdf.add_page()
        STARTUP.STORE_DATA('> get --filter-xpath /o-ran-software-management:software-inventory',Format=True, PDF=pdf)
        sw_inv = '''<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
        <software-inventory xmlns="urn:o-ran:software-management:1.0">
        </software-inventory>
        </filter>'''
        slot_names = self.session.get(sw_inv).data_xml
        s = xml.dom.minidom.parseString(slot_names)
        xml_pretty_str = s.toprettyxml()
        slot_n = xmltodict.parse(str(slot_names))
        li = ['INVALID', 'EMPTY']
        slots_info1 = slot_n['data']['software-inventory']['software-slot']
        for SLOT in slots_info1:
            if SLOT['status'] in li:
                STARTUP.STORE_DATA(xml_pretty_str,Format='XML', PDF=pdf)

                return f'SW slot status is Invalid for {SLOT["name"]}...'
        STARTUP.STORE_DATA(xml_pretty_str, Format='XML', PDF=pdf)


        ###############################################################################
        ## Test Procedure 1 : Configure_Reset_RPC_in_RU
        ###############################################################################
        summary.append('Configure reset RPC!!')
        Test_Step1 = '\t\tStep 1 : TER NETCONF Client sends <rpc><reset></rpc> to the O-RU NETCONF Server..'
        STARTUP.STORE_DATA('{}'.format(Test_Step1),Format='TEST_STEP', PDF=pdf)
        STARTUP.STORE_DATA('\n> user-rpc\n',Format=True, PDF=pdf)
        STARTUP.STORE_DATA('******* Replace with below xml ********',Format=True, PDF=pdf)
        xml_data3 = '''<reset xmlns="urn:o-ran:operations:1.0"></reset>'''
        STARTUP.STORE_DATA(xml_data3,Format='XML', PDF=pdf)
        d3 = self.session.dispatch(to_ele(xml_data3))

        ###############################################################################
        ## Test Procedure 2 : Get RPC Reply
        ###############################################################################
        Test_Step2 = '\t\tStep 2 : O-RU NETCONF Server responds with rpc-reply.'
        STARTUP.STORE_DATA('{}'.format(Test_Step2),Format='TEST_STEP', PDF=pdf)
        STARTUP.STORE_DATA('{}'.format(d3),Format='XML', PDF=pdf)

        Test_Step3 = '\t\tStep 3 : O-RU restarts with a new software version running matching the version activated.'
        STARTUP.STORE_DATA('{}'.format(Test_Step3),Format='TEST_STEP', PDF=pdf)
        summary.append('RU Going for reboot!!')
        return True


    ###############################################################################
    ## Get_Filter_after_Reboot_the_RU
    ###############################################################################
    def get_config_detail(self):
        self.linked_detected()
        sniff(iface = self.interface, stop_filter = self.check_tcp_ip, timeout = 100)
        ###############################################################################
        ## Perform Call Home to get IP after RU comes up
        ###############################################################################
        t = time.time() +20
        while time.time() < t:
            try:
                self.session2, self.login_info = STARTUP.session_login(host = self.hostname,USER_N = self.USER_N,PSWRD = self.PSWRD)

                if self.session2:
                    ###############################################################################
                    ## Check the get filter of SW
                    ###############################################################################
                    sw_inv = '''<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                            <software-inventory xmlns="urn:o-ran:software-management:1.0">
                            </software-inventory>
                            </filter>'''

                    slot_names = self.session2.get(sw_inv).data_xml
                    s = xml.dom.minidom.parseString(slot_names)
                    xml_pretty_str = s.toprettyxml()
                    dict_slots = xmltodict.parse(str(slot_names))

                    li = ['INVALID', 'EMPTY']
                    SLOTS_INFO = dict_slots['data']['software-inventory']['software-slot']
                    for i in SLOTS_INFO:
                        if i['name'] in li:
                            STARTUP.STORE_DATA(xml_pretty_str,Format='XML', PDF=pdf)
                            return f'{i["name"]} status is not correct....'
                    STARTUP.STORE_DATA(xml_pretty_str, Format='XML', PDF=pdf)
                    # self.session2.close_session()
                    summary.append('RU Boot Successfully with new software!!')
                    return True
                
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
                # self.session.close_session()
                return [e.type, e.tag, e.severity, e.path, e.message, exc_tb.tb_lineno]

            finally:
                try:
                    self.session2.close_session()
                except Exception as e:
                    print(e)
                pass
        else:
            return 'Call Home is not Initiated...'

    ###############################################################################
    ## Reboot The RU after activation
    ###############################################################################
    def reset_rpc(self):
        summary.append("Test Case M_CTC_ID_014 is under process...")
        Check1 = self.linked_detected()
        

        ###############################################################################
        ## Read User Name and password from Config.INI of Config.py
        ############################################################################### 
        self.USER_N = configur.get('INFO','sudo_user')
        self.PSWRD = configur.get('INFO','sudo_pass')
        if Check1 == False or Check1 == None:
            return Check1
    
        pkt = sniff(iface = self.interface, stop_filter = self.check_tcp_ip, timeout = 100)
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
                    if val[1] == 'true':
                        ###############################################################################
                        ## Test Description
                        ###############################################################################
                        Test_Desc = '''Test Description : This scenario is MANDATORY
                        This test validates that the O-RU can successfully start up with activated software.
                        This scenario corresponds to the following chapters in [3]:
                        5. Software Management'''
                        CONFIDENTIAL = STARTUP.ADD_CONFIDENTIAL('17', SW_R=val[2])
                        STARTUP.STORE_DATA(CONFIDENTIAL, Format='CONF', PDF=pdf)
                        STARTUP.STORE_DATA(Test_Desc, Format='DESC', PDF=pdf)
                        pdf.add_page()

                
                del self.RU_Details[1]['swRecoverySlot']
                result = self.test_procedure()
                # time.sleep(5)
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

    def system_logs(self,hostname):
        for _ in range(5):
            try:
                host = hostname
                port = 22
                username = self.USER_N
                password = self.PSWRD
                command = "cat {};".format(configur.get('INFO','syslog_path'))
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(host, port, username, password)

                stdin, stdout, stderr = ssh.exec_command(command)
                lines = stdout.readlines()
                # print(lines)
                return lines
            except Exception as e:
                print(e)
        else:
            print('Can\'t connect to the RU.., Logs are not captured.')




        
def test_m_ctc_id_017():
    tc017_obj = M_CTC_ID_017()
    Check1 = tc017_obj.reset_rpc()
    
    if Check1 == False:
        STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
        STARTUP.STORE_DATA('SFP link not detected...',Format=False,PDF= pdf)
        STARTUP.ACT_RES(f"{'Supplemental Reset after Software Activation' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(255,0,0))
        summary.append('FAIL_REASON :SFP link not detected...')
        summary.append(f"{'Supplemental Reset after Software Activation' : <50}{'=' : ^20}{'FAIL' : ^20}")
        return False
    if Check1 == True:
        logs1 = tc017_obj.system_logs(tc017_obj.hostname)
        time.sleep(40)
        Check2 = tc017_obj.get_config_detail()
        logs2 = tc017_obj.system_logs(tc017_obj.hostname)
        STARTUP.STORE_DATA('\t\t\t\t############ SYSTEM LOGS ##############',Format=True,PDF=pdf)
        for i in logs1:
            STARTUP.STORE_DATA("{}".format(i),Format=False,PDF=pdf)
        for i in logs2:
            STARTUP.STORE_DATA("{}".format(i),Format=False,PDF=pdf)
        ###############################################################################
        ## Expected/Actual Result
        ###############################################################################
        Exp_Result = '''Expected Result : 1. The status of the software slot used for software activation remains VALID (it is unchanged) and the parameter "active" remains "True". The parameter "running" is set to True.
        2. Status of the software slot containing the previous version of software used by device remains VALID, the parameter "active" remains False. The parameter "running" is set to False.'''
        STARTUP.STORE_DATA(Exp_Result, Format='DESC', PDF=pdf)

        STARTUP.STORE_DATA('\t\t{}'.format('****************** Actual Result ******************'), Format=True, PDF=pdf)
        
        try:
            if Check2 == True:
                STARTUP.ACT_RES(f"{'Supplemental Reset after Software Activation' : <50}{'=' : ^20}{'SUCCESS' : ^20}",PDF= pdf,COL=(0,255,0))
                summary.append(f"{'Supplemental Reset after Software Activation' : <50}{'=' : ^20}{'PASS' : ^20}")
                return True

            else:
                if type(Check2) == list:
                    STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
                    Error_Info = '''ERROR\n\terror-type \t: \t{}\n\terror-tag \t: \t{}\n\terror-severity \t: \t{}\n\tmessage' \t: \t{}'''.format(*map(str,Check2))
                    STARTUP.STORE_DATA(Error_Info,Format=False,PDF= pdf)
                    STARTUP.ACT_RES(f"{'Supplemental Reset after Software Activation' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(255,0,0))
                    summary.append("FAIL_REASON : {}".format(Error_Info))
                    summary.append(f"{'Supplemental Reset after Software Activation' : <50}{'=' : ^20}{'FAIL' : ^20}")
                    return False

                else:
                    STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
                    STARTUP.STORE_DATA('{}'.format(Check2),Format=False,PDF= pdf)
                    STARTUP.ACT_RES(f"{'Supplemental Reset after Software Activation' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(255,0,0))
                    summary.append("FAIL_REASON : {}".format(Check2))
                    summary.append(f"{'Supplemental Reset after Software Activation' : <50}{'=' : ^20}{'FAIL' : ^20}")
                    return False

        except Exception as e:
            STARTUP.STORE_DATA('{}'.format(e), Format=True,PDF=pdf)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
            summary.append("FAIL_REASON : {}".format(e))
            summary.append(f"{'Supplemental Reset after Software Activation' : <50}{'=' : ^20}{'FAIL' : ^20}")
            return False
        
        ###############################################################################
        ## For Capturing the logs
        ###############################################################################
        finally:
            STARTUP.CREATE_LOGS('M_CTC_ID_017',PDF=pdf)
            summary.append("Successfully completed Test Case M_CTC_ID_017. Logs captured !!") 


    else:
        ###############################################################################
        ## Expected/Actual Result
        ###############################################################################
        Exp_Result = '''Expected Result : 1. The status of the software slot used for software activation remains VALID (it is unchanged) and the parameter "active" remains "True". The parameter "running" is set to True.
        2. Status of the software slot containing the previous version of software used by device remains VALID, the parameter "active" remains False. The parameter "running" is set to False.'''
        STARTUP.STORE_DATA(Exp_Result, Format='DESC', PDF=pdf)

        STARTUP.STORE_DATA('\t\t{}'.format('****************** Actual Result ******************'), Format=True, PDF=pdf)
        try:

            if type(Check1) == list:
                STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
                Error_Info = '''ERROR\n\terror-type \t: \t{}\n\terror-tag \t: \t{}\n\terror-severity \t: \t{}\n\tmessage' \t: \t{}'''.format(*map(str,Check1))
                STARTUP.STORE_DATA(Error_Info,Format=False,PDF= pdf)
                STARTUP.ACT_RES(f"{'Supplemental Reset after Software Activation' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(255,0,0))
                summary.append("FAIL_REASON : {}".format(Error_Info))
                summary.append(f"{'Supplemental Reset after Software Activation' : <50}{'=' : ^20}{'FAIL' : ^20}")
                return False
            else:
                STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
                STARTUP.STORE_DATA('{}'.format(Check1),Format=False,PDF= pdf)
                STARTUP.ACT_RES(f"{'Supplemental Reset after Software Activation' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(255,0,0))
                summary.append("FAIL_REASON : {}".format(Check1))
                summary.append(f"{'Supplemental Reset after Software Activation' : <50}{'=' : ^20}{'FAIL' : ^20}")
                return False


        except Exception as e:
                STARTUP.STORE_DATA('{}'.format(e), Format=True,PDF=pdf)
                exc_type, exc_obj, exc_tb = sys.exc_info()
                STARTUP.STORE_DATA(
                    f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
                summary.append("FAIL_REASON : {}".format(e))
                summary.append(f"{'Supplemental Reset after Software Activation' : <50}{'=' : ^20}{'FAIL' : ^20}")
                return False

        ###############################################################################
        ## For Capturing the logs
        ###############################################################################
        finally:
            STARTUP.CREATE_LOGS('M_CTC_ID_017',PDF=pdf)
            summary.append("Successfully completed Test Case M_CTC_ID_017. Logs captured !!") 
            notification('\n'.join(summary))


if __name__ == "__main__":
    start_time = time.time()
    test_m_ctc_id_017()
    end_time = time.time()
    print('Execution Time is : {}'.format(int(end_time-start_time)))
    pass
