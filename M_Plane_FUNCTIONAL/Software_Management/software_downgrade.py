###############################################################################
##@ FILE NAME:      Software downgrade time taken
##@ TEST SCOPE:     M PLANE O-RAN Functional
##@ Version:        V_1.0.0
##@ Support:        @Ramiyer, @VaibhavDhiman, @PriyaSharma
###############################################################################

###############################################################################
## Package Imports 
###############################################################################

import sys, os, time, xmltodict, xml.dom.minidom, lxml.etree, ifcfg, paramiko
from ncclient import manager
from ncclient.operations.rpc import RPC, RPCError
from ncclient.transport import errors
from paramiko.ssh_exception import NoValidConnectionsError
from ncclient.operations.errors import TimeoutExpiredError
from ncclient.transport.errors import SessionCloseError
from ncclient.xml_ import to_ele
from configparser import ConfigParser

###############################################################################
## Directory Path
###############################################################################
dir_name = os.path.dirname(os.path.abspath(__file__))
parent = os.path.dirname(dir_name)
print(parent)
sys.path.append(parent)

########################################################################
## For reading data from .ini file
########################################################################
configur = ConfigParser()
configur.read('{}/inputs.ini'.format(dir_name))

###############################################################################
## Related Imports
###############################################################################
from require import STARTUP, Config
from require.Vlan_Creation import *



###############################################################################
## Initiate PDF
###############################################################################
pdf_log = STARTUP.PDF_CAP()

class software_downgrade(vlan_Creation):

    def __init__(self) -> None:
        super().__init__()
        try:
            Check1 = self.linked_detected()
            if Check1 == False or Check1 == None:
                return Check1

            sniff(iface = self.interface, stop_filter = self.check_tcp_ip, timeout = 100)
            STARTUP.delete_system_log(host= self.hostname)
            self.port = 830
            self.USER_N = configur.get('INFO', 'sudo_user')
            self.PSWRD = configur.get('INFO', 'sudo_pass')
            self.du_password = Config.details['DU_PASS']
            self.session = manager.connect(host = self.hostname, port=830, hostkey_verify=False,username = self.USER_N, password = self.PSWRD ,allow_agent = False , look_for_keys = False)
            data = STARTUP.demo(self.session)
            self.users, self.slots, self.macs = data[0], data[1], data[2]
            pass
        except Exception as e:
            STARTUP.STORE_DATA('{}'.format(e), Format = True,PDF=pdf_log)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format = False,PDF=pdf_log)
            return '{}'.format(e)

    ###############################################################################
    ## Get_Filter_after_Reboot_the_RU
    ###############################################################################
    def get_config_detail(self):
        self.linked_detected()
        sniff(iface = self.interface, stop_filter = self.check_tcp_ip, timeout = 100)
        self.hostname1 = self.hostname
        ###############################################################################
        ## Perform Call Home to get IP after RU comes up
        ###############################################################################
        t = time.time() +20
        while time.time() < t:
            try:
                self.session2, self.login_info = STARTUP.session_login(host = self.hostname1,USER_N = self.USER_N,PSWRD = self.PSWRD)

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
                            STARTUP.STORE_DATA(xml_pretty_str,Format='XML', PDF=pdf_log)
                            return f'{i["name"]} status is not correct....'
                    STARTUP.STORE_DATA(xml_pretty_str, Format='XML', PDF=pdf_log)
                    # self.session2.close_session()
                    return True
                
            ###############################################################################
            ## Exception
            ###############################################################################
            except socket.timeout as e:
                Error = '{} : Call Home is not initiated, SSH Socket connection lost....'.format(
                    e)
                STARTUP.STORE_DATA(Error, Format=True,PDF=pdf_log)
                exc_type, exc_obj, exc_tb = sys.exc_info()
                STARTUP.STORE_DATA(
                    f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf_log)
                return Error

            except RPCError as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                print(
                    f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf_log)
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


    def sw_activate_with_reset(self):
        try:
            ###############################################################################
            ## Test Step 1 Connect to the Netconf-Server
            ###############################################################################
            STARTUP.STORE_DATA('********** Connect to the NETCONF Server ***********',Format='TEST_STEP',PDF=pdf_log)
            STATUS = STARTUP.STATUS(self.hostname,self.USER_N,self.session.session_id,self.port)
            STARTUP.STORE_DATA(STATUS,Format=False,PDF=pdf_log)

            for i in self.session.server_capabilities:
                STARTUP.STORE_DATA('{}'.format(i),Format=False,PDF=pdf_log)


            ###############################################################################
            ## Create Subscription
            ###############################################################################                
            cap = self.session.create_subscription()
            STARTUP.STORE_DATA('********** Create Subscription ***********',Format=True,PDF=pdf_log)
            STARTUP.STORE_DATA('>subscribe',Format=True,PDF=pdf_log)
            dict_data = xmltodict.parse(str(cap))
            if dict_data['nc:rpc-reply']['nc:ok']== None:
                STARTUP.STORE_DATA('\nOk\n',Format=False,PDF=pdf_log)

            ###############################################################################
            ## Initial Get Filter
            ###############################################################################
            pdf_log.add_page()
            STARTUP.STORE_DATA('\t\tInitial Get Filter',Format='TEST_STEP', PDF=pdf_log)
            STARTUP.STORE_DATA(
                '\n> get --filter-xpath /o-ran-software-management:software-inventory', Format=True, PDF=pdf_log)
            sw_inv = '''<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            <software-inventory xmlns="urn:o-ran:software-management:1.0">
            </software-inventory>
            </filter>'''
            slot_names = self.session.get(sw_inv).data_xml

            # ###############################################################################
            # ## Checking The status, active and running value
            # ###############################################################################
            # s = xml.dom.minidom.parseString(slot_names)
            # xml_pretty_str = s.toprettyxml()
            # slot_n = xmltodict.parse(str(slot_names))
            # SLOTS = slot_n['data']['software-inventory']['software-slot']
            # SLOT_INFO = {}
            # for SLOT in SLOTS:
            #     if SLOT['status'] == 'INVALID':
            #         STARTUP.STORE_DATA(xml_pretty_str, Format='XML', PDF=pdf_log)
            #         return f'SW slot status is Invalid for {SLOT["name"]}...'
            #     if (SLOT['name'] != 'swRecoverySlot'):
            #         SLOT_INFO[SLOT['name']] = [SLOT['active'], SLOT['running']]

            #     if (SLOT['active'] == 'true' and SLOT['running'] == 'true') or (SLOT['active'] == 'false' and SLOT['running'] == 'false'):
            #         if (SLOT['active'] == 'false' and SLOT['running'] == 'false') and (SLOT['name'] != 'swRecoverySlot'):
            #             slot_name = SLOT['name']
            #             del SLOT_INFO[SLOT['name']]
            #         pass
            #     else:
            #         return f'Slots Active and Running Status are diffrent for {SLOT["name"]}...'

            # DEACTIVE_SLOT = list(SLOT_INFO.keys())
            # STARTUP.STORE_DATA(xml_pretty_str, Format='XML', PDF=pdf_log)



            # ###############################################################################
            # ## Test Procedure 1 : Configure SW Activate RPC in RU
            # ###############################################################################
            # Test_Step1 = '\t\tStep 1 : TER NETCONF Client triggers <rpc><software-activate> Slot must have attributes active = FALSE, running = FALSE.'
            # STARTUP.STORE_DATA('{}'.format(Test_Step1), Format='TEST_STEP', PDF=pdf_log)
            # xml_data2 = f"""<software-activate xmlns="urn:o-ran:software-management:1.0">
            #             <slot-name>{slot_name}</slot-name>
            #             </software-activate>"""

            # STARTUP.STORE_DATA('\n> user-rpc\n', Format=True, PDF=pdf_log)
            # STARTUP.STORE_DATA('******* Replace with below xml ********', Format=True, PDF=pdf_log)
            # STARTUP.STORE_DATA(xml_data2, Format='XML', PDF=pdf_log)
            # d3 = self.session.dispatch(to_ele(xml_data2))

            # ###############################################################################
            # ## Test Procedure 2 : O-RU NETCONF Server responds with <software-activate>
            # ###############################################################################
            # Test_Step2 = '\t\tStep 2 : O-RU NETCONF Server responds with <rpc-reply><software-activate><status>. The parameter "status" is set to STARTED.'
            # STARTUP.STORE_DATA('{}'.format(Test_Step2),Format='TEST_STEP', PDF=pdf_log)
            # STARTUP.STORE_DATA('{}'.format(d3), Format='XML', PDF=pdf_log)

            # ###############################################################################
            # ## Capture_The_Notifications
            # ###############################################################################
            # while True:
            #     n = self.session.take_notification(timeout=60)
            #     if n == None:
            #         break
            #     notify = n.notification_xml
            #     dict_n = xmltodict.parse(str(notify))
            #     try:
            #         notf = dict_n['notification']['activation-event']
            #         if notf:
            #             Test_Step3 = '\t\tStep 3 : O-RU NETCONF Server sends <notification><activation-event> with a status COMPLETED.'
            #             STARTUP.STORE_DATA('{}'.format(
            #                 Test_Step3), Format='TEST_STEP', PDF=pdf_log)
            #             x = xml.dom.minidom.parseString(notify)
            #             xml_pretty_str = x.toprettyxml()
            #             STARTUP.STORE_DATA(
            #                 xml_pretty_str, Format='XML', PDF=pdf_log)
            #             status = dict_n['notification']['activation-event']['status']
            #             if status != 'COMPLETED':
            #                 return status
            #             break
            #     except:
            #         pass

            # ###############################################################################
            # ## POST_GET_FILTER
            # ###############################################################################
            # time.sleep(5)
            # pdf_log.add_page()
            # STARTUP.STORE_DATA(
            #     '\n> get --filter-xpath /o-ran-software-management:software-inventory', Format=True, PDF=pdf_log)
            # sw_inv = '''<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            #             <software-inventory xmlns="urn:o-ran:software-management:1.0">
            #             </software-inventory>
            #             </filter>'''
            # slot_names1 = self.session.get(sw_inv).data_xml
            # s = xml.dom.minidom.parseString(slot_names1)
            # xml_pretty_str = s.toprettyxml()
            # self.slots.pop(slot_name)
            # slot_n1 = xmltodict.parse(str(slot_names1))
            # SLOTS1 = slot_n1['data']['software-inventory']['software-slot']
            # for slot in SLOTS1:
            #     if slot['status'] == 'INVALID':
            #         STARTUP.STORE_DATA(
            #             xml_pretty_str, Format='XML', PDF=pdf_log)
            #         return f'SW slot status is Invid for {slot["name"]}...'
            #     if slot['name'] == slot_name:
            #         if (slot['active'] == 'true') and slot['running'] == 'false':
            #             pass
            #         else:
            #             STARTUP.STORE_DATA(
            #                 xml_pretty_str, Format='XML', PDF=pdf_log)
            #             return f"SW Inventory didn't update for {slot_name}..."

            #     if slot['name'] == DEACTIVE_SLOT[0]:
            #         if (slot['active'] != 'false') and slot['running'] != 'true':
            #             STARTUP.STORE_DATA(
            #                 xml_pretty_str, Format='XML', PDF=pdf_log)
            #             return f"SW Inventory didn't update for {slot['name'] }..."
            # STARTUP.STORE_DATA(xml_pretty_str, Format='XML', PDF=pdf_log)



            ###############################################################################
            ## Test Procedure 3 : Configure_Reset_RPC_in_RU
            ###############################################################################
            Test_Step1 = '\t\tStep 3 : TER NETCONF Client sends <rpc><reset></rpc> to the O-RU NETCONF Server..'
            STARTUP.STORE_DATA('{}'.format(Test_Step1),Format='TEST_STEP', PDF=pdf_log)
            STARTUP.STORE_DATA('\n> user-rpc\n',Format=True, PDF=pdf_log)
            STARTUP.STORE_DATA('******* Replace with below xml ********',Format=True, PDF=pdf_log)
            xml_data3 = '''<reset xmlns="urn:o-ran:operations:1.0"></reset>'''
            STARTUP.STORE_DATA(xml_data3,Format='XML', PDF=pdf_log)
            d3 = self.session.dispatch(to_ele(xml_data3))

            ###############################################################################
            ## Test Procedure 4 : Get RPC Reply
            ###############################################################################
            Test_Step2 = '\t\tStep 4 : O-RU NETCONF Server responds with rpc-reply.'
            STARTUP.STORE_DATA('{}'.format(Test_Step2),Format='TEST_STEP', PDF=pdf_log)
            STARTUP.STORE_DATA('{}'.format(d3),Format='XML', PDF=pdf_log)
            self.start_time = time.time()
            return True
                

            
            

        ###############################################################################
        ## Corresponding error tag will come
        ###############################################################################                
        except RPCError as e:
            STARTUP.STORE_DATA("###########  Rpc Reply ####################",Format=True,PDF=pdf_log)
            STARTUP.STORE_DATA('ERROR',Format=False,PDF=pdf_log)
            STARTUP.STORE_DATA(f"\t{'type' : <20}{':' : ^10}{e.type: ^10}\n",Format=False,PDF=pdf_log)
            STARTUP.STORE_DATA(f"\t{'tag' : <20}{':' : ^10}{e.tag: ^10}\n",Format=False,PDF=pdf_log)
            STARTUP.STORE_DATA(f"\t{'severity' : <20}{':' : ^10}{e.severity: ^10}\n",Format=False,PDF=pdf_log)
            STARTUP.STORE_DATA(f"\t{'path' : <20}{':' : ^10}{e.path: ^10}\n",Format=False,PDF=pdf_log)
            STARTUP.STORE_DATA(f"\t{'message' : <20}{':' : ^10}{e.message: ^10}\n",Format=False,PDF=pdf_log)
            return [e.type, e.tag, e.severity, e.path, e.message]

        except Exception as e:
            STARTUP.STORE_DATA(e, Format=True,PDF=pdf_log)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf_log)
            return e

        finally:
            try:
                self.session.close_session()
            except Exception as e:
                print(e)
           
    def system_logs(self,hostname):
        t = time.time()+30
        while t>time.time():
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
                # print(lines, 'hey how are you')
                return lines
            except Exception as e:
                print(e)
        else:
            print('Can\'t connect to RU..')


    def test_main(self):
        try:
            del self.slots['swRecoverySlot']
            
            for key, val in self.slots.items():
                if val[0] == 'true' and val[1] == 'true':
                    ############################### Test Description #############################
                    Test_Desc = '''Test Description : 1. Downgrade the software using NETCONF software-activate rpc is used to activate the software.
'''
                    CONFIDENTIAL = STARTUP.ADD_CONFIDENTIAL(filename,SW_R = val[2]) 
                    STARTUP.STORE_DATA(CONFIDENTIAL,Format='CONF',PDF= pdf_log)
                    STARTUP.STORE_DATA(Test_Desc,Format='DESC',PDF= pdf_log)
                    pdf_log.add_page()
                    pass


            
            
            time.sleep(5)
            result = self.sw_activate_with_reset()
            print('first step is completed : {}'.format(result))
            log1 = self.system_logs(self.hostname)
            

            if result != True:
                STARTUP.STORE_DATA('\t\t\t\t############ SYSTEM LOGS ##############',Format=True,PDF=pdf_log)
                STARTUP.STORE_DATA("{}".format(i),Format=False,PDF=pdf_log)
                Exp_Result = '''Expected Result : 1.verify system is up with downgraded image and check the time taken.
    '''
                STARTUP.STORE_DATA(Exp_Result,Format='DESC',PDF= pdf_log)
                STARTUP.STORE_DATA('\t\t{}'.format('****************** Actual Result ******************'),Format=True,PDF= pdf_log)
                if type(result) == list:
                    STARTUP.STORE_DATA(f"ERROR",Format=True,PDF= pdf_log)
                    STARTUP.STORE_DATA(f"{'error-type' : <20}{':' : ^10}{result[0]: ^10}",Format=False,PDF=pdf_log)
                    STARTUP.STORE_DATA(f"{'error-tag' : <20}{':' : ^10}{result[1]: ^10}",Format=False,PDF=pdf_log)
                    STARTUP.STORE_DATA(f"{'error-severity' : <20}{':' : ^10}{result[2]: ^10}",Format=False,PDF=pdf_log)
                    STARTUP.STORE_DATA(f"{'error-path' : <20}{':' : ^10}{result[3]: ^10}",Format=False,PDF=pdf_log)
                    STARTUP.STORE_DATA(f"{'Description' : <20}{':' : ^10}{result[4]: ^10}",Format=False,PDF=pdf_log)
                else:
                    STARTUP.STORE_DATA(f"{'Fail-Reason' : <15}{'=' : ^20}{result : ^20}",Format=False,PDF=pdf_log)
                STARTUP.ACT_RES(f"{'Software downgrade time taken' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf_log,COL=(255,0,0))
                return result
                
            else:
                time.sleep(40)
                check = self.get_config_detail()
                log2 = self.system_logs(self.hostname1)
                STARTUP.STORE_DATA('\t\t\t\t############ SYSTEM LOGS ##############',Format=True,PDF=pdf_log)
                for i in log1:
                    STARTUP.STORE_DATA("{}".format(i),Format=False,PDF=pdf_log)
                for i in log2:
                    STARTUP.STORE_DATA("{}".format(i),Format=False,PDF=pdf_log)

                Exp_Result = '''Expected Result : 1.verify system is up with downgraded image and check the time taken.
    '''
                STARTUP.STORE_DATA(Exp_Result,Format='DESC',PDF= pdf_log)
                STARTUP.STORE_DATA('\t\t{}'.format('****************** Actual Result ******************'),Format=True,PDF= pdf_log)
                

                if check == True:
                    STARTUP.ACT_RES(f"{'Software downgrade time taken' : <50}{'=' : ^20}{'PASS' : ^20}",PDF= pdf_log,COL=(105, 224, 113))
                    return True  
                
                else:
                    if type(check) == list:
                        STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf_log)
                        Error_Info = '''ERROR\n\terror-type \t: \t{}\n\terror-tag \t: \t{}\n\terror-severity \t: \t{}\n\tmessage' \t: \t{}'''.format(*map(str,check))
                        STARTUP.STORE_DATA(Error_Info,Format=False,PDF= pdf_log)
                        STARTUP.ACT_RES(f"{'Supplemental Reset after Software Activation' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf_log,COL=(255,0,0))
                        return False

                    else:
                        STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf_log)
                        STARTUP.STORE_DATA('{}'.format(check),Format=False,PDF= pdf_log)
                        STARTUP.ACT_RES(f"{'Supplemental Reset after Software Activation' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf_log,COL=(255,0,0))
                        return False


        ############################### Known Exceptions ####################################################
        except socket.timeout as e:
            Error = '{} : Call Home is not initiated, SSH Socket connection lost....'.format(
                e)
            STARTUP.STORE_DATA(Error, Format=True,PDF=pdf_log)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf_log)
            return Error
            # raise socket.timeout('{}: SSH Socket connection lost....'.format(e)) from None

        except Exception as e:
            STARTUP.STORE_DATA('{}'.format(e), Format=True,PDF=pdf_log)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf_log)
            return '{}'.format(e)
            # raise Exception('{}'.format(e)) from None

        finally:
            end_time = time.time()
            Excution_time = end_time - self.start_time
            STARTUP.STORE_DATA('Excution_time : {}'.format(Excution_time), Format=True,PDF=pdf_log)
            STARTUP.CREATE_LOGS('M_FTC_ID_{}'.format(filename),PDF=pdf_log)

    
                
                
    
if __name__ == '__main__':
    try:
        obj = software_downgrade()
        filename = sys.argv[1]
        Result = obj.test_main()
    except Exception as e:
        STARTUP.STORE_DATA('{}'.format(e), Format = True,PDF=pdf_log)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(
            f"Error occured in line number {exc_tb.tb_lineno}", Format = False,PDF=pdf_log)
        print('Usage: python software_downgrade.py <Test_Case_ID>')
    
    