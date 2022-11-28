###############################################################################
##@ FILE NAME:      M_CTC_ID_016
##@ TEST SCOPE:     M PLANE O-RAN CONFORMANCE
##@ Version:        V_1.0.0
##@ Support:        @Ramiyer, @VaibhavDhiman, @PriyaSharma
###############################################################################

###############################################################################
## Package Imports 
###############################################################################

import socket, sys, os, time, xmltodict, xml.dom.minidom, lxml.etree, subprocess
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
from require.Vlan_Creation import *
from require import STARTUP, Config



###############################################################################
## Initiate PDF
###############################################################################
pdf = STARTUP.PDF_CAP()

class M_CTC_ID_016(vlan_Creation):
    # init method or constructor 
    def __init__(self):
        super().__init__()
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
        ## Initial Get Filter
        ###############################################################################
        pdf.add_page()
        STARTUP.STORE_DATA('\t\tInitial Get Filter',Format='TEST_STEP', PDF=pdf)
        STARTUP.STORE_DATA(
            '\n> get --filter-xpath /o-ran-software-management:software-inventory', Format=True, PDF=pdf)
        sw_inv = '''<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
        <software-inventory xmlns="urn:o-ran:software-management:1.0">
        </software-inventory>
        </filter>'''
        slot_names = self.session.get(sw_inv).data_xml

        ###############################################################################
        ## Checking The status, active and running value
        ###############################################################################
        s = xml.dom.minidom.parseString(slot_names)
        xml_pretty_str = s.toprettyxml()
        slot_n = xmltodict.parse(str(slot_names))
        SLOTS = slot_n['data']['software-inventory']['software-slot']
        SLOT_INFO = {}
        for SLOT in SLOTS:
            if SLOT['status'] == 'INVALID':
                STARTUP.STORE_DATA(xml_pretty_str, Format='XML', PDF=pdf)
                return f'SW slot status is Invalid for {SLOT["name"]}...'
            if (SLOT['name'] != 'swRecoverySlot'):
                SLOT_INFO[SLOT['name']] = [SLOT['active'], SLOT['running']]

            if (SLOT['active'] == 'true' and SLOT['running'] == 'true') or (SLOT['active'] == 'false' and SLOT['running'] == 'false'):
                if (SLOT['active'] == 'false' and SLOT['running'] == 'false') and (SLOT['name'] != 'swRecoverySlot'):
                    slot_name = SLOT['name']
                    del SLOT_INFO[SLOT['name']]
                pass
            else:
                return f'Slots Active and Running Status are diffrent for {SLOT["name"]}...'

        DEACTIVE_SLOT = list(SLOT_INFO.keys())
        STARTUP.STORE_DATA(xml_pretty_str, Format='XML', PDF=pdf)

        ###############################################################################
        ## Test Procedure 1 : Configure SW Activate RPC in RU
        ###############################################################################
        Test_Step1 = '\t\tStep 1 : TER NETCONF Client triggers <rpc><software-activate> Slot must have attributes active = FALSE, running = FALSE.'
        STARTUP.STORE_DATA('{}'.format(Test_Step1), Format='TEST_STEP', PDF=pdf)
        xml_data2 = open("{}/require/Yang_xml/sw_activate.xml".format(parent)).read()
        xml_data2 = xml_data2.format(slot_name=slot_name)

        STARTUP.STORE_DATA('\n> user-rpc\n', Format=True, PDF=pdf)
        STARTUP.STORE_DATA('******* Replace with below xml ********', Format=True, PDF=pdf)
        STARTUP.STORE_DATA(xml_data2, Format='XML', PDF=pdf)
        d3 = self.session.dispatch(to_ele(xml_data2))

        ###############################################################################
        ## Test Procedure 2 : O-RU NETCONF Server responds with <software-activate>
        ###############################################################################
        Test_Step2 = '\t\tStep 2 : O-RU NETCONF Server responds with <rpc-reply><software-activate><status>. The parameter "status" is set to STARTED.'
        STARTUP.STORE_DATA('{}'.format(Test_Step2),Format='TEST_STEP', PDF=pdf)
        STARTUP.STORE_DATA('{}'.format(d3), Format='XML', PDF=pdf)

        ###############################################################################
        ## Capture_The_Notifications
        ###############################################################################
        while True:
            n = self.session.take_notification(timeout=60)
            if n == None:
                break
            notify = n.notification_xml
            dict_n = xmltodict.parse(str(notify))
            try:
                notf = dict_n['notification']['activation-event']
                if notf:
                    Test_Step3 = '\t\tStep 3 : O-RU NETCONF Server sends <notification><activation-event> with a status COMPLETED.'
                    STARTUP.STORE_DATA('{}'.format(
                        Test_Step3), Format='TEST_STEP', PDF=pdf)
                    x = xml.dom.minidom.parseString(notify)
                    xml_pretty_str = x.toprettyxml()
                    STARTUP.STORE_DATA(
                        xml_pretty_str, Format='XML', PDF=pdf)
                    status = dict_n['notification']['activation-event']['status']
                    if status != 'COMPLETED':
                        return status
                    break
            except:
                pass

        ###############################################################################
        ## POST_GET_FILTER
        ###############################################################################
        time.sleep(5)
        pdf.add_page()
        STARTUP.STORE_DATA(
            '\n> get --filter-xpath /o-ran-software-management:software-inventory', Format=True, PDF=pdf)
        sw_inv = '''<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                    <software-inventory xmlns="urn:o-ran:software-management:1.0">
                    </software-inventory>
                    </filter>'''
        slot_names1 = self.session.get(sw_inv).data_xml
        s = xml.dom.minidom.parseString(slot_names1)
        xml_pretty_str = s.toprettyxml()
        self.RU_Details[1].pop(slot_name)
        slot_n1 = xmltodict.parse(str(slot_names1))
        SLOTS1 = slot_n1['data']['software-inventory']['software-slot']
        for slot in SLOTS1:
            if slot['status'] == 'INVALID':
                STARTUP.STORE_DATA(
                    xml_pretty_str, Format='XML', PDF=pdf)
                return f'SW slot status is Invid for {SLOT["name"]}...'
            if slot['name'] == slot_name:
                if (slot['active'] == 'true') and slot['running'] == 'false':
                    pass
                else:
                    STARTUP.STORE_DATA(
                        xml_pretty_str, Format='XML', PDF=pdf)
                    return f"SW Inventory didn't update for {slot_name}..."

            if slot['name'] == DEACTIVE_SLOT[0]:
                if (slot['active'] != 'false') and slot['running'] != 'true':
                    STARTUP.STORE_DATA(
                        xml_pretty_str, Format='XML', PDF=pdf)
                    return f"SW Inventory didn't update for {slot['name'] }..."
        STARTUP.STORE_DATA(xml_pretty_str, Format='XML', PDF=pdf)
        return True

                
    ###############################################################################
    ## Main Function
    ###############################################################################
    def test_Main_016(self):
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
            self.session = STARTUP.call_home(host = '0.0.0.0', port=4334, hostkey_verify=False,username = self.USER_N, password = self.PSWRD,timeout = 60,allow_agent = False , look_for_keys = False)
            self.hostname, self.call_home_port = self.session._session._transport.sock.getpeername()   #['ip_address', 'TCP_Port']
            
            if self.session:
                self.RU_Details = STARTUP.demo(session = self.session,host= self.hostname, port= 830)
                for key, val in self.RU_Details[1].items():
                    if val[0] == 'true' and val[1] == 'true':
                        ###############################################################################
                        ## Test Description
                        ###############################################################################
                        Test_Desc = 'Test Description : The minimum functions of the TER described in section 2.1 that support validation of the M-Plane are operational, configured and connected to the O-RU'
                        CONFIDENTIAL = STARTUP.ADD_CONFIDENTIAL('16', SW_R=val[2])
                        STARTUP.STORE_DATA(CONFIDENTIAL, Format='CONF', PDF=pdf)
                        STARTUP.STORE_DATA(Test_Desc, Format='DESC', PDF=pdf)
                        pdf.add_page()

                del self.RU_Details[1]['swRecoverySlot']
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
        
        

def test_m_ctc_id_016():
    tc016_obj = M_CTC_ID_016()
    Check = tc016_obj.test_Main_016()
    if Check == False:
        STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
        STARTUP.STORE_DATA('SFP link not detected...',Format=False,PDF= pdf)
        STARTUP.ACT_RES(f"{'O-RU Software Activate without reset' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(255,0,0))
        return False
    ###############################################################################
    ## Expected/Actual Result
    ###############################################################################
    STARTUP.GET_SYSTEM_LOGS(tc016_obj.hostname,tc016_obj.USER_N,tc016_obj.PSWRD,pdf)
    Exp_Result = 'Expected Result : \n 1. The O-RU NETCONF Server performs a software activation procedure. When the procedure is completed, the O-RU NETCONF Server sends <notification><activation-event> with a status COMPLETED and the slot-name in the activation event corresponds to the slot-name used in the software-activate RPC to the TER NETCONF Client.\n 2. Status of the software slot containing the software still used by device remains VALID, the parameter "active" is set to False. The parameter "running" is True.'
    STARTUP.STORE_DATA(Exp_Result, Format='DESC', PDF=pdf)

    STARTUP.STORE_DATA('\t\t{}'.format('****************** Actual Result ******************'), Format=True, PDF=pdf)
    try:
        if Check == True:
            STARTUP.ACT_RES(f"{'O-RU Software Activate without reset' : <50}{'=' : ^20}{'SUCCESS' : ^20}",PDF= pdf,COL=(0,255,0))
            return True

        elif type(Check) == list:
            STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
            Error_Info = '''ERROR\n\terror-type \t: \t{}\n\terror-tag \t: \t{}\n\terror-severity \t: \t{}\n\tmessage' \t: \t{}'''.format(*map(str,Check))
            STARTUP.STORE_DATA(Error_Info,Format=False,PDF= pdf)
            STARTUP.ACT_RES(f"{'O-RU Software Activate without reset' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(255,0,0))
            return False
        else:
            STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
            STARTUP.STORE_DATA('{}'.format(Check),Format=False,PDF= pdf)
            STARTUP.ACT_RES(f"{'O-RU Software Activate without reset' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(255,0,0))
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
        STARTUP.CREATE_LOGS('M_CTC_ID_016',PDF=pdf)


if __name__ == "__main__":
    test_m_ctc_id_016()
    pass
