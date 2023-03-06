###############################################################################
##@ FILE NAME:      Software Update
##@ TEST SCOPE:     M PLANE O-RAN CONFORMANCE
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
configur.read('{}/require/inputs.ini'.format(parent))

###############################################################################
## Related Imports
###############################################################################
from require.Notification import *
# from require.Vlan_Creation import *
from require.LINK_DETECTED import *
from require import STARTUP

###############################################################################
## Initiate PDF
###############################################################################

class Firmware_Upgrade(Link_Detect):
    # init method or constructor 
    def __init__(self):
        super().__init__()
        self.summary = []
        self.pdf = STARTUP.PDF_CAP()
        self.hostname, self.call_home_port = '',''
        self.USER_N = ''
        self.PSWRD = ''
        self.session = ''
        self.rmt = ''
        self.sftp_pass = ''
        self.RU_Details = ''
        self.logs1,self.logs2 = '',''
        self.sw_inv = '''<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            <software-inventory xmlns="urn:o-ran:software-management:1.0">
            </software-inventory>
            </filter>'''

    ###############################################################################
    ## Test Procedure
    ###############################################################################
    def netopeer_connection_and_capability(self):
        try:
            STARTUP.STORE_DATA('\n\n\t\t********** Connect to the NETCONF Server ***********\n\n',Format='TEST_STEP',PDF = self.pdf)
            STARTUP.STORE_DATA(self.login_info,Format=False,PDF = self.pdf)
            STATUS = STARTUP.STATUS(self.hostname,self.USER_N,self.session.session_id,830)
            STARTUP.STORE_DATA(STATUS,Format=False,PDF = self.pdf)


            ###############################################################################
            ## Server Capabilities
            ###############################################################################
            for cap in self.session.server_capabilities:
                STARTUP.STORE_DATA("\t{}".format(cap),Format=False,PDF = self.pdf)
            STARTUP.append_data_and_print('Capability exchange || Successful',self.summary)

            ###############################################################################
            ## Create_subscription
            ###############################################################################
            filter = """<filter type="xpath" xmlns="urn:ietf:params:xml:ns:netconf:notification:1.0" xmlns:swm="urn:o-ran:software-management:1.0" select="/swm:*"/>"""
            cap=self.session.create_subscription(filter=filter)
            STARTUP.STORE_DATA('> subscribe --filter-xpath /o-ran-software-management:*', Format=True, PDF=self.pdf)
            dict_data = xmltodict.parse(str(cap))
            if dict_data['nc:rpc-reply']['nc:ok'] == None:
                STARTUP.STORE_DATA('\nOk\n', Format=False, PDF=self.pdf)
            STARTUP.append_data_and_print('Create-subscription || Successful!!',self.summary)
            return True

        except Exception as e:
            STARTUP.STORE_DATA('{}'.format(e), Format=True,PDF=self.pdf)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=self.pdf)
            return f"{e} Subscribe and Capability Exchange"
        
    def software_download(self):
        try:
            print(f'{"-"*100}\nConfiguring SW Download RPC!!')
            ###############################################################################
            ## Fetch Public Key of Linux PC
            ###############################################################################
            pub_k = subprocess.getoutput('cat /etc/ssh/ssh_host_rsa_key.pub')
            pk = pub_k.split()
            pub_key = pk[1]

            ###############################################################################
            ## Initial Get Filter
            ###############################################################################
            self.pdf.add_page()
            STARTUP.STORE_DATA('\t\tInitial Get Filter',Format='TEST_STEP',PDF=self.pdf)
            STARTUP.STORE_DATA('\n> get --filter-xpath /o-ran-software-management:software-inventory', Format=True,PDF=self.pdf)
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
                    STARTUP.STORE_DATA(xml_pretty_str, Format='XML',PDF=self.pdf)
                    return 'SW slot status is Invalid...'
                if (i['active'] == 'false' and i['running'] == 'false') or (i['active'] == 'true' and i['running'] == 'true'):
                    pass
                else:
                    return 'Slots Active and Running Status are diffrent...'
            STARTUP.STORE_DATA(xml_pretty_str, Format='XML',PDF=self.pdf)
            
            ###############################################################################
            ## Configure SW Download RPC in RU
            ###############################################################################
            xml_data = open("{}/require/Yang_xml/sw_download.xml".format(parent)).read()
            xml_data = xml_data.format(rmt_path=self.rmt, password=self.sftp_pass, public_key=pub_key)

            ###############################################################################
            ## Test Procedure 1
            ###############################################################################
            Test_Step1 = '\t\tStep 1 : TER NETCONF Client triggers <rpc><software-download>'
            STARTUP.STORE_DATA('{}'.format(Test_Step1), Format='TEST_STEP',PDF=self.pdf)
            STARTUP.STORE_DATA('\n> user-rpc\n', Format=True,PDF=self.pdf)

            STARTUP.STORE_DATA('\t\t******* Replace with below xml ********', Format=True,PDF=self.pdf)
            STARTUP.STORE_DATA(xml_data, Format='XML',PDF=self.pdf)
            rpc_command = to_ele(xml_data)
            rpc_reply = self.session.rpc(rpc_command)
            if 'FAILED' in str(rpc_reply):
                return rpc_reply

            STARTUP.STORE_DATA('******* RPC Reply ********',Format=True,PDF=self.pdf)
            STARTUP.STORE_DATA('{}'.format(rpc_reply), Format='XML',PDF=self.pdf)

            ###############################################################################
            ## Test Procedure 2 : Capture_The_Notifications
            ###############################################################################
            self.pdf.add_page()
            Test_Step2 = '\t\tStep 2 :  O-RU NETCONF Server sends <notification><download-event> with status COMPLETED to TER NETCONF Client'
            STARTUP.STORE_DATA('{}'.format(Test_Step2),Format='TEST_STEP',PDF=self.pdf)

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
                        STARTUP.STORE_DATA(xml_pretty_str, Format='XML',PDF=self.pdf)
                        status = dict_n['notification']['download-event']['status']
                        if status != 'COMPLETED':
                            return status
                        break
                except:
                    pass
            STARTUP.append_data_and_print(f'Software File Download || {self.flash_image} Successful!!',self.summary)
            return True

        except Exception as e:
            STARTUP.STORE_DATA('{}'.format(e), Format=True,PDF=self.pdf)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=self.pdf)
            return f"{e} Software Download"

    def software_install(self):
        try:
            print(f'{"-"*100}\nConfiguring SW Install RPC!!')
            ###############################################################################
            ## Test Procedure 2 : Configure_SW_Install_RPC
            ###############################################################################
            Test_Step3 = '\t\tStep 3 : TER NETCONF Client triggers <rpc><software-install> Slot must have attributes active = FALSE, running = FALSE.'
            STARTUP.STORE_DATA('{}'.format(Test_Step3), Format='TEST_STEP',PDF=self.pdf)
            ###############################################################################
            ## Install_at_the_slot_Which_Have_False_Status
            ###############################################################################
            xml_data2 = open("{}/require/Yang_xml/sw_install.xml".format(parent)).read()
            file_path = self.rmt
            li = file_path.split(':22/')
            xml_data2 = xml_data2.format(slot_name=self.inactive_slot,File_name = '/{}'.format(li[1]))
            STARTUP.STORE_DATA('\n> user-rpc\n',Format=True,PDF=self.pdf)
            STARTUP.STORE_DATA('******* Replace with below xml ********', Format=True,PDF=self.pdf)
            STARTUP.STORE_DATA(xml_data2, Format='XML',PDF=self.pdf)
            rpc_reply = self.session.dispatch(to_ele(xml_data2))
            if 'FAILED' in str(rpc_reply):
                return rpc_reply
            STARTUP.STORE_DATA('******* RPC Reply ********', Format=True,PDF=self.pdf)
            STARTUP.STORE_DATA('{}'.format(rpc_reply), Format='XML',PDF=self.pdf)


            ###############################################################################
            ## Test Procedure 4 and 5 : Capture_The_Notifications
            ###############################################################################
            Test_Step4 = '\t\tStep 4 and 5 :  O-RU NETCONF Server sends <notification><install-event> with status COMPLETED to TER NETCONF Client'
            STARTUP.STORE_DATA('{}'.format(Test_Step4), Format='TEST_STEP',PDF=self.pdf)
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
                        STARTUP.STORE_DATA(xml_pretty_str, Format='XML',PDF=self.pdf)
                        status = dict_n['notification']['install-event']['status']
                        if status != 'COMPLETED':
                            return status
                        break
                except:
                    pass


            ###############################################################################
            ## POST_GET_FILTER
            ###############################################################################            
            self.pdf.add_page()
            STARTUP.STORE_DATA('\t\t POST GET AFTER INSTALL SW', Format='TEST_STEP',PDF=self.pdf)
            STARTUP.STORE_DATA('\n> get --filter-xpath /o-ran-software-management:software-inventory', Format=True,PDF=self.pdf)
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
                    STARTUP.STORE_DATA(xml_pretty_str, Format='XML', PDF=self.pdf)
                    return f'SW slot status is Invalid for {SLOT["name"]}...'

                elif (SLOT['name'] != 'swRecoverySlot'):
                    SLOT_INFO[SLOT['name']] = [SLOT['active'], SLOT['running']]

                elif (SLOT['active'] == 'true' and SLOT['running'] == 'true') or (SLOT['active'] == 'false' and SLOT['running'] == 'false'):
                    if (SLOT['active'] == 'false' and SLOT['running'] == 'false') and (SLOT['name'] != 'swRecoverySlot'):
                        self.inactive_slot = SLOT['name']
                        del SLOT_INFO[SLOT['name']]
                    pass
                else:
                    return f'Slots Active and Running Status are diffrent for {SLOT["name"]}...'
            STARTUP.STORE_DATA(xml_pretty_str, Format='XML', PDF=self.pdf)
            STARTUP.append_data_and_print(f'Software {self.flash_image} Install || Successfully install on {self.inactive_slot}!!',self.summary)
            return True
        
        except Exception as e:
            STARTUP.STORE_DATA('{}'.format(e), Format=True,PDF=self.pdf)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=self.pdf)
            return f"{e} Software Install"
        
    def software_activate(self):
        try:
            STARTUP.append_data_and_print(f'Running Software || {self.running_sw}!!',self.summary)
            print(f'{"-"*100}\nConfiguring SW Activate RPC!!')
            ###############################################################################
            ## Test Procedure 3 : Configure SW Activate RPC in RU
            ###############################################################################
            Test_Step1 = '\t\tStep 5 : TER NETCONF Client triggers <rpc><software-activate> Slot must have attributes active = FALSE, running = FALSE.'
            STARTUP.STORE_DATA('{}'.format(Test_Step1), Format='TEST_STEP', PDF=self.pdf)
            xml_data2 = open("{}/require/Yang_xml/sw_activate.xml".format(parent)).read()
            xml_data2 = xml_data2.format(slot_name=self.inactive_slot)

            STARTUP.STORE_DATA('\n> user-rpc\n', Format=True, PDF=self.pdf)
            STARTUP.STORE_DATA('******* Replace with below xml ********', Format=True, PDF=self.pdf)
            STARTUP.STORE_DATA(xml_data2, Format='XML', PDF=self.pdf)
            rpc_reply = self.session.dispatch(to_ele(xml_data2))
            if 'FAILED' in str(rpc_reply):
                return rpc_reply
            ###############################################################################
            ## Test Procedure 4 : O-RU NETCONF Server responds with <software-activate>
            ###############################################################################
            Test_Step2 = '\t\tStep 6 : O-RU NETCONF Server responds with <rpc-reply><software-activate><status>. The parameter "status" is set to STARTED.'
            STARTUP.STORE_DATA('{}'.format(Test_Step2),Format='TEST_STEP', PDF=self.pdf)
            STARTUP.STORE_DATA('{}'.format(rpc_reply), Format='XML', PDF=self.pdf)

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
                            Test_Step3), Format='TEST_STEP', PDF=self.pdf)
                        x = xml.dom.minidom.parseString(notify)
                        xml_pretty_str = x.toprettyxml()
                        STARTUP.STORE_DATA(
                            xml_pretty_str, Format='XML', PDF=self.pdf)
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
            self.pdf.add_page()
            STARTUP.STORE_DATA(
                '\n> get --filter-xpath /o-ran-software-management:software-inventory', Format=True, PDF=self.pdf)
            slot_names1 = self.session.get(self.sw_inv).data_xml
            s = xml.dom.minidom.parseString(slot_names1)
            xml_pretty_str = s.toprettyxml()
            self.RU_Details.pop(self.inactive_slot)
            slot_n1 = xmltodict.parse(str(slot_names1))
            SLOTS1 = slot_n1['data']['software-inventory']['software-slot']
            
            for slot in SLOTS1:
                if slot['name'] == 'swRecoverySlot':
                    SLOTS1.remove(slot)

                elif slot['status'] == 'INVALID':
                    STARTUP.STORE_DATA(
                        xml_pretty_str, Format='XML', PDF=self.pdf)
                    return f'SW slot status is Invid for {slot["name"]}...'
                elif slot['name'] == self.inactive_slot:
                    if (slot['active'] == 'true') and slot['running'] == 'false':
                        pass
                    else:
                        STARTUP.STORE_DATA(
                            xml_pretty_str, Format='XML', PDF=self.pdf)
                        return f"SW Inventory didn't update for {self.inactive_slot}..."

                elif slot['name'] != self.inactive_slot:
                    if (slot['active'] != 'false') and slot['running'] != 'true':
                        STARTUP.STORE_DATA(
                            xml_pretty_str, Format='XML', PDF=self.pdf)
                        return f"SW Inventory didn't update for {slot['name'] }..."
            STARTUP.STORE_DATA(xml_pretty_str, Format='XML', PDF=self.pdf)
            STARTUP.append_data_and_print(f'Software {self.flash_image} Activate || Successfully activate on {self.inactive_slot}!!',self.summary)
            return True

        except Exception as e:
            STARTUP.STORE_DATA('{}'.format(e), Format=True,PDF=self.pdf)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=self.pdf)
            return f"{e} Software Activate"

    def reset_rpc(self):
        print(f'{"-"*100}\nConfiguring SW Reset RPC!!')
        ###############################################################################
        ## Test Procedure 1 : Configure_Reset_RPC_in_RU
        ###############################################################################
        Test_Step1 = '\t\tStep 1 : TER NETCONF Client sends <rpc><reset></rpc> to the O-RU NETCONF Server..'
        STARTUP.STORE_DATA('{}'.format(Test_Step1),Format='TEST_STEP', PDF=self.pdf)
        STARTUP.STORE_DATA('\n> user-rpc\n',Format=True, PDF=self.pdf)
        STARTUP.STORE_DATA('******* Replace with below xml ********',Format=True, PDF=self.pdf)
        xml_data3 = '''<reset xmlns="urn:o-ran:operations:1.0"></reset>'''
        STARTUP.STORE_DATA(xml_data3,Format='XML', PDF=self.pdf)
        rpc_reply = self.session.dispatch(to_ele(xml_data3))
        if 'FAILED' in str(rpc_reply):
            return rpc_reply
        ###############################################################################
        ## Test Procedure 2 : Get RPC Reply
        ###############################################################################
        Test_Step2 = '\t\tStep 2 : O-RU NETCONF Server responds with rpc-reply.'
        STARTUP.STORE_DATA('{}'.format(Test_Step2),Format='TEST_STEP', PDF=self.pdf)
        STARTUP.STORE_DATA('{}'.format(rpc_reply),Format='XML', PDF=self.pdf)

        Test_Step3 = '\t\tStep 3 : O-RU restarts with a new software version running matching the version activated.'
        STARTUP.STORE_DATA('{}'.format(Test_Step3),Format='TEST_STEP', PDF=self.pdf)
        STARTUP.append_data_and_print('O-RU going for reboot || Successful!!',self.summary)
        return True

    ###############################################################################
    ## Check Image to flash
    ###############################################################################
    def check_image(self):           
        list_image = os.popen('ls -lrt {}'.format(configur.get('INFO','flash_image_path')))
        images = list_image.readlines()[-1]
        pattern = r'\d\_\d\_[0-9][0-9]?'
        image_name = images.split()[-1]
        # self.image = re.search(pattern,image_name).group()
        return image_name


    ###############################################################################
    ## Befor_Reset
    ###############################################################################
    def Befor_Reset(self):
        print(f'{"-"*100}\nCheck the Link Detection')
        Check1 = self.link_detected()
        Result = STARTUP.check_link_and_ping_dhcp_either_static(Check1,self.pdf,self.INTERFACE_NAME,self.summary)
        if not Result[-1]:
            return Result[0]
        self.hostname = Result[0]

        self.sftp_server_ip = STARTUP.test_server_10_interface_ip('.'.join(self.hostname.split('.')[:-1])+'.')

        ###############################################################################
        ## Read User Name and password from Config.INI of Config.py
        ###############################################################################
        self.USER_N = configur.get('INFO','sudo_user')
        self.PSWRD = configur.get('INFO','sudo_pass')
        self.sftp_user = configur.get('INFO','sftp_user')
        self.sftp_pass = configur.get('INFO','sftp_pass')
        

        try:
            STARTUP.delete_system_log(host= self.hostname)
            time.sleep(2)
            print(f'{"-"*100}\nEstablishing Netopeer Connection')
            ###############################################################################
            ## Perform call home to get ip_details
            ###############################################################################
            self.session, self.login_info = STARTUP.session_login(host = self.hostname,USER_N = self.USER_N,PSWRD = self.PSWRD)

            if self.session:
                STARTUP.append_data_and_print('Netopeer Connection || Successful!!',self.summary)
                self.RU_Details = STARTUP.Software_detail(session = self.session)
                del self.RU_Details['swRecoverySlot']

                ###############################################################################
                ## Test Description
                ###############################################################################
                for key, val in self.RU_Details.items():
                    if (val[0] == 'true' and val[1] == 'true'):
                        Test_Desc = 'Test Description :  This test validates that the O-RU can successfully perform a software update procedure.'
                        CONFIDENTIAL = STARTUP.ADD_CONFIDENTIAL('Slot_Switch',SW_R = val[2]) 
                        STARTUP.STORE_DATA(CONFIDENTIAL,Format='CONF',PDF= self.pdf)
                        STARTUP.STORE_DATA(Test_Desc,Format='DESC',PDF= self.pdf)
                        self.pdf.add_page()
                        self.running_sw = val[2]
                    elif (val[0] == 'true' and val[1] == 'false'):
                        Test_Desc = 'Test Description :  This test validates that the O-RU can successfully perform a software update procedure.'
                        CONFIDENTIAL = STARTUP.ADD_CONFIDENTIAL('Slot_Switch',SW_R = val[2]) 
                        STARTUP.STORE_DATA(CONFIDENTIAL,Format='CONF',PDF= self.pdf)
                        STARTUP.STORE_DATA(Test_Desc,Format='DESC',PDF= self.pdf)
                        self.pdf.add_page()
                        self.inactive_slot = key
                    else:
                        self.running_false = val[2]
                        self.inactive_slot = key

                self.flash_image = self.check_image()
                STARTUP.append_data_and_print('Image Going to flash || {0} to {1}'.format(self.running_false,self.flash_image),self.summary)
                self.sw_file = '/'.join((configur.get('INFO','flash_image_path'),self.flash_image))
                self.rmt = 'sftp://{0}@{1}:22{2}'.format(self.sftp_user,self.sftp_server_ip, self.sw_file)
                
                STARTUP.STORE_DATA('{}'.format(Result[1][0]).center(100),Format=True,PDF=self.pdf)
                STARTUP.STORE_DATA(Result[1][1],Format=False,PDF=self.pdf)
                STARTUP.STORE_DATA('{}'.format("ping -c 5 {}".format(self.hostname)).center(100),Format=True,PDF=self.pdf)
                STARTUP.STORE_DATA(Result[1][2],Format=False,PDF=self.pdf)


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
                Res5 = self.reset_rpc()
                if Res5 != True:
                    return Res5
                return True
            
                
        ###############################################################################
        ## Exception
        ###############################################################################
        except socket.timeout as e:
            Error = '{} : Call Home is not initiated, SSH Socket connection lost....'.format(e)
            STARTUP.STORE_DATA(Error, Format=True,PDF=self.pdf)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=self.pdf)
            return Error
            
        except RPCError as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=self.pdf)
            return [e.type, e.tag, e.severity, e.path, e.message, exc_tb.tb_lineno]

        except Exception as e:
            STARTUP.STORE_DATA('{}'.format(e), Format=True,PDF=self.pdf)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=self.pdf)
            return e 
        
        finally:
            self.logs1 = self.system_logs(self.hostname)
            try:
                self.session.close_session()
            except Exception as e:
                print(e)

    ###############################################################################
    ## Get_Filter_after_Reboot_the_RU
    ###############################################################################
    def get_config_detail(self):
        print(f'{"-"*100}\nCheck the Link Detection')
        Check1 = self.link_detected()
        Result = STARTUP.check_link_and_ping_dhcp_either_static(Check1,self.pdf,self.INTERFACE_NAME,self.summary)
        if not Result[-1]:
            return Result[0]
        self.hostname = Result[0]

        STARTUP.STORE_DATA('{}'.format(Result[1][0]).center(100),Format=True,PDF=self.pdf)
        STARTUP.STORE_DATA(Result[1][1],Format=False,PDF=self.pdf)
        STARTUP.STORE_DATA('{}'.format("ping -c 5 {}".format(self.hostname)).center(100),Format=True,PDF=self.pdf)
        STARTUP.STORE_DATA(Result[1][2],Format=False,PDF=self.pdf)


        ###############################################################################
        ## Perform Call Home to get IP after RU comes up
        ###############################################################################
        t = time.time() +30
        while time.time() < t:
            try:
                self.session2, self.login_info = STARTUP.session_login(host = self.hostname,USER_N = self.USER_N,PSWRD = self.PSWRD)

                if self.session2:
                    ###############################################################################
                    ## Check the get filter of SW
                    ###############################################################################
                    slot_names = self.session2.get(self.sw_inv).data_xml
                    s = xml.dom.minidom.parseString(slot_names)
                    xml_pretty_str = s.toprettyxml()
                    dict_slots = xmltodict.parse(str(slot_names))

                    li = ['INVALID', 'EMPTY']
                    SLOTS_INFO = dict_slots['data']['software-inventory']['software-slot']
                    for i in SLOTS_INFO:
                        if i['status'] in li:
                            STARTUP.STORE_DATA(xml_pretty_str,Format='XML', PDF=self.pdf)
                            return f'{i["name"]} status is not correct....'
                        elif i['name'] == self.inactive_slot and i['active'] != 'true' and i['status'] != 'true':
                            STARTUP.STORE_DATA(xml_pretty_str,Format='XML', PDF=self.pdf)
                            self.summary[f'Running Software After Boot'] = f'{self.running_sw}!!'
                            return f'{i["name"]} is not going to running state....'
                        if i['name'] == self.inactive_slot:
                            self.running_false = i['build-version']
                    STARTUP.STORE_DATA(xml_pretty_str, Format='XML', PDF=self.pdf)
                    STARTUP.append_data_and_print(f'Running Software after boot || {self.running_false}!!',self.summary)
                    STARTUP.append_data_and_print(f'Software {self.flash_image} || Successfuly Update and Running!!',self.summary)
                    return True
                
            ###############################################################################
            ## Exception
            ###############################################################################
            except socket.timeout as e:
                Error = '{} : Call Home is not initiated, SSH Socket connection lost....'.format(e)
                STARTUP.STORE_DATA(Error, Format=True,PDF=self.pdf)
                exc_type, exc_obj, exc_tb = sys.exc_info()
                STARTUP.STORE_DATA(f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=self.pdf)
                return Error

            except RPCError as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                STARTUP.STORE_DATA(f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=self.pdf)
                return [e.type, e.tag, e.severity, e.path, e.message, exc_tb.tb_lineno]

            finally:
                try:
                    self.session2.close_session()
                except Exception as e:
                    print(e)
                pass
        else:
            return 'Cannection not Established...'

    ###############################################################################
    ## After_reset
    ###############################################################################
    def after_reset(self):
        self.waittime = configur.getint('INFO','wait_time')
        time.sleep(self.waittime)
        Res1 = self.get_config_detail()
        time.sleep(5)
        self.logs2 = self.system_logs(self.hostname)
        # print(self.logs2)
        if Res1 != True:
            return Res1
        return Res1
    
    ###############################################################################
    ## Gather system logs
    ###############################################################################
    def system_logs(self,hostname):
        for _ in range(10):
            try:
                host = hostname
                port = 22
                username = self.USER_N
                password = self.PSWRD
                syslog = configur.get('INFO','syslog_path')
                command = "cat {0};".format(syslog)
                ssh = paramiko.SSHClient()
                # ssh.load_system_host_keys()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(host, port, username, password)

                stdin, stdout, stderr = ssh.exec_command(command)
                lines = stdout.readlines()
                # print(lines)
                return lines
            except Exception as e:
                print(e)
                time.sleep(3)
                pass
        else:
            return 'Can\'t connect to the RU.., Logs are not captured.'

    ###############################################################################
    ## Main Function
    ###############################################################################
    def Main_Function(self):
        Check1 = self.Befor_Reset()
        if Check1 == False:
            STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= self.pdf)
            STARTUP.STORE_DATA('SFP link not detected...',Format=False,PDF= self.pdf)
            STARTUP.ACT_RES(f"{'Software Update' : <50}{'||' : ^20}{'FAIL' : ^20}",PDF= self.pdf,COL=(255,0,0))
            STARTUP.append_data_and_print(f'FAIL_REASON || SFP link not detected!!',self.summary)
            STARTUP.append_data_and_print(f"{'Software Update' : <50}{'||' : ^20}{'FAIL' : ^20}",self.summary)
            return False

        elif Check1 == True:
            Check2 = self.after_reset()
            STARTUP.STORE_DATA('\t\t\t\t############ SYSTEM LOGS ##############',Format=True,PDF=self.pdf)
            for i in self.logs1:
                STARTUP.STORE_DATA("{}".format(i),Format=False,PDF=self.pdf)
            for i in self.logs2:
                STARTUP.STORE_DATA("{}".format(i),Format=False,PDF=self.pdf)
            ###############################################################################
            ## Expected/Actual Result
            ###############################################################################
            self.pdf.add_page()
            Exp_Result = '''Expected Result : 1. The O-RU NETCONF Server sends <notification><install-event><status> to the TER NETCONF Client. Field <status> contains the value COMPLETED to indicate the successful installation of software to the desired slot.
            2. The status of the software slot used for software activation remains VALID (it is unchanged) and the parameter "active" remains "True". The parameter "running" is set to True.
            3. Status of the software slot containing the previous version of software used by device remains VALID, the parameter "active" remains False. The parameter "running" is set to False.'''
            STARTUP.STORE_DATA(Exp_Result,Format='DESC',PDF= self.pdf)

            STARTUP.STORE_DATA('\t\t{}'.format('****************** Actual Result ******************'),Format=True,PDF= self.pdf)
            try:
                if Check2 == True:
                    STARTUP.ACT_RES(f"{'Software Update' : <50}{'=' : ^20}{'SUCCESS' : ^20}",PDF= self.pdf,COL=(0,255,0))
                    STARTUP.append_data_and_print(f"{'Software Update' : <50}{'||' : ^20}{'PASS' : ^20}",self.summary)
                    return True

                else:
                    if type(Check2) == list:
                        STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= self.pdf)
                        Error_Info = '''ERROR\n\terror-type \t: \t{}\n\terror-tag \t: \t{}\n\terror-severity \t: \t{}\n\tmessage' \t: \t{}'''.format(*map(str,Check2))
                        STARTUP.STORE_DATA(Error_Info,Format=False,PDF= self.pdf)
                        STARTUP.ACT_RES(f"{'Software Update' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= self.pdf,COL=(255,0,0))
                        STARTUP.append_data_and_print(f'FAIL_REASON || {Error_Info}',self.summary)
                        STARTUP.append_data_and_print(f"{'Software Update' : <50}{'||' : ^20}{'FAIL' : ^20}",self.summary)
                        return False

                    else:
                        STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= self.pdf)
                        STARTUP.STORE_DATA('{}'.format(Check2),Format=False,PDF= self.pdf)
                        STARTUP.ACT_RES(f"{'Software Update' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= self.pdf,COL=(255,0,0))
                        STARTUP.append_data_and_print(f'FAIL_REASON || {Check2}',self.summary)
                        STARTUP.append_data_and_print(f"{'Software Update' : <50}{'||' : ^20}{'FAIL' : ^20}",self.summary)
                        return False

            except Exception as e:
                STARTUP.STORE_DATA('{}'.format(e), Format=True,PDF=self.pdf)
                exc_type, exc_obj, exc_tb = sys.exc_info()
                STARTUP.STORE_DATA(f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=self.pdf)
                STARTUP.append_data_and_print(f'FAIL_REASON || {e}',self.summary)
                STARTUP.append_data_and_print(f"{'Software Update' : <50}{'||' : ^20}{'FAIL' : ^20}",self.summary)
                return False
            ###############################################################################
            ## For Capturing the logs
            ###############################################################################
            finally:
                STARTUP.HEADING(PDF=self.pdf,data='{0} Summary {0}'.format('*'*30))
                STARTUP.render_table_data(self.pdf,STARTUP.append_data(self.summary))
                STARTUP.CREATE_LOGS('Firmware_Upgrade',PDF=self.pdf)

        else:
            STARTUP.STORE_DATA('\t\t\t\t############ SYSTEM LOGS ##############',Format=True,PDF=self.pdf)
            for i in self.logs1:
                STARTUP.STORE_DATA("{}".format(i),Format=False,PDF=self.pdf)
            ###############################################################################
            ## Expected/Actual Result
            ###############################################################################
            self.pdf.add_page()
            Exp_Result = '''Expected Result : 1. The O-RU NETCONF Server sends <notification><install-event><status> to the TER NETCONF Client. Field <status> contains the value COMPLETED to indicate the successful installation of software to the desired slot.
            2. The status of the software slot used for software activation remains VALID (it is unchanged) and the parameter "active" remains "True". The parameter "running" is set to True.
            3. Status of the software slot containing the previous version of software used by device remains VALID, the parameter "active" remains False. The parameter "running" is set to False.'''
            STARTUP.STORE_DATA(Exp_Result, Format='DESC', PDF=self.pdf)

            STARTUP.STORE_DATA('\t\t{}'.format('****************** Actual Result ******************'), Format=True, PDF=self.pdf)
            try:

                if type(Check1) == list:
                    STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= self.pdf)
                    Error_Info = '''ERROR\n\terror-type \t: \t{}\n\terror-tag \t: \t{}\n\terror-severity \t: \t{}\n\tmessage' \t: \t{}'''.format(*map(str,Check1))
                    STARTUP.STORE_DATA(Error_Info,Format=False,PDF= self.pdf)
                    STARTUP.append_data_and_print(f'FAIL_REASON || {Error_Info}',self.summary)
                    STARTUP.append_data_and_print(f"{'Software Update' : <50}{'||' : ^20}{'FAIL' : ^20}",self.summary)
                    return False
                else:
                    STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= self.pdf)
                    STARTUP.STORE_DATA('{}'.format(Check1),Format=False,PDF= self.pdf)
                    STARTUP.ACT_RES(f"{'Software Update' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= self.pdf,COL=(255,0,0))
                    STARTUP.append_data_and_print(f'FAIL_REASON || {Check1}',self.summary)
                    STARTUP.append_data_and_print(f"{'Software Update' : <50}{'||' : ^20}{'FAIL' : ^20}",self.summary)
                    return False


            except Exception as e:
                    STARTUP.STORE_DATA('{}'.format(e), Format=True,PDF=self.pdf)
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    STARTUP.STORE_DATA(f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=self.pdf)
                    STARTUP.append_data_and_print(f'FAIL_REASON || {e}',self.summary)
                    STARTUP.append_data_and_print(f"{'Software Update' : <50}{'||' : ^20}{'FAIL' : ^20}",self.summary)
                    return False

            ###############################################################################
            ## For Capturing the logs
            ###############################################################################
            finally:
                STARTUP.HEADING(PDF=self.pdf,data='{0} Summary {0}'.format('*'*30))
                STARTUP.render_table_data(self.pdf,STARTUP.append_data(self.summary))
                STARTUP.CREATE_LOGS('Firmware_Upgrade',PDF=self.pdf)



### api name of software update testcase
def sw_update():
    start_time = datetime.fromtimestamp(int(time.time()))
    Test_procedure = [f"{'='*100}\nTest case *SW Update* Started!! Status: Running\n{'='*100}",'** Test Coverage **'.center(50),'Static IP Ping',
                'Netopeer Connection','Capability exchange and create-subscription','Configure SW Download',
                'Configure SW Install','Configure SW Activate','Configure reset RPC','Start Time : {}'.format(start_time),'='*100]
    notification('\n'.join(Test_procedure))
    fw_upgrade = Firmware_Upgrade()
    Result = fw_upgrade.Main_Function()
    end_time = datetime.fromtimestamp(int(time.time()))
    st_time = 'Start Time : {}'.format(start_time)
    en_time = 'End Time : {}'.format(end_time)
    execution_time = 'Execution Time is : {}'.format(end_time-start_time)
    print('-'*100)
    print(f'{st_time}\n{en_time}\n{execution_time}')
    fw_upgrade.summary.insert(0,'******* Result *******'.center(50))
    fw_upgrade.summary.insert(0,'='*100)
    notification('\n'.join(fw_upgrade.summary[:-1]))
    notification(f'{st_time}\n{en_time}\n{execution_time}')
    notification(f"{'='*100}\n{fw_upgrade.summary[-1]}\n{'='*100}")
    if Result != True:
        sys.exit(1)
    return Result, fw_upgrade.summary, end_time-start_time

if __name__ == "__main__":
    Result = sw_update()


