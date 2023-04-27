###############################################################################
##@ FILE NAME:      Software Slot Switch
##@ TEST SCOPE:     M PLANE O-RAN CONFORMANCE
##@ Version:        V_1.0.0
##@ Support:        @Ramiyer, @VaibhavDhiman, @PriyaSharma
###############################################################################

###############################################################################
## Package Imports 
###############################################################################

import socket, sys, os, time, xmltodict, xml.dom.minidom, paramiko, subprocess
from datetime import time
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

class Slot_Switch(Link_Detect):
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
            self.summary.append(['Capability exchange','Successful'])
            print('-'*100)
            print(f' '.join(self.summary[-1]))
            
            ###############################################################################
            ## Create_subscription
            ###############################################################################
            filter = """<filter type="xpath" xmlns="urn:ietf:params:xml:ns:netconf:notification:1.0" xmlns:swm="urn:o-ran:software-management:1.0" select="/swm:*"/>"""
            cap=self.session.create_subscription(filter=filter)
            STARTUP.STORE_DATA('> subscribe --filter-xpath /o-ran-software-management:*', Format=True, PDF=self.pdf)
            dict_data = xmltodict.parse(str(cap))
            if dict_data['nc:rpc-reply']['nc:ok'] == None:
                STARTUP.STORE_DATA('\nOk\n', Format=False, PDF=self.pdf)
            self.summary.append(['Create-subscription','Successful'])
            print('-'*100)
            print(f' '.join(self.summary[-1]))
            return True

        except Exception as e:
            STARTUP.STORE_DATA('{}'.format(e), Format=True,PDF=self.pdf)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=self.pdf)
            return f"{e} Subscribe and Capability Exchange"
        
    def software_activate(self):
        try:
            self.summary.append([f'Running Software',f'{self.running_sw}'])
            print('-'*100)
            print(f' '.join(self.summary[-1]))
            print(f'{"-"*100}\nConfiguring SW Activate RPC')
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
            ## Test Procedure 1 : Configure SW Activate RPC in RU
            ###############################################################################
            Test_Step1 = '\t\tStep 1 : TER NETCONF Client triggers <rpc><software-activate> Slot must have attributes active = FALSE, running = FALSE.'
            STARTUP.STORE_DATA('{}'.format(Test_Step1), Format='TEST_STEP', PDF=self.pdf)
            xml_data2 = open("{}/require/Yang_xml/sw_activate.xml".format(parent)).read()
            xml_data2 = xml_data2.format(slot_name=self.inactive_slot)

            STARTUP.STORE_DATA('\n> user-rpc\n', Format=True, PDF=self.pdf)
            STARTUP.STORE_DATA('******* Replace with below xml ********', Format=True, PDF=self.pdf)
            STARTUP.STORE_DATA(xml_data2, Format='XML', PDF=self.pdf)
            d3 = self.session.dispatch(to_ele(xml_data2))

            ###############################################################################
            ## Test Procedure 2 : O-RU NETCONF Server responds with <software-activate>
            ###############################################################################
            Test_Step2 = '\t\tStep 2 : O-RU NETCONF Server responds with <rpc-reply><software-activate><status>. The parameter "status" is set to STARTED.'
            STARTUP.STORE_DATA('{}'.format(Test_Step2),Format='TEST_STEP', PDF=self.pdf)
            STARTUP.STORE_DATA('{}'.format(d3), Format='XML', PDF=self.pdf)

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
            self.summary.append([f'Software {self.running_sw} Activate', f'Successfully activate on {self.inactive_slot}'])
            print('-'*100)
            print(f' '.join(self.summary[-1]))
            return True

        except Exception as e:
            STARTUP.STORE_DATA('{}'.format(e), Format=True,PDF=self.pdf)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=self.pdf)
            return f"{e} Software Activate"

    def reset_rpc(self):
        ###############################################################################
        ## Test Procedure 1 : Configure_Reset_RPC_in_RU
        ###############################################################################
        print(f'{"-"*100}\nConfiguring SW Reset RPC')
        Test_Step1 = '\t\tStep 1 : TER NETCONF Client sends <rpc><reset></rpc> to the O-RU NETCONF Server..'
        STARTUP.STORE_DATA('{}'.format(Test_Step1),Format='TEST_STEP', PDF=self.pdf)
        STARTUP.STORE_DATA('\n> user-rpc\n',Format=True, PDF=self.pdf)
        STARTUP.STORE_DATA('******* Replace with below xml ********',Format=True, PDF=self.pdf)
        xml_data3 = '''<reset xmlns="urn:o-ran:operations:1.0"></reset>'''
        STARTUP.STORE_DATA(xml_data3,Format='XML', PDF=self.pdf)
        d3 = self.session.dispatch(to_ele(xml_data3))

        ###############################################################################
        ## Test Procedure 2 : Get RPC Reply
        ###############################################################################
        Test_Step2 = '\t\tStep 2 : O-RU NETCONF Server responds with rpc-reply.'
        STARTUP.STORE_DATA('{}'.format(Test_Step2),Format='TEST_STEP', PDF=self.pdf)
        STARTUP.STORE_DATA('{}'.format(d3),Format='XML', PDF=self.pdf)

        Test_Step3 = '\t\tStep 3 : O-RU restarts with a new software version running matching the version activated.'
        STARTUP.STORE_DATA('{}'.format(Test_Step3),Format='TEST_STEP', PDF=self.pdf)
        self.summary.append(['O-RU going for reboot:','Successful'])
        print('-'*100)
        print(f' '.join(self.summary[-1]))
        return True
    
    ###############################################################################
    ## Befor_Reset
    ###############################################################################
    def Befor_Reset(self):
        print(f'{"-"*100}\nCheck the Link Detection')
        Check1 = self.link_detected()
        if Check1 == False or Check1 == None:
            self.summary.append(['SFP Link Detection','Fail'])
            return Check1
            
        cmd = "ethtool " + self.INTERFACE_NAME
        ethtool_out = subprocess.getoutput(cmd)
        self.summary.append(['SFP Link Detection','Successful'])
        ###############################################################################
        ## Read User Name and password from Config.INI of Config.py
        ###############################################################################
        self.USER_N = configur.get('INFO','sudo_user')
        self.PSWRD = configur.get('INFO','sudo_pass')

        ###############################################################################
        ## Sniff the live packet and filter the dhcp ip
        ###############################################################################
        # sniff(iface = self.interface, stop_filter = self.check_tcp_ip, timeout = 100)
        # if self.hostname:
        #     pass
        # else:
        #     self.hostname = STARTUP.check_dhcp_status()
        self.hostname = configur.get('INFO','static_ip')
        ###############################################################################
        ## Check Static IP Ping
        ###############################################################################
        timeout = time.time()+60
        print(f'{"-"*100}\nCheck the status of Static ip ping\n{"-"*100}')
        while time.time()<timeout:
            if STARTUP.ping_status(self.hostname):
                self.summary.append(['Static IP Ping ','Successful'])
                print('-'*100)
                print(f' '.join(self.summary[-1]))
                ping_out = subprocess.getoutput("ping -c 5 {}".format(self.hostname))
                break
        else:
            return f'Static IP {self.hostname} not Pinging'


        try:
            STARTUP.delete_system_log(host= self.hostname)
            time.sleep(2)
            print(f'{"-"*100}\nEstablishing Netopeer Connection')
            ###############################################################################
            ## Perform call home to get ip_details
            ###############################################################################
            self.session, self.login_info = STARTUP.session_login(host = self.hostname,USER_N = self.USER_N,PSWRD = self.PSWRD)

            if self.session:
                self.summary.append(['Netopeer Connection ','Successful'])
                print('-'*100)
                print(f' '.join(self.summary[-1]))
                self.RU_Details = STARTUP.Software_detail(session = self.session)
                del self.RU_Details['swRecoverySlot']

                ###############################################################################
                ## Test Description
                ###############################################################################
                for key, val in self.RU_Details.items():
                    if (val[0] == 'true' and val[1] == 'true'):
                        Test_Desc = 'Test Description :  This test validates that the O-RU can successfully perform a software slot switch procedure.'
                        CONFIDENTIAL = STARTUP.ADD_CONFIDENTIAL('Slot_Switch',SW_R = val[2]) 
                        STARTUP.STORE_DATA(CONFIDENTIAL,Format='CONF',PDF= self.pdf)
                        STARTUP.STORE_DATA(Test_Desc,Format='DESC',PDF= self.pdf)
                        self.pdf.add_page()
                        self.running_sw = val[2]
                    elif (val[0] == 'true' and val[1] == 'false'):
                        Test_Desc = 'Test Description :  This test validates that the O-RU can successfully perform a software slot switch procedure.'
                        CONFIDENTIAL = STARTUP.ADD_CONFIDENTIAL('Slot_Switch',SW_R = val[2]) 
                        STARTUP.STORE_DATA(CONFIDENTIAL,Format='CONF',PDF= self.pdf)
                        STARTUP.STORE_DATA(Test_Desc,Format='DESC',PDF= self.pdf)
                        self.pdf.add_page()
                        self.inactive_slot = key
                    else:
                        self.running_false = val[2]
                        self.inactive_slot = key

                
                STARTUP.STORE_DATA('{}'.format(cmd).center(100),Format=True,PDF=self.pdf)
                STARTUP.STORE_DATA(ethtool_out,Format=False,PDF=self.pdf)
                STARTUP.STORE_DATA('{}'.format("ping -c 5 {}".format(self.hostname)).center(100),Format=True,PDF=self.pdf)
                STARTUP.STORE_DATA(ping_out,Format=False,PDF=self.pdf)

                Res1 = self.netopeer_connection_and_capability()
                if Res1 != True:
                    return Res1
                Res2 = self.software_activate()
                if Res2 != True:
                    return Res2
                Res3 = self.reset_rpc()
                if Res3 != True:
                    return Res3
                return True
            
                
        ###############################################################################
        ## Exception
        ###############################################################################
        except socket.timeout as e:
            Error = '{} : Call Home is not initiated, SSH Socket connection lost....'.format(
                e)
            STARTUP.STORE_DATA(Error, Format=True,PDF=self.pdf)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=self.pdf)
            return Error
            
        except RPCError as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=self.pdf)
            # self.session.close_session()
            return [e.type, e.tag, e.severity, e.path, e.message, exc_tb.tb_lineno]

        except Exception as e:
            STARTUP.STORE_DATA('{}'.format(e), Format=True,PDF=self.pdf)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=self.pdf)
            # self.session.close_session()
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
        if Check1 == False or Check1 == None:
            self.summary.append(['SFP Link Detection','Fail'])
            return Check1
        
        cmd = "ethtool " + self.INTERFACE_NAME
        ethtool_out = subprocess.getoutput(cmd)
        self.summary.append(['SFP Link Detection','Successful'])
        # sniff(iface = self.interface, stop_filter = self.check_tcp_ip, timeout = 100)

        # if self.hostname:
        #     pass
        # else:
        #     self.hostname = STARTUP.check_dhcp_status()

        ###############################################################################
        ## Check Static IP Ping
        ###############################################################################
        timeout = time.time()+60
        print(f'{"-"*100}\nCheck the status of Static ip ping\n{"-"*100}')
        while time.time()<timeout:
            ping_out = subprocess.getoutput("ping -c 5 {}".format(self.hostname))
            if STARTUP.ping_status(self.hostname):
                self.summary.append(['Static IP Ping ','Successful'])
                print('-'*100)
                print(f' '.join(self.summary[-1]))
                break
        else:
            STARTUP.STORE_DATA('{}'.format(cmd).center(100),Format=True,PDF=self.pdf)
            STARTUP.STORE_DATA(ethtool_out,Format=False,PDF=self.pdf)
            STARTUP.STORE_DATA('{}'.format("ping -c 5 {}".format(self.hostname)).center(100),Format=True,PDF=self.pdf)
            STARTUP.STORE_DATA(ping_out,Format=False,PDF=self.pdf)
            return f'Static IP {self.hostname} not Pinging'

        STARTUP.STORE_DATA('{}'.format(cmd).center(100),Format=True,PDF=self.pdf)
        STARTUP.STORE_DATA(ethtool_out,Format=False,PDF=self.pdf)
        STARTUP.STORE_DATA('{}'.format("ping -c 5 {}".format(self.hostname)).center(100),Format=True,PDF=self.pdf)
        STARTUP.STORE_DATA(ping_out,Format=False,PDF=self.pdf)

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
                    STARTUP.STORE_DATA(xml_pretty_str, Format='XML', PDF=self.pdf)
                    self.summary.append([f'Running Software after boot',f'{self.running_false}'])
                    print('-'*100)
                    print(f' '.join(self.summary[-1]))
                    self.summary.append([f'Software {self.inactive_slot}','Successfuly Switch and Running'])
                    print('-'*100)
                    print(f' '.join(self.summary[-1]))
                    return True
                
            ###############################################################################
            ## Exception
            ###############################################################################
            except socket.timeout as e:
                Error = '{} : Call Home is not initiated, SSH Socket connection lost....'.format(
                    e)
                STARTUP.STORE_DATA(Error, Format=True,PDF=self.pdf)
                exc_type, exc_obj, exc_tb = sys.exc_info()
                STARTUP.STORE_DATA(
                    f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=self.pdf)
                return Error

            except RPCError as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                STARTUP.STORE_DATA(
                    f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=self.pdf)
                # self.session.close_session()
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
        time.sleep(40)
        Res1 = self.get_config_detail()
        time.sleep(10)
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
            STARTUP.ACT_RES(f"{'O-RU Software Update and Install' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= self.pdf,COL=(255,0,0))
            self.summary.append([f'FAIL_REASON','SFP link not detected'])
            print('-'*100)
            print(f' '.join(self.summary[-1]))
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
            Exp_Result = '''Expected Result : 1. The status of the software slot used for software activation remains VALID (it is unchanged) and the parameter "active" remains "True". The parameter "running" is set to True.
            2. Status of the software slot containing the previous version of software used by device remains VALID, the parameter "active" remains False. The parameter "running" is set to False.'''
            STARTUP.STORE_DATA(Exp_Result,Format='DESC',PDF= self.pdf)

            STARTUP.STORE_DATA('\t\t{}'.format('****************** Actual Result ******************'),Format=True,PDF= self.pdf)
            try:
                if Check2 == True:
                    STARTUP.ACT_RES(f"{'Slot Switch' : <50}{'=' : ^20}{'SUCCESS' : ^20}",PDF= self.pdf,COL=(0,255,0))
                    return True

                else:
                    if type(Check2) == list:
                        STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= self.pdf)
                        Error_Info = '''ERROR\n\terror-type \t: \t{}\n\terror-tag \t: \t{}\n\terror-severity \t: \t{}\n\tmessage' \t: \t{}'''.format(*map(str,Check2))
                        STARTUP.STORE_DATA(Error_Info,Format=False,PDF= self.pdf)
                        STARTUP.ACT_RES(f"{'Slot Switch' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= self.pdf,COL=(255,0,0))
                        self.summary.append([f'FAIL_REASON',Error_Info])
                        print('-'*100)
                        print(f' '.join(self.summary[-1]))
                        return False

                    else:
                        STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= self.pdf)
                        STARTUP.STORE_DATA('{}'.format(Check2),Format=False,PDF= self.pdf)
                        STARTUP.ACT_RES(f"{'Slot Switch' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= self.pdf,COL=(255,0,0))
                        self.summary.append([f'FAIL_REASON','{}'.format(Check2)])
                        print('-'*100)
                        print(f' '.join(self.summary[-1]))
                        return False

            except Exception as e:
                STARTUP.STORE_DATA('{}'.format(e), Format=True,PDF=self.pdf)
                exc_type, exc_obj, exc_tb = sys.exc_info()
                STARTUP.STORE_DATA(
                    f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=self.pdf)
                self.summary.append([f'Exception','{}'.format(e)])
                print('-'*100)
                print(f' '.join(self.summary[-1]))
                return False
            ###############################################################################
            ## For Capturing the logs
            ###############################################################################
            finally:
                STARTUP.HEADING(PDF=self.pdf,data='{0} Summary {0}'.format('*'*30))
                STARTUP.render_table_data(self.pdf,self.summary)
                STARTUP.CREATE_LOGS('Slot_Switch',PDF=self.pdf)

        else:
            STARTUP.STORE_DATA('\t\t\t\t############ SYSTEM LOGS ##############',Format=True,PDF=self.pdf)
            for i in self.logs1:
                STARTUP.STORE_DATA("{}".format(i),Format=False,PDF=self.pdf)
            ###############################################################################
            ## Expected/Actual Result
            ###############################################################################
            self.pdf.add_page()
            Exp_Result = '''Expected Result : 1. The status of the software slot used for software activation remains VALID (it is unchanged) and the parameter "active" remains "True". The parameter "running" is set to True.
            2. Status of the software slot containing the previous version of software used by device remains VALID, the parameter "active" remains False. The parameter "running" is set to False.'''
            STARTUP.STORE_DATA(Exp_Result, Format='DESC', PDF=self.pdf)

            STARTUP.STORE_DATA('\t\t{}'.format('****************** Actual Result ******************'), Format=True, PDF=self.pdf)
            try:

                if type(Check1) == list:
                    STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= self.pdf)
                    Error_Info = '''ERROR\n\terror-type \t: \t{}\n\terror-tag \t: \t{}\n\terror-severity \t: \t{}\n\tmessage' \t: \t{}'''.format(*map(str,Check1))
                    STARTUP.STORE_DATA(Error_Info,Format=False,PDF= self.pdf)
                    STARTUP.ACT_RES(f"{'Slot Switch' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= self.pdf,COL=(255,0,0))
                    self.summary.append([f'FAIL_REASON',Error_Info])
                    print('-'*100)
                    print(f' '.join(self.summary[-1]))
                    return False
                else:
                    STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= self.pdf)
                    STARTUP.STORE_DATA('{}'.format(Check1),Format=False,PDF= self.pdf)
                    STARTUP.ACT_RES(f"{'Slot Switch' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= self.pdf,COL=(255,0,0))
                    self.summary.append([f'FAIL_REASON','{}'.format(Check1)])
                    print('-'*100)
                    print(f' '.join(self.summary[-1]))
                    return False


            except Exception as e:
                    STARTUP.STORE_DATA('{}'.format(e), Format=True,PDF=self.pdf)
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    STARTUP.STORE_DATA(
                        f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=self.pdf)
                    self.summary.appedn([f'Exception','{}'.format(e)])
                    print('-'*100)
                    print(f' '.join(self.summary[-1]))
                    return False

            ###############################################################################
            ## For Capturing the logs
            ###############################################################################
            finally:
                STARTUP.HEADING(PDF=self.pdf,data='{0} Summary {0}'.format('*'*30))
                STARTUP.render_table_data(self.pdf,self.summary)
                STARTUP.CREATE_LOGS('Slot_Switch',PDF=self.pdf)


### api name of software update testcase
def slot_change(nums):
    st_time = datetime.now()
    Test_procedure = [f"{'='*100}\nTest case *Slot Switch* Started!! Status: Running\n{'='*100}",
            'Start Time : {}'.format(st_time.strftime('%c')),'** Test Coverage **'.center(50),'Static IP Ping', 
                'Netopeer Connection','Capability exchange and create-subscription','Software Activate for slot switch',
                'Configure Reset RPC']
    notification('\n'.join(Test_procedure))
    Pass = 0
    fail = 0
    for i in range(nums):
        iteration_time = datetime.now()
        slot_switch = Slot_Switch()
        Result = slot_switch.Main_Function()
        if Result:
            Pass+=1
            pass
        else:
            fail+=1
        notification(f"{'='*100}\nIteration {i+1}\n{'='*100}")
        smry = ['** Result **'.center(50)]
        for i in slot_switch.summary:
            smry.append('{0} || {1}'.format(i[0],i[1]))
        en_time = datetime.now()
        smry.append('Start Time : {}'.format(iteration_time.strftime('%c')))
        smry.append('End Time : {}'.format(en_time.strftime('%c')))
        notification('\n'.join(smry))
        notification(f'{"="*100}\nStatus \t\t=\t {"Pass" if Result else "Fail"}\n{"="*100}')
    end_time = datetime.now()
    t1 = 'Start Time : {}'.format(st_time.strftime('%c'))
    t2 = 'End Time : {}'.format(end_time.strftime('%c'))
    
    total_time = (int((end_time-st_time).seconds),60)
    total_time = '{0} min {1} sec'.format(total_time[0],total_time[1])
    notification(''.join((t1,t2,total_time)))
    notification('{3}\nTotal iteration: {0}, Pass: {1}, Fail: {2}\n{3}'.format(nums,Pass,fail,'='*100))
    return Result, slot_switch.summary, int((end_time-st_time).seconds)


if __name__ == "__main__":
    try:
        if len(sys.argv)>1:
            Result = slot_change(int(sys.argv[1]))
        else:
            Result = slot_change(1)
    except Exception as e:
        print(e)
        print('Please run with following command: python slot_swtich_n_times.py 1/2/3')



