###############################################################################
##@ FILE NAME:      M_CTC_ID_014
##@ TEST SCOPE:     M PLANE O-RAN CONFORMANCE \n
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

class M_CTC_ID_014(vlan_Creation):
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
        ## Fetch Public Key of Linux PC
        ###############################################################################
        pub_k = subprocess.getoutput('cat /etc/ssh/ssh_host_rsa_key.pub')
        pk = pub_k.split()
        pub_key = pk[1]


        ###############################################################################
        ## Initial Get Filter
        ###############################################################################
        pdf.add_page()
        STARTUP.STORE_DATA('\t\tInitial Get Filter',Format='TEST_STEP',PDF=pdf)
        STARTUP.STORE_DATA('\n> get --filter-xpath /o-ran-software-management:software-inventory', Format=True,PDF=pdf)
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
        slots_info = slot_n['data']['software-inventory']['software-slot']
        for i in slots_info:
            if i['status'] == 'INVALID':
                STARTUP.STORE_DATA(xml_pretty_str, Format='XML',PDF=pdf)
                return 'SW slot status is Invalid...'
            if (i['active'] == 'false' and i['running'] == 'false') or (i['active'] == 'true' and i['running'] == 'true'):
                pass
            else:
                return 'Slots Active and Running Status are diffrent...'

        STARTUP.STORE_DATA(xml_pretty_str, Format='XML',PDF=pdf)
        


                
        ###############################################################################
        ## Configure SW Download RPC in RU
        ###############################################################################
        xml_data = open("{}/require/Yang_xml/sw_download.xml".format(parent)).read()
        xml_data = xml_data.format(
            rmt_path=self.rmt, password=self.du_pswrd, public_key=pub_key)

        ###############################################################################
        ## Test Procedure 1
        ###############################################################################
        Test_Step1 = '\t\tStep 1 : TER NETCONF Client triggers <rpc><software-download>'
        STARTUP.STORE_DATA('{}'.format(Test_Step1), Format='TEST_STEP',PDF=pdf)
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
        pdf.add_page()
        Test_Step2 = '\t\tStep 2 :  O-RU NETCONF Server sends <notification><download-event> with status COMPLETED to TER NETCONF Client'
        STARTUP.STORE_DATA('{}'.format(Test_Step2),Format='TEST_STEP',PDF=pdf)

        while True:
            n = self.session.take_notification(timeout = 60)
            if n == None:
                break
            notify = n.notification_xml
            dict_n = xmltodict.parse(str(notify))
            try:
                notf = dict_n['notification']['download-event']
                if notf:
                    x = xml.dom.minidom.parseString(notify)
                    xml_pretty_str = x.toprettyxml()
                    STARTUP.STORE_DATA(xml_pretty_str, Format='XML',PDF=pdf)
                    status = dict_n['notification']['download-event']['status']
                    if status != 'COMPLETED':
                        return status
                    break
            except:
                pass

         
        ###############################################################################
        ## Test Procedure 2 : Configure_SW_Install_RPC
        ###############################################################################
        Test_Step3 = '\t\tStep 3 : TER NETCONF Client triggers <rpc><software-install> Slot must have attributes active = FALSE, running = FALSE.'
        STARTUP.STORE_DATA(
            '{}'.format(Test_Step3), Format='TEST_STEP',PDF=pdf)
        STARTUP.STORE_DATA(f"{'SR_NO' : <20}{'Slot_Name' : <20}{'|' : ^10}{'Active': ^10}{'Running': ^10}", Format=True,PDF=pdf)
        k = 1
        for key, val in self.RU_Details[1].items():
            STARTUP.STORE_DATA (f"{k : <20}{key : <20}{'=' : ^10}{val[0]: ^10}{val[1]: ^10}\n", Format=False,PDF=pdf)
            k += 1
                
                
        ###############################################################################
        ## Install_at_the_slot_Which_Have_False_Status
        ###############################################################################
        for key, val in self.RU_Details[1].items():
            if val[0] == 'false' and val[1] == 'false':
                xml_data2 = open("{}/require/Yang_xml/sw_install.xml".format(parent)).read()
                file_path = self.rmt
                li = file_path.split(':22/')
                xml_data2 = xml_data2.format(slot_name=key,File_name = '/{}'.format(li[1]))
                STARTUP.STORE_DATA('\n> user-rpc\n',Format=True,PDF=pdf)
                STARTUP.STORE_DATA('******* Replace with below xml ********', Format=True,PDF=pdf)
                STARTUP.STORE_DATA(xml_data2, Format='XML',PDF=pdf)
                d1 = self.session.dispatch(to_ele(xml_data2))
                STARTUP.STORE_DATA('******* RPC Reply ********', Format=True,PDF=pdf)
                STARTUP.STORE_DATA('{}'.format(d1), Format='XML',PDF=pdf)


        ###############################################################################
        ## Test Procedure 4 and 5 : Capture_The_Notifications
        ###############################################################################
        Test_Step4 = '\t\tStep 4 and 5 :  O-RU NETCONF Server sends <notification><install-event> with status COMPLETED to TER NETCONF Client'
        STARTUP.STORE_DATA('{}'.format(Test_Step4), Format='TEST_STEP',PDF=pdf)
        while True:
            n = self.session.take_notification(timeout=60)
            if n == None:
                break
            notify = n.notification_xml
            dict_n = xmltodict.parse(str(notify))
            try:
                notf = dict_n['notification']['install-event']
                if notf:
                    x = xml.dom.minidom.parseString(notify)
                    xml_pretty_str = x.toprettyxml()
                    STARTUP.STORE_DATA(xml_pretty_str, Format='XML',PDF=pdf)
                    status = dict_n['notification']['install-event']['status']
                    if status != 'COMPLETED':
                        return status
                    break
            except:
                pass


        ###############################################################################
        ## POST_GET_FILTER
        ###############################################################################            
        pdf.add_page()
        STARTUP.STORE_DATA('\t\t POST GET AFTER INSTALL SW', Format='TEST_STEP',PDF=pdf)
        STARTUP.STORE_DATA('\n> get --filter-xpath /o-ran-software-management:software-inventory', Format=True,PDF=pdf)
        sw_inv = '''<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
        <software-inventory xmlns="urn:o-ran:software-management:1.0">
        </software-inventory>
        </filter>'''
        slot_names = self.session.get(sw_inv).data_xml
        s = xml.dom.minidom.parseString(slot_names)
        xml_pretty_str = s.toprettyxml()
        slots_info = slot_n['data']['software-inventory']['software-slot']
        for i in slots_info:
            if i['status'] == 'INVALID':
                STARTUP.STORE_DATA(
                    xml_pretty_str, Format='XML',PDF=pdf)
                return 'SW slot status is Invalid...'
            if (i['active'] == 'false' and i['running'] == 'false') or (i['active'] == 'true' and i['running'] == 'true'):
                pass
            else:
                return 'Slots Active and Running Status are diffrent...'
        STARTUP.STORE_DATA(xml_pretty_str, Format='XML',PDF=pdf)
        return True


    ###############################################################################
    ## Main Function
    ###############################################################################
    def test_Main_014(self):
        Check1 = self.linked_detected()
        
        
        ###############################################################################
        ## Read User Name and password from Config.INI of Config.py
        ###############################################################################
        self.rmt = configur.get('INFO','sw_path')
        self.du_pswrd = configur.get('INFO','du_pass')
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
            self.session = STARTUP.call_home(host = '0.0.0.0', port=4334, hostkey_verify=False,username = self.USER_N, password = self.PSWRD,timeout = 60,allow_agent = False , look_for_keys = False)
            self.hostname, self.call_home_port = self.session._session._transport.sock.getpeername()   #['ip_address', 'TCP_Port']
            
            if self.session:
                self.RU_Details = STARTUP.demo(session = self.session,host= self.hostname, port= 830)

                for key, val in self.RU_Details[1].items():
                    if val[0] == 'true' and val[1] == 'true':
                        ###############################################################################
                        ## Test Description
                        ###############################################################################
                        Test_Desc = 'Test Description :  This test validates that the O-RU can successfully perform a software download and software install procedure.'
                        CONFIDENTIAL = STARTUP.ADD_CONFIDENTIAL('14',SW_R = val[2]) 
                        STARTUP.STORE_DATA(CONFIDENTIAL,Format='CONF',PDF= pdf)
                        STARTUP.STORE_DATA(Test_Desc,Format='DESC',PDF= pdf)
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

        
def test_m_ctc_id_014():
    tc014_obj = M_CTC_ID_014()
    Check = tc014_obj.test_Main_014()
    if Check == False:
        STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
        STARTUP.STORE_DATA('SFP link not detected...',Format=False,PDF= pdf)
        STARTUP.ACT_RES(f"{'O-RU Software Update and Install' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(255,0,0))
        return False
    
    ###############################################################################
    ## Expected/Actual Result
    ###############################################################################
    STARTUP.GET_SYSTEM_LOGS(tc014_obj.hostname,tc014_obj.USER_N,tc014_obj.PSWRD,pdf)
    Exp_Result = 'Expected Result : The O-RU NETCONF Server sends <notification><install-event><status> to the TER NETCONF Client. Field <status> contains the value COMPLETED to indicate the successful installation of software to the desired slot.'
    STARTUP.STORE_DATA(Exp_Result,Format='DESC',PDF= pdf)

    STARTUP.STORE_DATA('\t\t{}'.format('****************** Actual Result ******************'),Format=True,PDF= pdf)
    try:
        if Check == True:
            STARTUP.ACT_RES(f"{'O-RU Software Update and Install' : <50}{'=' : ^20}{'SUCCESS' : ^20}",PDF= pdf,COL=(0,255,0))
            return True

        elif type(Check) == list:
            STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
            Error_Info = '''ERROR\n\terror-type \t: \t{}\n\terror-tag \t: \t{}\n\terror-severity \t: \t{}\n\tmessage' \t: \t{}'''.format(*map(str,Check))
            STARTUP.STORE_DATA(Error_Info,Format=False,PDF= pdf)
            STARTUP.ACT_RES(f"{'O-RU Software Update and Install' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(255,0,0))
            return False
        else:
            STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
            STARTUP.STORE_DATA('{}'.format(Check),Format=False,PDF= pdf)
            STARTUP.ACT_RES(f"{'O-RU Software Update and Install' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(255,0,0))
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
        STARTUP.CREATE_LOGS('M_CTC_ID_014',PDF=pdf)


if __name__ == "__main__":
    test_m_ctc_id_014()
    pass
