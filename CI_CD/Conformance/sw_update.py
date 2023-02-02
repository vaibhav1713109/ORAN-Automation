###############################################################################
##@ FILE NAME:      M_CTC_ID_014
##@ TEST SCOPE:     M PLANE O-RAN CONFORMANCE \n
##@ Version:        V_1.0.0
##@ Support:        @Ramiyer, @VaibhavDhiman, @PriyaSharma
###############################################################################

###############################################################################
## Package Imports 
###############################################################################

import socket, sys, os, time, xmltodict, xml.dom.minidom, paramiko, subprocess
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
from require import STARTUP

###############################################################################
## Initiate PDF
###############################################################################
pdf = STARTUP.PDF_CAP()
summary = []

class Firmware_Upgrade(vlan_Creation):
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
        self.sw_inv = '''<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            <software-inventory xmlns="urn:o-ran:software-management:1.0">
            </software-inventory>
            </filter>'''

    ###############################################################################
    ## Test Procedure
    ###############################################################################
    def netopeer_connection_and_capability(self):
        try:
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
            filter = """<filter type="xpath" xmlns="urn:ietf:params:xml:ns:netconf:notification:1.0" xmlns:swm="urn:o-ran:software-management:1.0" select="/swm:*"/>"""
            cap=self.session.create_subscription(filter=filter)
            STARTUP.STORE_DATA('> subscribe', Format=True, PDF=pdf)
            dict_data = xmltodict.parse(str(cap))
            if dict_data['nc:rpc-reply']['nc:ok'] == None:
                STARTUP.STORE_DATA('\nOk\n', Format=False, PDF=pdf)
            summary.append('Netopeer Connection, capability exchange and create-subscription completed!!')
            return True

        except Exception as e:
            STARTUP.STORE_DATA('{}'.format(e), Format=True,PDF=pdf)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
            return f"{e} Subscribe and Capability Exchange"
        
    def software_download(self):
        try:
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
            slot_names = self.session.get(self.sw_inv).data_xml

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
            xml_data = xml_data.format(rmt_path=self.rmt, password=self.du_pswrd, public_key=pub_key)

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
            summary.append('Software download process completed!!')
            return True

        except Exception as e:
            STARTUP.STORE_DATA('{}'.format(e), Format=True,PDF=pdf)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
            return f"{e} Software Download"

    def software_install(self):
        try:
            ###############################################################################
            ## Test Procedure 2 : Configure_SW_Install_RPC
            ###############################################################################
            Test_Step3 = '\t\tStep 3 : TER NETCONF Client triggers <rpc><software-install> Slot must have attributes active = FALSE, running = FALSE.'
                    
            ###############################################################################
            ## Install_at_the_slot_Which_Have_False_Status
            ###############################################################################
            xml_data2 = open("{}/require/Yang_xml/sw_install.xml".format(parent)).read()
            file_path = self.rmt
            li = file_path.split(':22/')
            xml_data2 = xml_data2.format(slot_name=self.inactive_slot,File_name = '/{}'.format(li[1]))
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
            slot_names = self.session.get(self.sw_inv).data_xml

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

                elif (SLOT['name'] != 'swRecoverySlot'):
                    SLOT_INFO[SLOT['name']] = [SLOT['active'], SLOT['running']]

                elif (SLOT['active'] == 'true' and SLOT['running'] == 'true') or (SLOT['active'] == 'false' and SLOT['running'] == 'false'):
                    if (SLOT['active'] == 'false' and SLOT['running'] == 'false') and (SLOT['name'] != 'swRecoverySlot'):
                        self.slot_name = SLOT['name']
                        del SLOT_INFO[SLOT['name']]
                    pass
                else:
                    return f'Slots Active and Running Status are diffrent for {SLOT["name"]}...'
            summary.append('Software install process completed!!')
            return True
        
        except Exception as e:
            STARTUP.STORE_DATA('{}'.format(e), Format=True,PDF=pdf)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
            return f"{e} Software Install"
        
    def software_activate(self):
        try:
            ###############################################################################
            ## Test Procedure 3 : Configure SW Activate RPC in RU
            ###############################################################################
            Test_Step1 = '\t\tStep 5 : TER NETCONF Client triggers <rpc><software-activate> Slot must have attributes active = FALSE, running = FALSE.'
            STARTUP.STORE_DATA('{}'.format(Test_Step1), Format='TEST_STEP', PDF=pdf)
            xml_data2 = open("{}/require/Yang_xml/sw_activate.xml".format(parent)).read()
            xml_data2 = xml_data2.format(slot_name=self.slot_name)

            STARTUP.STORE_DATA('\n> user-rpc\n', Format=True, PDF=pdf)
            STARTUP.STORE_DATA('******* Replace with below xml ********', Format=True, PDF=pdf)
            STARTUP.STORE_DATA(xml_data2, Format='XML', PDF=pdf)
            d3 = self.session.dispatch(to_ele(xml_data2))

            ###############################################################################
            ## Test Procedure 4 : O-RU NETCONF Server responds with <software-activate>
            ###############################################################################
            Test_Step2 = '\t\tStep 6 : O-RU NETCONF Server responds with <rpc-reply><software-activate><status>. The parameter "status" is set to STARTED.'
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
            self.RU_Details[1].pop(self.slot_name)
            slot_n1 = xmltodict.parse(str(slot_names1))
            SLOTS1 = slot_n1['data']['software-inventory']['software-slot']
            for slot in SLOTS1:
                if slot['status'] == 'INVALID':
                    STARTUP.STORE_DATA(
                        xml_pretty_str, Format='XML', PDF=pdf)
                    return f'SW slot status is Invid for {slot["name"]}...'
                if slot['name'] == self.slot_name:
                    if (slot['active'] == 'true') and slot['running'] == 'false':
                        pass
                    else:
                        STARTUP.STORE_DATA(
                            xml_pretty_str, Format='XML', PDF=pdf)
                        return f"SW Inventory didn't update for {self.slot_name}..."

                if slot['name'] == self.inactive_slot:
                    if (slot['active'] != 'false') and slot['running'] != 'true':
                        STARTUP.STORE_DATA(
                            xml_pretty_str, Format='XML', PDF=pdf)
                        return f"SW Inventory didn't update for {slot['name'] }..."
            STARTUP.STORE_DATA(xml_pretty_str, Format='XML', PDF=pdf)
            summary.append('Software activate process completed!!')
            return True
        except Exception as e:
            STARTUP.STORE_DATA('{}'.format(e), Format=True,PDF=pdf)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
            return "{e} Software Activate"

    def reset_rpc(self):
        ###############################################################################
        ## Test Procedure 1 : Configure_Reset_RPC_in_RU
        ###############################################################################
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
        summary.append('RU going for reboot!!')
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
                    summary.append('Software Successfully update!!')
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
    ## Gather system logs
    ###############################################################################
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
                pass
        else:
            print('Can\'t connect to the RU.., Logs are not captured.')
            return False

    ###############################################################################
    ## Befor_Reset
    ###############################################################################
    def Befor_Reset(self):
        summary.append('Firmware Upgrade process start!!')
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
            self.session, self.login_info = STARTUP.session_login(host = self.hostname,USER_N = self.USER_N,PSWRD = self.PSWRD)

            if self.session:
                self.RU_Details = STARTUP.demo(session = self.session,host= self.hostname, port= 830)
                del self.RU_Details[1]['swRecoverySlot']

                for key, val in self.RU_Details[1].items():
                    if val[0] == 'true' and val[1] == 'true':
                        ###############################################################################
                        ## Test Description
                        ###############################################################################
                        Test_Desc = 'Test Description :  This test validates that the O-RU can successfully perform a software download and software install procedure.'
                        CONFIDENTIAL = STARTUP.ADD_CONFIDENTIAL('Firmware_Upgrade',SW_R = val[2]) 
                        STARTUP.STORE_DATA(CONFIDENTIAL,Format='CONF',PDF= pdf)
                        STARTUP.STORE_DATA(Test_Desc,Format='DESC',PDF= pdf)
                        pdf.add_page()
                    else:
                        self.inactive_slot = key
                Res1 = self.netopeer_connection_and_capability()
                if Res1 != True:
                    return Res1
                Res2 = self.software_download()
                if Res2 != True:
                    return Res2
                Res3 = self.software_install()
                if Res3 != True:
                    return Res3
                Res4 = self.software_activate()
                if Res4 != True:
                    return Res4
            
                
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
            self.logs1 = self.system_logs(self.hostname)
            try:
                self.session.close_session()
            except Exception as e:
                print(e)

    ###############################################################################
    ## After_reset
    ###############################################################################
    def after_reset(self):
        time.sleep(40)
        Res5 = self.get_config_detail()
        self.logs2 = self.system_logs(self.hostname)
        if Res5 != True:
            return Res5
        pass
    
    ###############################################################################
    ## Main Function
    ###############################################################################
    def Main_fw_upgrade(self):
        Check1 = self.Befor_Reset()
        if Check1 == False:
            STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
            STARTUP.STORE_DATA('SFP link not detected...',Format=False,PDF= pdf)
            STARTUP.ACT_RES(f"{'O-RU Software Update and Install' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(255,0,0))
            return False

        elif Check1 == True:
            Check2 = self.after_reset()
            STARTUP.STORE_DATA('\t\t\t\t############ SYSTEM LOGS ##############',Format=True,PDF=pdf)
            for i in self.logs1:
                STARTUP.STORE_DATA("{}".format(i),Format=False,PDF=pdf)
            for i in self.logs2:
                STARTUP.STORE_DATA("{}".format(i),Format=False,PDF=pdf)
            ###############################################################################
            ## Expected/Actual Result
            ###############################################################################
            Exp_Result = 'Expected Result : The O-RU NETCONF Server sends <notification><install-event><status> to the TER NETCONF Client. Field <status> contains the value COMPLETED to indicate the successful installation of software to the desired slot.'
            STARTUP.STORE_DATA(Exp_Result,Format='DESC',PDF= pdf)

            STARTUP.STORE_DATA('\t\t{}'.format('****************** Actual Result ******************'),Format=True,PDF= pdf)
            try:
                if Check2 == True:
                    STARTUP.ACT_RES(f"{'Supplemental Reset after Software Activation' : <50}{'=' : ^20}{'SUCCESS' : ^20}",PDF= pdf,COL=(0,255,0))
                    return True

                else:
                    if type(Check2) == list:
                        STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
                        Error_Info = '''ERROR\n\terror-type \t: \t{}\n\terror-tag \t: \t{}\n\terror-severity \t: \t{}\n\tmessage' \t: \t{}'''.format(*map(str,Check2))
                        STARTUP.STORE_DATA(Error_Info,Format=False,PDF= pdf)
                        STARTUP.ACT_RES(f"{'Supplemental Reset after Software Activation' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(255,0,0))
                        return False

                    else:
                        STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
                        STARTUP.STORE_DATA('{}'.format(Check2),Format=False,PDF= pdf)
                        STARTUP.ACT_RES(f"{'Supplemental Reset after Software Activation' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(255,0,0))
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
                STARTUP.CREATE_LOGS('Firmware_Upgrade',PDF=pdf)

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
                    return False
                else:
                    STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
                    STARTUP.STORE_DATA('{}'.format(Check1),Format=False,PDF= pdf)
                    STARTUP.ACT_RES(f"{'Supplemental Reset after Software Activation' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(255,0,0))
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
                STARTUP.CREATE_LOGS('Firmware_Upgrade',PDF=pdf)


if __name__ == "__main__":
    fw_upgrade = Firmware_Upgrade()
    fw_upgrade.Main_fw_upgrade()
    pass

