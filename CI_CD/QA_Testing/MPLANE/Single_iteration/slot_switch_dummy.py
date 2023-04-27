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
from require.Configuration import *


class Slot_Switch(PDF,netopeer_connection,Configuration,genrate_pdf_report):
    # init method or constructor 
    def __init__(self):
        super().__init__()
        netopeer_connection.__init__(self)
        Configuration.__init__(self)
        genrate_pdf_report.__init__(self)
        self.PDF_CAP()
        self.summary = []
        self.logs1, self.logs2 = '', ''
        self.sw_inv = '''<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            <software-inventory xmlns="urn:o-ran:software-management:1.0">
            </software-inventory>
            </filter>'''


    ###############################################################################
    ## Did the create subscription
    ###############################################################################
    def create_subscribe(self):
        try:
            filter = """<filter type="xpath" xmlns="urn:ietf:params:xml:ns:netconf:notification:1.0" xmlns:swm="urn:o-ran:software-management:1.0" select="/swm:*"/>"""
            cmd = '> subscribe --filter-xpath /o-ran-software-management:*'
            self.create_subscription(filter=filter,cmd=cmd)
            return True

        except Exception as e:
            self.STORE_DATA('{}'.format(e), Format=True,)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            self.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,)
            return f"{e} Create_subscribe"
        
    def software_activate(self):
        try:
            self.summary.append([f'Running Software',f'{self.running_sw}'])
            print('-'*100)
            print(f' '.join(self.summary[-1]))
            print(f'{"-"*100}\nConfiguring SW Activate RPC')
            ###############################################################################
            ## Initial Get Filter
            ###############################################################################
            self.add_page()
            self.STORE_DATA('\t\tInitial Get Filter',Format='TEST_STEP',)
            cmd = '\n> get --filter-xpath /o-ran-software-management:software-inventory'
            xml_pretty_str,slot_n = self.get(filter=self.sw_inv,cmd=cmd)

            sw_detail = self.Software_detail()
            del sw_detail['swRecoverySlot']
            for key, val in sw_detail.items():
                if val[3] == 'INVALID':
                    self.STORE_DATA(xml_pretty_str, Format='XML',)
                    return 'SW slot status is Invalid...'
                if (val[0] == 'false' and val[1] == 'false') or (val[0] == 'true' and val[1] == 'true'):
                    pass
                else:
                    self.STORE_DATA(xml_pretty_str, Format='XML')
                    print(sw_detail)
                    self.reboot_ru(self.hostname)
                    return 'Slots Active and Running Status are diffrent...'
            self.STORE_DATA(xml_pretty_str, Format='XML',)

            ###############################################################################
            ## Test Procedure 1 : Configure SW Activate RPC in RU
            ###############################################################################
            Test_Step1 = '\t\tStep 1 : TER NETCONF Client triggers <rpc><software-activate> Slot must have attributes active = FALSE, running = FALSE.'
            self.STORE_DATA('{}'.format(Test_Step1), Format='TEST_STEP', )
            xml_data2 = open("{}/require/Yang_xml/sw_activate.xml".format(parent)).read()
            xml_data2 = xml_data2.format(slot_name=self.inactive_slot)

            ###############################################################################
            ## Test Procedure 2 : O-RU NETCONF Server responds with <software-activate>
            ###############################################################################
            Test_Step2 = '\t\tStep 2 : O-RU NETCONF Server responds with <rpc-reply><software-activate><status>. The parameter "status" is set to STARTED.'
            self.STORE_DATA('{}'.format(Test_Step2),Format='TEST_STEP', )
            rpc_reply = self.send_rpc(rpc_data=xml_data2)
            if rpc_reply != True:
                return rpc_reply

            ###############################################################################
            ## Capture_The_Notifications
            ###############################################################################
            filter =  'activation-event'
            dict_notification = self.captured_notifications(filter=filter)
            if type(dict_notification) == dict:
                status = dict_notification['status']
                if status != 'COMPLETED':
                    return status
            else:
                return dict_notification

            ###############################################################################
            ## POST_GET_FILTER
            ###############################################################################
            time.sleep(5)
            self.add_page()
            cmd = '\n> get --filter-xpath /o-ran-software-management:software-inventory'
            xml_pretty_str,slot_n1 = self.get(filter=self.sw_inv,cmd=cmd)

            sw_detail = self.Software_detail()
            del sw_detail['swRecoverySlot']

            for key, val in sw_detail.items():
                if val[3] == 'INVALID' and key !=self.inactive_slot:
                    self.STORE_DATA(xml_pretty_str, Format='XML', )
                    return f'SW slot status is Invid for {key}...'
                elif key == self.inactive_slot:
                    if (val[0] == 'true') and val[1] == 'false':
                        pass
                    else:
                        self.STORE_DATA(xml_pretty_str, Format='XML', )
                        return f"SW Inventory didn't update for {self.inactive_slot}..."
                elif key != self.inactive_slot:
                    if (val[0] == 'false') and val[1] == 'true':
                        pass
                    else:
                        self.STORE_DATA(xml_pretty_str, Format='XML', )
                        return f"SW Inventory didn't update for {key}..."

            self.STORE_DATA(xml_pretty_str, Format='XML', )
            self.summary.append([f'Software {self.running_false_sw} Activate', f'Successfully activate on {self.inactive_slot}'])
            print('-'*100)
            print(f' '.join(self.summary[-1]))
            return True

        except Exception as e:
            self.STORE_DATA('{}'.format(e), Format=True,)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            self.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,)
            return f"{e} Software Activate"

    def reset_rpc(self):
        ###############################################################################
        ## Test Procedure 1 : Configure_Reset_RPC_in_RU
        ###############################################################################
        print(f'{"-"*100}\nConfiguring SW Reset RPC')
        Test_Step1 = '\t\tStep 1 : TER NETCONF Client sends <rpc><reset></rpc> to the O-RU NETCONF Server..'
        self.STORE_DATA('{}'.format(Test_Step1),Format='TEST_STEP', )
        xml_data3 = '''<reset xmlns="urn:o-ran:operations:1.0"></reset>'''
        rpc_reply = self.send_rpc(rpc_data=xml_data3)
        if not rpc_reply:
            return rpc_reply

        Test_Step3 = '\t\tStep 3 : O-RU restarts with a new software version running matching the version activated.'
        self.STORE_DATA('{}'.format(Test_Step3),Format='TEST_STEP', )
        self.summary.append(['O-RU going for reboot:','Successful'])
        print('-'*100)
        print(f' '.join(self.summary[-1]))
        return True
    
    ###############################################################################
    ## Befor_sending_Reset_rpc
    ###############################################################################
    def Befor_sending_Reset_rpc(self):
        Output = self.Link_detction_and_check_ping(self)
        if Output[-1]!=True:
            return Output[0]

        try:
            time.sleep(10)
            self.delete_system_log(host= self.hostname)
            print(f'{"-"*100}\nEstablishing Netopeer Connection')
            ###############################################################################
            ## Perform call home to get ip_details
            ###############################################################################
            self.session_login(timeout=10)
            
            if self.session:
                self.summary.append(['Netopeer Connection ','Successful'])
                print('-'*100)
                print(f' '.join(self.summary[-1]))
                Test_Description =  'This test validates that the O-RU can successfully perform a software slot switch procedure.'
                Result = self.add_test_description(Test_Description=Test_Description, Test_Case_name='Slot_Switch')
                if len(Result) > 2:
                    self.running_sw, self.running_false_sw, self.inactive_slot = Result[0], Result[1], Result[2]

                self.STORE_DATA('{}'.format(Output[2]).center(100),Format=True,)
                self.STORE_DATA(Output[0],Format=False,)
                self.STORE_DATA('{}'.format("ping -c 5 {}".format(self.hostname)).center(100),Format=True,)
                self.STORE_DATA(Output[1],Format=False,)

                self.add_netopeer_connection_details()
                Res1 = self.hello_capability()
                if Res1 != True:
                    return Res1
                Res2 = self.create_subscribe()
                if Res2 != True:
                    return Res2
                Res3 = self.software_activate()
                if Res3 != True:
                    return Res3
                Res4 = self.reset_rpc()
                if Res4 != True:
                    return Res4
                return True
            
                
        ###############################################################################
        ## Exception
        ###############################################################################
        except socket.timeout as e:
            Error = '{} : Call Home is not initiated, SSH Socket connection lost....'.format(
                e)
            self.STORE_DATA(Error, Format=True,)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            self.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,)
            return Error
            
        except RPCError as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            self.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,)
            # self.session.close_session()
            return [e.type, e.tag, e.severity, e.path, e.message, exc_tb.tb_lineno]

        except Exception as e:
            self.STORE_DATA('{}'.format(e), Format=True,)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            self.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,)
            # self.session.close_session()
            return e 
        
        finally:
            self.logs1 = self.system_logs(self.hostname)
            try:
                self.session.close_session()
            except Exception as e:
                print(e)

    ###############################################################################
    ## Check wether slot switch is successful
    ###############################################################################
    def Check_slot_switch_successful(self):
        Output = self.Link_detction_and_check_ping(self)
        if Output[-1]!=True:
            return Output[0]

        ###############################################################################
        ## Perform Call Home to get IP after RU comes up
        ###############################################################################
        t = time.time() +30
        while time.time() < t:
            try:
                self.session_login(timeout=10)

                if self.session:
                    ###############################################################################
                    ## Check the get filter of SW
                    ###############################################################################
                    cmd = '\n> get --filter-xpath /o-ran-software-management:software-inventory'
                    xml_pretty_str,dict_slots = self.get(filter=self.sw_inv,cmd=cmd)

                    li = ['INVALID', 'EMPTY']
                    SLOTS_INFO = dict_slots['data']['software-inventory']['software-slot']
                    for i in SLOTS_INFO:
                        if i['status'] in li:
                            self.STORE_DATA(xml_pretty_str,Format='XML', )
                            return f'{i["name"]} status is not correct....'
                    self.STORE_DATA(xml_pretty_str, Format='XML', )
                    self.summary.append([f'Running Software after boot',f'{self.running_false_sw}'])
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
                self.STORE_DATA(Error, Format=True,)
                exc_type, exc_obj, exc_tb = sys.exc_info()
                self.STORE_DATA(
                    f"Error occured in line number {exc_tb.tb_lineno}", Format=False,)
                return Error

            except RPCError as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                self.STORE_DATA(
                    f"Error occured in line number {exc_tb.tb_lineno}", Format=False,)
                # self.session.close_session()
                return [e.type, e.tag, e.severity, e.path, e.message, exc_tb.tb_lineno]

            finally:
                try:
                    self.session.close_session()
                except Exception as e:
                    print(e)
                pass
        else:
            return 'Cannection not Established...'

    ###############################################################################
    ## Check_the_slot_status_after_slot_switch
    ###############################################################################
    def Check_the_slot_status_after_slot_switch(self):
        self.waittime = configur.getint('INFO','wait_time')
        time.sleep(self.waittime-30)
        Res1 = self.Check_slot_switch_successful()
        print(self.hostname,'Check_the_slot_status_after_slot_switch')
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
                time.sleep(2)
                pass
        else:
            return 'Can\'t connect to the RU.., Logs are not captured.'

    ###############################################################################
    ## Main Function
    ###############################################################################
    def Main_Function(self):
        Check1 = self.Befor_sending_Reset_rpc()
        if Check1 == False:
            self.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True)
            self.STORE_DATA('SFP link not detected...',Format=False)
            self.ACT_RES(f"{'Slot Switch' : <50}{'=' : ^20}{'FAIL' : ^20}",COL=(255,0,0))
            self.summary.append([f'FAIL_REASON','SFP link not detected'])
            print('-'*100)
            print(f' '.join(self.summary[-1]))
            return False

        elif Check1 == True:
            Check2 = self.Check_the_slot_status_after_slot_switch()
            self.STORE_DATA('\t\t\t\t############ SYSTEM LOGS ##############',Format=True,)
            for i in self.logs1:
                self.STORE_DATA("{}".format(i),Format=False,)
            for i in self.logs2:
                self.STORE_DATA("{}".format(i),Format=False,)
            ###############################################################################
            ## Expected/Actual Result
            ###############################################################################
            self.add_page()
            Exp_Result = '''Expected Result : 1. The status of the software slot used for software activation remains VALID (it is unchanged) and the parameter "active" remains "True". The parameter "running" is set to True.
            2. Status of the software slot containing the previous version of software used by device remains VALID, the parameter "active" remains False. The parameter "running" is set to False.'''
            self.STORE_DATA(Exp_Result,Format='DESC')

            self.STORE_DATA('\t\t{}'.format('****************** Actual Result ******************'),Format=True)
            try:
                if Check2 == True:
                    self.ACT_RES(f"{'Slot Switch' : <50}{'=' : ^20}{'SUCCESS' : ^20}",COL=(0,255,0))
                    return True

                else:
                    if type(Check2) == list:
                        self.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True)
                        Error_Info = '''ERROR\n\terror-type \t: \t{}\n\terror-tag \t: \t{}\n\terror-severity \t: \t{}\n\tmessage' \t: \t{}'''.format(*map(str,Check2))
                        self.STORE_DATA(Error_Info,Format=False)
                        self.ACT_RES(f"{'Slot Switch' : <50}{'=' : ^20}{'FAIL' : ^20}",COL=(255,0,0))
                        self.summary.append([f'FAIL_REASON',Error_Info])
                        print('-'*100)
                        print(f' '.join(self.summary[-1]))
                        return False

                    else:
                        self.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True)
                        self.STORE_DATA('{}'.format(Check2),Format=False)
                        self.ACT_RES(f"{'Slot Switch' : <50}{'=' : ^20}{'FAIL' : ^20}",COL=(255,0,0))
                        self.summary.append([f'FAIL_REASON','{}'.format(Check2)])
                        print('-'*100)
                        print(f' '.join(self.summary[-1]))
                        return False

            except Exception as e:
                self.STORE_DATA('{}'.format(e), Format=True,)
                exc_type, exc_obj, exc_tb = sys.exc_info()
                self.STORE_DATA(
                    f"Error occured in line number {exc_tb.tb_lineno}", Format=False,)
                self.summary.append([f'Exception','{}'.format(e)])
                print('-'*100)
                print(f' '.join(self.summary[-1]))
                return False
            ###############################################################################
            ## For Capturing the logs
            ###############################################################################
            finally:
                self.HEADING(data='{0} Summary {0}'.format('*'*30))
                self.render_table_data(self.summary)
                self.CREATE_LOGS('Slot_Switch')

        else:
            self.STORE_DATA('\t\t\t\t############ SYSTEM LOGS ##############',Format=True)
            for i in self.logs1:
                self.STORE_DATA("{}".format(i),Format=False,)
            ###############################################################################
            ## Expected/Actual Result
            ###############################################################################
            self.add_page()
            Exp_Result = '''Expected Result : 1. The status of the software slot used for software activation remains VALID (it is unchanged) and the parameter "active" remains "True". The parameter "running" is set to True.
            2. Status of the software slot containing the previous version of software used by device remains VALID, the parameter "active" remains False. The parameter "running" is set to False.'''
            self.STORE_DATA(Exp_Result, Format='DESC', )

            self.STORE_DATA('\t\t{}'.format('****************** Actual Result ******************'), Format=True, )
            try:

                if type(Check1) == list:
                    self.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True)
                    Error_Info = '''ERROR\n\terror-type \t: \t{}\n\terror-tag \t: \t{}\n\terror-severity \t: \t{}\n\tmessage' \t: \t{}'''.format(*map(str,Check1))
                    self.STORE_DATA(Error_Info,Format=False)
                    self.ACT_RES(f"{'Slot Switch' : <50}{'=' : ^20}{'FAIL' : ^20}",COL=(255,0,0))
                    self.summary.append([f'FAIL_REASON',Error_Info])
                    print('-'*100)
                    print(f' '.join(self.summary[-1]))
                    return False
                else:
                    self.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True)
                    self.STORE_DATA('{}'.format(Check1),Format=False)
                    self.ACT_RES(f"{'Slot Switch' : <50}{'=' : ^20}{'FAIL' : ^20}",COL=(255,0,0))
                    self.summary.append([f'FAIL_REASON','{}'.format(Check1)])
                    print('-'*100)
                    print(f' '.join(self.summary[-1]))
                    return False


            except Exception as e:
                    self.STORE_DATA('{}'.format(e), Format=True,)
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    self.STORE_DATA(
                        f"Error occured in line number {exc_tb.tb_lineno}", Format=False,)
                    self.summary.appedn([f'Exception','{}'.format(e)])
                    print('-'*100)
                    print(f' '.join(self.summary[-1]))
                    return False

            ###############################################################################
            ## For Capturing the logs
            ###############################################################################
            finally:
                self.HEADING(data='{0} Summary {0}'.format('*'*30))
                self.render_table_data(self.summary)
                self.CREATE_LOGS('Slot_Switch')



### api name of software update testcase
def slot_change():
    Test_procedure = [f"{'='*100}\nTest case *Slot Switch* Started!! Status: Running\n{'='*100}",'** Test Coverage **'.center(50),'Static IP Ping',
                'Netopeer Connection','Capability exchange and create-subscription','Software Activate for slot switch',
                'Configure Reset RPC']
    notification('\n'.join(Test_procedure))
    start_time = time.time()
    slot_switch = Slot_Switch()
    Result = slot_switch.Main_Function()
    end_time = time.time()
    print('{0}\nExecution Time is : {1}'.format("="*100,int(end_time-start_time)))
    smry = ['\n','** Result **'.center(50)]
    for i in slot_switch.summary:
        smry.append('{0} || {1}'.format(i[0],i[1]))
    notification('\n'.join(smry))
    notification(f"{'='*100}\nStatus\t\t=\t{Result}\n{'='*100}")
    return Result, slot_switch.summary, int(end_time-start_time)


if __name__ == "__main__":
    Result = slot_change()
