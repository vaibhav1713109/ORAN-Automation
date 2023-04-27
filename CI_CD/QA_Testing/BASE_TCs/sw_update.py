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
parent_dir = os.path.dirname(dir_name)
print(parent_dir)
sys.path.append(parent_dir)

########################################################################
## For reading data from .ini file
########################################################################
configur = ConfigParser()
configur.read('{}/MPLANE/require/inputs.ini'.format(parent_dir))

###############################################################################
## Related Imports
###############################################################################
from MPLANE.require.Notification import *
from MPLANE.require.Configuration import *

###############################################################################
## Initiate PDF
###############################################################################

class Firmware_Upgrade(PDF,Configuration,netopeer_connection,genrate_pdf_report):
   
    # init method or constructor 
    def __init__(self):
        PDF.__init__(self)
        netopeer_connection.__init__(self)
        Configuration.__init__(self)
        genrate_pdf_report.__init__(self)
        PDF.PDF_CAP(self)
        self.summary = []
        self.rmt = ''
        self.sftp_pass = ''
        self.logs1,self.logs2 = '',''
        self.sw_inv = '''<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            <software-inventory xmlns="urn:o-ran:software-management:1.0">
            </software-inventory>
            </filter>'''
        self.get_filter_cmd = "> get --filter-xpath /o-ran-software-management:software-inventory"

    ###############################################################################
    ## Test Procedure
    ###############################################################################
    def netopeer_connection_and_capability(self,cmd,ethtool_out,ping_output):
        try:
            time.sleep(10)
            netopeer_connection.delete_system_log(self,host= self.hostname)
            ###############################################################################
            ## Establishing netopeer connetion
            ###############################################################################
            self.session_login(timeout=60,username = self.username,password=self.password)
            if self.session:
                Configuration.append_data_and_print(self,'Netopeer Connection || Successful')
                Test_Desc = 'Test Description :  This test validates that the O-RU can successfully perform a software update procedure.'
                Result = netopeer_connection.add_test_description(self,Test_Description=Test_Desc, Test_Case_name='M_CTC_ID_019')
                if len(Result) > 2:
                    self.running_sw, self.running_false_sw, self.inactive_slot = Result[0], Result[1], Result[2]

                Configuration.append_data_and_print(self,'Image Going to flash || {0} to {1}'.format(self.running_false_sw,self.flash_image))

                PDF.STORE_DATA(self,'{}'.format(cmd).center(100),Format=True,)
                PDF.STORE_DATA(self,ethtool_out,Format=False)
                PDF.STORE_DATA(self,'{}'.format("ping -c 5 {}".format(self.hostname)).center(100),Format=True,)
                PDF.STORE_DATA(self,ping_output,Format=False)

                netopeer_connection.add_netopeer_connection_details(self)
                netopeer_connection.hello_capability(self)
                
                ###############################################################################
                ## Create_subscription
                ###############################################################################
                filter = """<filter type="xpath" xmlns="urn:ietf:params:xml:ns:netconf:notification:1.0" xmlns:notf_c="urn:ietf:params:xml:ns:yang:ietf-netconf-notifications" select="/notf_c:*"/>"""
                cmd = '> subscribe --filter-xpath /ietf-netconf-notifications:*'
                netopeer_connection.create_subscription(self,filter=filter,cmd=cmd)
                return True

        except RPCError as e:
            rpc_error_element = etree.ElementTree(e.xml)
            rpc_error = etree.tostring(rpc_error_element).decode()
            rpc_error = xml.dom.minidom.parseString(rpc_error).toprettyxml()
            print(rpc_error)
            Configuration.append_data_and_print(self,'Create Subscription Filter || Fail')
            return f"Netopeer_connection_and_capability Error : {e}"
        
        except Exception as e:
            PDF.STORE_DATA(self,'Fetch_mac_of_ru_and_pre_get_filter_user_mgmt Error : {}'.format(e), Format=True)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            PDF.STORE_DATA(self,f"Error occured in line number {exc_tb.tb_lineno}", Format=False)
            return f"Netopeer_connection_and_capability Error : {e}"
        
    def software_download(self):
        try:
            Configuration.append_data_and_print(self,"Try to Configuring SW Download RPC || In progress")
            ###############################################################################
            ## Fetch Public Key of Linux PC
            ###############################################################################
            pub_k = subprocess.getoutput('cat /etc/ssh/ssh_host_rsa_key.pub')
            pk = pub_k.split()
            pub_key = pk[1]

            ###############################################################################
            ## Initial Get Filter
            ###############################################################################
            PDF.add_page(self)
            PDF.STORE_DATA(self,'\t\tInitial Get Filter',Format='TEST_STEP')
            xml_pretty_sw_inventory, slot_dict_data = netopeer_connection.get(self,filter=self.sw_inv,cmd=self.get_filter_cmd)

            ###############################################################################
            ## Checking The status, active and running value
            ###############################################################################
            slots_info = slot_dict_data['data']['software-inventory']['software-slot']
            for i in slots_info:
                if i['status'] == 'INVALID':
                    PDF.STORE_DATA(self,xml_pretty_sw_inventory, Format='XML')
                    return 'SW slot status is Invalid...'
                if (i['active'] == 'false' and i['running'] == 'false') or (i['active'] == 'true' and i['running'] == 'true'):
                    pass
                else:
                    return 'Slots Active and Running Status are diffrent...'
            PDF.STORE_DATA(self,xml_pretty_sw_inventory, Format='XML')
            
            ###############################################################################
            ## Configure SW Download RPC in RU
            ###############################################################################
            xml_data = open("{}/MPLANE/require/Yang_xml/sw_download.xml".format(parent_dir)).read()
            xml_data = xml_data.format(rmt_path=self.rmt, password=self.sftp_pass, public_key=pub_key)

            ###############################################################################
            ## Test Procedure 1
            ###############################################################################
            Test_Step1 = '\t\tStep 1 : TER NETCONF Client triggers <rpc><software-download>'
            PDF.STORE_DATA(self,'{}'.format(Test_Step1), Format='TEST_STEP')
            sw_download_rpc_reply = netopeer_connection.send_rpc(self,rpc_data=xml_data)
            if sw_download_rpc_reply != True:
                return sw_download_rpc_reply

            PDF.STORE_DATA(self,'******* RPC Reply ********',Format=True)
            PDF.STORE_DATA(self,'{}'.format(sw_download_rpc_reply), Format='XML')

            ###############################################################################
            ## Test Procedure 2 : Capture_The_Notifications
            ###############################################################################
            PDF.add_page(self)
            Test_Step2 = '\t\tStep 2 :  O-RU NETCONF Server sends <notification><download-event> with status COMPLETED to TER NETCONF Client'
            PDF.STORE_DATA(self,'{}'.format(Test_Step2),Format='TEST_STEP')

            xml_pretty_str = ''
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
                        PDF.STORE_DATA(self,xml_pretty_str, Format='XML')
                        status = dict_n['notification']['download-event']['status']
                        if status != 'COMPLETED':
                            return status
                        break
                except:
                    pass
            if not xml_pretty_str:
                Configuration.append_data_and_print(self,f'Notification not captured || Fail !!')
                pass
            Configuration.append_data_and_print(self,f'Software File Download || {self.flash_image} Successful!!')
            return True

        except RPCError as e:
            rpc_error_element = etree.ElementTree(e.xml)
            rpc_error = etree.tostring(rpc_error_element).decode()
            rpc_error = xml.dom.minidom.parseString(rpc_error).toprettyxml()
            print(rpc_error)
            Configuration.append_data_and_print(self,'Software Download || Fail')
            return f"Software Download Error : {e}"
        
        except Exception as e:
            PDF.STORE_DATA(self,'{}'.format(e), Format=True)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            PDF.STORE_DATA(self,
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False)
            return f"Software Download Error : {e}"

    def software_install(self):
        try:
            Configuration.append_data_and_print(self,"Try to Configuring SW Install RPC || In progress")
            ###############################################################################
            ## Test Procedure 2 : Configure_SW_Install_RPC
            ###############################################################################
            Test_Step3 = '\t\tStep 3 : TER NETCONF Client triggers <rpc><software-install> Slot must have attributes active = FALSE, running = FALSE.'
            PDF.STORE_DATA(self,'{}'.format(Test_Step3), Format='TEST_STEP')
            ###############################################################################
            ## Install_at_the_slot_Which_Have_False_Status
            ###############################################################################
            xml_data2 = open("{}/MPLANE/require/Yang_xml/sw_install.xml".format(parent_dir)).read()
            file_path = self.rmt
            li = file_path.split(':22/')
            xml_data2 = xml_data2.format(slot_name=self.inactive_slot,File_name = '/{}'.format(li[1]))
            sw_install_rpc_reply = netopeer_connection.send_rpc(self,rpc_data=xml_data2)
            if sw_install_rpc_reply != True:
                return sw_install_rpc_reply
            PDF.STORE_DATA(self,'******* RPC Reply ********', Format=True)
            PDF.STORE_DATA(self,'{}'.format(sw_install_rpc_reply), Format='XML')


            ###############################################################################
            ## Test Procedure 4 and 5 : Capture_The_Notifications
            ###############################################################################
            Test_Step4 = '\t\tStep 4 and 5 :  O-RU NETCONF Server sends <notification><install-event> with status COMPLETED to TER NETCONF Client'
            PDF.STORE_DATA(self,'{}'.format(Test_Step4), Format='TEST_STEP')
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
                        PDF.STORE_DATA(self,xml_pretty_str, Format='XML')
                        status = dict_n['notification']['install-event']['status']
                        if status != 'COMPLETED':
                            return status
                        break
                except:
                    pass


            ###############################################################################
            ## POST_GET_FILTER
            ###############################################################################            
            PDF.add_page(self)
            PDF.STORE_DATA(self,'\t\t POST GET AFTER INSTALL SW', Format='TEST_STEP')
            xml_pretty_sw_inventory, slot_dict_data = netopeer_connection.get(self,filter=self.sw_inv,cmd=self.get_filter_cmd)

            ###############################################################################
            ## Checking The status, active and running value
            ###############################################################################
            SLOTS = slot_dict_data['data']['software-inventory']['software-slot']
            SLOT_INFO = {}
            for SLOT in SLOTS:
                if SLOT['status'] == 'INVALID':
                    PDF.STORE_DATA(self,xml_pretty_sw_inventory, Format='XML', )
                    return f'SW slot status is Invalid for {SLOT["name"]}...'

                elif (SLOT['name'] != 'swRecoverySlot'):
                    SLOT_INFO[SLOT['name']] = [SLOT['active'], SLOT['running']]

                elif (SLOT['active'] == 'true' and SLOT['running'] == 'true') or (SLOT['active'] == 'false' and SLOT['running'] == 'false'):
                    if (SLOT['active'] == 'false' and SLOT['running'] == 'false') and (SLOT['name'] != 'swRecoverySlot'):
                        self.inactive_slot = SLOT['name']
                        del SLOT_INFO[SLOT['name']]
                    pass
                else:
                    PDF.STORE_DATA(self,xml_pretty_sw_inventory, Format='XML', )
                    return f'Slots Active and Running Status are diffrent for {SLOT["name"]}...'
            PDF.STORE_DATA(self,xml_pretty_sw_inventory, Format='XML', )
            Configuration.append_data_and_print(self,f'Software {self.flash_image} Install || Successfully install on {self.inactive_slot}!!')
            return True
        
        except RPCError as e:
            rpc_error_element = etree.ElementTree(e.xml)
            rpc_error = etree.tostring(rpc_error_element).decode()
            rpc_error = xml.dom.minidom.parseString(rpc_error).toprettyxml()
            print(rpc_error)
            Configuration.append_data_and_print(self,'Software Install || Fail')
            return f"Software Install Error : {e}"
        
        except Exception as e:
            PDF.STORE_DATA(self,'{}'.format(e), Format=True)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            PDF.STORE_DATA(self,f"Error occured in line number {exc_tb.tb_lineno}", Format=False)
            return f"Software Install Error : {e}"
        
    def software_activate(self):
        try:
            Configuration.append_data_and_print(self,f'Running Software || {self.running_sw}!!')
            Configuration.append_data_and_print(self,"Try to Configuring SW Activate RPC || In progress")
            ###############################################################################
            ## Test Procedure 3 : Configure SW Activate RPC in RU
            ###############################################################################
            Test_Step1 = '\t\tStep 5 : TER NETCONF Client triggers <rpc><software-activate> Slot must have attributes active = FALSE, running = FALSE.'
            PDF.STORE_DATA(self,'{}'.format(Test_Step1), Format='TEST_STEP', )
            xml_data2 = open("{}/MPLANE/require/Yang_xml/sw_activate.xml".format(parent_dir)).read()
            xml_data2 = xml_data2.format(slot_name=self.inactive_slot)
            sw_activate_rpc_reply = netopeer_connection.send_rpc(self,rpc_data=xml_data2)
            if sw_activate_rpc_reply != True:
                return sw_activate_rpc_reply
            ###############################################################################
            ## Test Procedure 4 : O-RU NETCONF Server responds with <software-activate>
            ###############################################################################
            Test_Step2 = '\t\tStep 6 : O-RU NETCONF Server responds with <rpc-reply><software-activate><status>. The parameter "status" is set to STARTED.'
            PDF.STORE_DATA(self,'{}'.format(Test_Step2),Format='TEST_STEP', )
            PDF.STORE_DATA(self,'{}'.format(sw_activate_rpc_reply), Format='XML', )

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
                        PDF.STORE_DATA(self,'{}'.format(
                            Test_Step3), Format='TEST_STEP', )
                        x = xml.dom.minidom.parseString(notify)
                        xml_pretty_str = x.toprettyxml()
                        PDF.STORE_DATA(self,
                            xml_pretty_str, Format='XML', )
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
            PDF.add_page(self)
            xml_pretty_sw_inventory, slot_dict_data = netopeer_connection.get(self,filter=self.sw_inv,cmd=self.get_filter_cmd)
            self.RU_Details.pop(self.inactive_slot)
            SLOTS1 = slot_dict_data['data']['software-inventory']['software-slot']
            
            for slot in SLOTS1:
                if slot['name'] == 'swRecoverySlot':
                    SLOTS1.remove(slot)

                elif slot['status'] == 'INVALID':
                    PDF.STORE_DATA(self,xml_pretty_sw_inventory, Format='XML', )
                    return f'SW slot status is Invid for {slot["name"]}...'
                elif slot['name'] == self.inactive_slot:
                    if (slot['active'] == 'true') and slot['running'] == 'false':
                        pass
                    else:
                        PDF.STORE_DATA(self,xml_pretty_sw_inventory, Format='XML', )
                        return f"SW Inventory didn't update for {self.inactive_slot}..."

                elif slot['name'] != self.inactive_slot:
                    if (slot['active'] != 'false') and slot['running'] != 'true':
                        PDF.STORE_DATA(self,xml_pretty_sw_inventory, Format='XML', )
                        return f"SW Inventory didn't update for {slot['name'] }..."
            PDF.STORE_DATA(self,xml_pretty_sw_inventory, Format='XML', )
            Configuration.append_data_and_print(self,f'Software {self.flash_image} Activate || Successfully activate on {self.inactive_slot}!!')
            return True

        except RPCError as e:
            rpc_error_element = etree.ElementTree(e.xml)
            rpc_error = etree.tostring(rpc_error_element).decode()
            rpc_error = xml.dom.minidom.parseString(rpc_error).toprettyxml()
            print(rpc_error)
            Configuration.append_data_and_print(self,'Software Activate || Fail')
            return f"Software Activate Error : {e}"
        
        except Exception as e:
            PDF.STORE_DATA(self,'{}'.format(e), Format=True)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            PDF.STORE_DATA(self,f"Error occured in line number {exc_tb.tb_lineno}", Format=False)
            return f"Software Activate Error : {e}"

    def reset_rpc(self):
        Configuration.append_data_and_print(self,"Try to Configuring SW Reset RPC || In progress")
        ###############################################################################
        ## Test Procedure 1 : Configure_Reset_RPC_in_RU
        ###############################################################################
        Test_Step1 = '\t\tStep 1 : TER NETCONF Client sends <rpc><reset></rpc> to the O-RU NETCONF Server..'
        PDF.STORE_DATA(self,'{}'.format(Test_Step1),Format='TEST_STEP', )
        xml_data3 = '''<reset xmlns="urn:o-ran:operations:1.0"></reset>'''
        sw_reset_rpc_reply = netopeer_connection.send_rpc(self,rpc_data=xml_data3)
        if sw_reset_rpc_reply != True:
            return sw_reset_rpc_reply
        ###############################################################################
        ## Test Procedure 2 : Get RPC Reply
        ###############################################################################
        Test_Step2 = '\t\tStep 2 : O-RU NETCONF Server responds with rpc-reply.'
        PDF.STORE_DATA(self,'{}'.format(Test_Step2),Format='TEST_STEP', )
        PDF.STORE_DATA(self,'{}'.format(sw_reset_rpc_reply),Format='XML', )

        Test_Step3 = '\t\tStep 3 : O-RU restarts with a new software version running matching the version activated.'
        PDF.STORE_DATA(self,'{}'.format(Test_Step3),Format='TEST_STEP', )
        Configuration.append_data_and_print(self,'O-RU going for reboot || Successful!!')
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
        Output = Configuration.Link_detction_and_check_ping(self)
        if Output[-1]!=True:
            return Output[0]
        self.hostname = Output[-2]
        test_server_ip_format='.'.join(self.hostname.split('.')[:-1])+'.'
        self.sftp_server_ip = Configuration.test_server_10_interface_ip(self,ip_format=test_server_ip_format)

        ###############################################################################
        ## Read User Name and password from Config.INI of Config.py
        ###############################################################################
        self.sftp_user = configur.get('INFO','sftp_user')
        self.sftp_pass = configur.get('INFO','sftp_pass')
        

        try:
            self.flash_image = self.check_image()
            self.sw_file = '/'.join((configur.get('INFO','flash_image_path'),self.flash_image))
            self.rmt = 'sftp://{0}@{1}:22{2}'.format(self.sftp_user,self.sftp_server_ip, self.sw_file)

            Res1 = self.netopeer_connection_and_capability(Output[2],Output[0],Output[1])
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
        except Exception as e:
            PDF.STORE_DATA(self,'Main_Function Error : {}'.format(e), Format=True)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            PDF.STORE_DATA(self,f"Error occured in line number {exc_tb.tb_lineno}", Format=False)
            return f'Befor_Reset Error : {e}'
        
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
        Result = Configuration.Link_detction_and_check_ping(self)
        if Result[-1]!=True:
            return Result[0]
        self.hostname = Result[-2]

        PDF.STORE_DATA(self,'{}'.format(Result[1][0]).center(100),Format=True)
        PDF.STORE_DATA(self,Result[1][1],Format=False)
        PDF.STORE_DATA(self,'{}'.format("ping -c 5 {}".format(self.hostname)).center(100),Format=True)
        PDF.STORE_DATA(self,Result[1][2],Format=False)


        ###############################################################################
        ## Perform Call Home to get IP after RU comes up
        ###############################################################################
        Error = ''
        t = time.time() +30
        while time.time() < t:
            try:
                self.session_login(timeout=60,username = self.username,password=self.password)

                if self.session:
                    ###############################################################################
                    ## Check the get filter of SW
                    ###############################################################################
                    slot_names = self.session.get(self.sw_inv).data_xml
                    s = xml.dom.minidom.parseString(slot_names)
                    xml_pretty_str = s.toprettyxml()
                    dict_slots = xmltodict.parse(str(slot_names))

                    li = ['INVALID', 'EMPTY']
                    SLOTS_INFO = dict_slots['data']['software-inventory']['software-slot']
                    for i in SLOTS_INFO:
                        if i['status'] in li:
                            PDF.STORE_DATA(self,xml_pretty_str,Format='XML', )
                            return f'{i["name"]} status is not correct....'
                        elif i['name'] == self.inactive_slot and i['active'] != 'true' and i['status'] != 'true':
                            PDF.STORE_DATA(self,xml_pretty_str,Format='XML', )
                            self.summary[f'Running Software After Boot'] = f'{self.running_sw}!!'
                            return f'{i["name"]} is not going to running state....'
                        if i['name'] == self.inactive_slot:
                            self.running_false_sw = i['build-version']
                    PDF.STORE_DATA(self,xml_pretty_str, Format='XML', )
                    Configuration.append_data_and_print(self,f'Running Software after boot || {self.running_false_sw}!!')
                    Configuration.append_data_and_print(self,f'Software {self.flash_image} || Successfuly Update and Running!!')
                    return True
                
            ###############################################################################
            ## Exception
            ###############################################################################
            except socket.timeout as e:
                Error = '{} : Call Home is not initiated, SSH Socket connection lost....'.format(e)
                PDF.STORE_DATA(self,Error, Format=True)
                exc_type, exc_obj, exc_tb = sys.exc_info()
                PDF.STORE_DATA(self,f"Error occured in line number {exc_tb.tb_lineno}", Format=False)

            except RPCError as e:
                rpc_error_element = etree.ElementTree(e.xml)
                rpc_error = etree.tostring(rpc_error_element).decode()
                rpc_error = xml.dom.minidom.parseString(rpc_error).toprettyxml()
                Error = rpc_error

            finally:
                try:
                    self.session.close_session()
                except Exception as e:
                    print(f'Get_config_detail Error : {e}')
                pass
        else:
            return f'Get_config_detail Error : {Error}, Cannection not Established.'

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
                username = self.username
                password = self.password
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
            return 'System_logs Error : Can\'t connect to the RU.., Logs are not captured.'

    ###############################################################################
    ## Main Function
    ###############################################################################
    def Main_Function(self):
        Check1 = self.Befor_Reset()
        if Check1 == False:
            PDF.STORE_DATA(self,'{0} FAIL_REASON {0}'.format('*'*20),Format=True)
            PDF.STORE_DATA(self,'SFP link not detected...',Format=False)
            PDF.ACT_RES(self,f"{'Software Update' : <50}{'||' : ^20}{'FAIL' : ^20}",COL=(255,0,0))
            Configuration.append_data_and_print(self,f'FAIL_REASON || SFP link not detected!!')
            Configuration.append_data_and_print(self,f"{'Software Update' : <50}{'||' : ^20}{'FAIL' : ^20}")
            return False

        elif Check1 == True:
            Check2 = self.after_reset()
            PDF.STORE_DATA(self,'\t\t\t\t############ SYSTEM LOGS ##############',Format=True)
            for i in self.logs1:
                PDF.STORE_DATA(self,"{}".format(i),Format=False)
            for i in self.logs2:
                PDF.STORE_DATA(self,"{}".format(i),Format=False)
            ###############################################################################
            ## Expected/Actual Result
            ###############################################################################
            PDF.add_page(self)
            Exp_Result = '''Expected Result : 1. The O-RU NETCONF Server sends <notification><install-event><status> to the TER NETCONF Client. Field <status> contains the value COMPLETED to indicate the successful installation of software to the desired slot.
            2. The status of the software slot used for software activation remains VALID (it is unchanged) and the parameter "active" remains "True". The parameter "running" is set to True.
            3. Status of the software slot containing the previous version of software used by device remains VALID, the parameter "active" remains False. The parameter "running" is set to False.'''
            PDF.STORE_DATA(self,Exp_Result,Format='DESC')

            PDF.STORE_DATA(self,'\t\t{}'.format('****************** Actual Result ******************'),Format=True)
            try:
                if Check2 == True:
                    PDF.ACT_RES(self,f"{'Software Update' : <50}{'=' : ^20}{'SUCCESS' : ^20}",COL=(0,255,0))
                    Configuration.append_data_and_print(self,f"{'Software Update' : <50}{'||' : ^20}{'PASS' : ^20}")
                    return True

                else:
                    if type(Check2) == list:
                        PDF.STORE_DATA(self,'{0} FAIL_REASON {0}'.format('*'*20),Format=True)
                        Error_Info = '''ERROR\n\terror-type \t: \t{}\n\terror-tag \t: \t{}\n\terror-severity \t: \t{}\n\tmessage' \t: \t{}'''.format(*map(str,Check2))
                        PDF.STORE_DATA(self,Error_Info,Format=False)
                        PDF.ACT_RES(self,f"{'Software Update' : <50}{'=' : ^20}{'FAIL' : ^20}",COL=(255,0,0))
                        Configuration.append_data_and_print(self,f'FAIL_REASON || {Error_Info}')
                        Configuration.append_data_and_print(self,f"{'Software Update' : <50}{'||' : ^20}{'FAIL' : ^20}")
                        return False

                    else:
                        PDF.STORE_DATA(self,'{0} FAIL_REASON {0}'.format('*'*20),Format=True)
                        PDF.STORE_DATA(self,'{}'.format(Check2),Format=False)
                        PDF.ACT_RES(self,f"{'Software Update' : <50}{'=' : ^20}{'FAIL' : ^20}",COL=(255,0,0))
                        Configuration.append_data_and_print(self,f'FAIL_REASON || {Check2}')
                        Configuration.append_data_and_print(self,f"{'Software Update' : <50}{'||' : ^20}{'FAIL' : ^20}")
                        return False

            except Exception as e:
                PDF.STORE_DATA(self,'{}'.format(e), Format=True)
                exc_type, exc_obj, exc_tb = sys.exc_info()
                PDF.STORE_DATA(self,f"Error occured in line number {exc_tb.tb_lineno}", Format=False)
                Configuration.append_data_and_print(self,f'FAIL_REASON || {e}')
                Configuration.append_data_and_print(self,f"{'Software Update' : <50}{'||' : ^20}{'FAIL' : ^20}")
                return False
            ###############################################################################
            ## For Capturing the logs
            ###############################################################################
            finally:
                PDF.HEADING(self,data='{0} Summary {0}'.format('*'*30))
                PDF.render_table_data(self,Configuration.nested_summary_list(self,self.summary))
                genrate_pdf_report.CREATE_LOGS(self,'Firmware_Upgrade')

        else:
            PDF.STORE_DATA(self,'\t\t\t\t############ SYSTEM LOGS ##############',Format=True)
            for i in self.logs1:
                PDF.STORE_DATA(self,"{}".format(i),Format=False)
            ###############################################################################
            ## Expected/Actual Result
            ###############################################################################
            PDF.add_page(self)
            Exp_Result = '''Expected Result : 1. The O-RU NETCONF Server sends <notification><install-event><status> to the TER NETCONF Client. Field <status> contains the value COMPLETED to indicate the successful installation of software to the desired slot.
            2. The status of the software slot used for software activation remains VALID (it is unchanged) and the parameter "active" remains "True". The parameter "running" is set to True.
            3. Status of the software slot containing the previous version of software used by device remains VALID, the parameter "active" remains False. The parameter "running" is set to False.'''
            PDF.STORE_DATA(self,Exp_Result, Format='DESC', )

            PDF.STORE_DATA(self,'\t\t{}'.format('****************** Actual Result ******************'), Format=True, )
            try:

                if type(Check1) == list:
                    PDF.STORE_DATA(self,'{0} FAIL_REASON {0}'.format('*'*20),Format=True)
                    Error_Info = '''ERROR\n\terror-type \t: \t{}\n\terror-tag \t: \t{}\n\terror-severity \t: \t{}\n\tmessage' \t: \t{}'''.format(*map(str,Check1))
                    PDF.STORE_DATA(self,Error_Info,Format=False)
                    Configuration.append_data_and_print(self,f'FAIL_REASON || {Error_Info}')
                    Configuration.append_data_and_print(self,f"{'Software Update' : <50}{'||' : ^20}{'FAIL' : ^20}")
                    return False
                else:
                    PDF.STORE_DATA(self,'{0} FAIL_REASON {0}'.format('*'*20),Format=True)
                    PDF.STORE_DATA(self,'{}'.format(Check1),Format=False)
                    PDF.ACT_RES(self,f"{'Software Update' : <50}{'=' : ^20}{'FAIL' : ^20}",COL=(255,0,0))
                    Configuration.append_data_and_print(self,f'FAIL_REASON || {Check1}')
                    Configuration.append_data_and_print(self,f"{'Software Update' : <50}{'||' : ^20}{'FAIL' : ^20}")
                    return False


            except Exception as e:
                    PDF.STORE_DATA(self,'{}'.format(e), Format=True)
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    PDF.STORE_DATA(self,f"Error occured in line number {exc_tb.tb_lineno}", Format=False)
                    Configuration.append_data_and_print(self,f'FAIL_REASON || {e}')
                    Configuration.append_data_and_print(self,f"{'Software Update' : <50}{'||' : ^20}{'FAIL' : ^20}")
                    return False

            ###############################################################################
            ## For Capturing the logs
            ###############################################################################
            finally:
                PDF.HEADING(self,data='{0} Summary {0}'.format('*'*30))
                PDF.render_table_data(self,Configuration.nested_summary_list(self,self.summary))
                genrate_pdf_report.CREATE_LOGS(self,'Firmware_Upgrade')


    def api_call(self):
        start_time = datetime.fromtimestamp(int(time.time()))
        Test_procedure = [f"{'='*100}\nTest case *SW Update* Started!! Status: Running\n{'='*100}",'** Test Coverage **'.center(50),'Static IP Ping',
                'Netopeer Connection','Capability exchange and create-subscription','Configure SW Download',
                'Configure SW Install','Configure SW Activate','Configure reset RPC','Start Time : {}'.format(start_time),'='*100]
        notification('\n'.join(Test_procedure))
        Result = self.Main_Function()
        end_time = datetime.fromtimestamp(int(time.time()))
        st_time = 'Start Time : {}'.format(start_time)
        en_time = 'End Time : {}'.format(end_time)
        execution_time = 'Execution Time is : {}'.format(end_time-start_time)
        print('-'*100)
        print(f'{st_time}\n{en_time}\n{execution_time}')
        self.summary.insert(0,'******* Result *******'.center(50))
        self.summary.insert(0,'='*100)
        notification('\n'.join(self.summary[:-1]))
        notification(f'{st_time}\n{en_time}\n{execution_time}')
        notification(f"{'='*100}\n{self.summary[-1]}\n{'='*100}")
        if Result !=True:
            sys.exit(1)
        

if __name__ == "__main__":
    obj = Firmware_Upgrade()
    Result = obj.api_call()
