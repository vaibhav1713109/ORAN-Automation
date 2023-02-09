###############################################################################
##@ FILE NAME:      Retrival of RU state
##@ TEST SCOPE:     M PLANE O-RAN Functional
##@ Version:        V_1.0.0
##@ Support:        @Ramiyer, @VaibhavDhiman, @PriyaSharma
###############################################################################

###############################################################################
## Package Imports 
###############################################################################

import sys, os, time, xmltodict, xml.dom.minidom, lxml.etree, ifcfg
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

class retrival_RU_state(vlan_Creation):

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

    ############### POWER-ON ################
    def Power_On(self):
        Description = '''enum POWER-ON {
            description
              "Equipment restarted because it was powered on";
          }'''

        STARTUP.STORE_DATA(Description,Format=True,PDF=pdf_log)
        try:
            STARTUP.STORE_DATA("get --filter-xpath /o-ran-operations:operational-info",Format=True,PDF=pdf_log)
            u_name = '''
                    <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                    <operational-info xmlns="urn:o-ran:operations:1.0">
                    </operational-info>
                    </filter>
            '''
            
            user_name = self.session.get(u_name).data_xml
            x = xml.dom.minidom.parseString(user_name)
            xml_pretty_str = x.toprettyxml()

            STARTUP.STORE_DATA(xml_pretty_str,Format='XML',PDF=pdf_log)
            return True

        except RPCError as e:
            return [e.type, e.tag, e.severity, e,e.message]

        except Exception as e:
            STARTUP.STORE_DATA('{} POWER_ON'.format(e), Format=True,PDF=pdf_log)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf_log)
            return '{}'.format(e)


    ############### MPLANE-TRIGGERED-RESTART ################
    def M_Plane_Triggered(self):
        try:
            Description = '''enum MPLANE-TRIGGERED-RESTART {
                description
                "Equipment restarted because of an M-plane issued  rpc";
            }'''

            STARTUP.STORE_DATA(Description,Format=True,PDF=pdf_log)
            STARTUP.STORE_DATA(' TER NETCONF Client sends <rpc><reset></rpc> to the O-RU NETCONF Server..',Format='TEST_STEP',PDF=pdf_log)
            STARTUP.STORE_DATA('> user-rpc',Format=True,PDF=pdf_log)
            STARTUP.STORE_DATA('******* Replace with below xml ********',Format=True,PDF=pdf_log)
            RPC_Data = '''<reset xmlns="urn:o-ran:operations:1.0"></reset>'''
            STARTUP.STORE_DATA(RPC_Data,Format=False,PDF=pdf_log)
            RPC_Reply = self.session.dispatch(to_ele(RPC_Data))
            STARTUP.STORE_DATA(' O-RU NETCONF Server responds with rpc-reply.',Format=True,PDF=pdf_log)
            STARTUP.STORE_DATA('{}'.format(RPC_Reply),Format=False,PDF=pdf_log)


            ############## Wait for 30 Sec ##############
            t = time.time()+40

            while time.time()<t:
                STARTUP.STORE_DATA("get --filter-xpath /o-ran-operations:operational-info",Format=True,PDF=pdf_log)
                u_name = '''
                        <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                        <operational-info xmlns="urn:o-ran:operations:1.0">
                        </operational-info>
                        </filter>
                '''
                
                user_name = self.session.get(u_name).data_xml
                x = xml.dom.minidom.parseString(user_name)
                xml_pretty_str = x.toprettyxml()
                restart_couses = xmltodict.parse(user_name)
                restart_cause = restart_couses['data']['operational-info']['operational-state']['restart-cause']
                if restart_cause == 'MPLANE-TRIGGERED-RESTART':
                    STARTUP.STORE_DATA(xml_pretty_str,Format='XML',PDF=pdf_log)
                    return True

        except RPCError as e:
            return [e.type, e.tag, e.severity, e,e.message]

        except Exception as e:
            STARTUP.STORE_DATA('{} M_Plane_Triggered'.format(e), Format=True,PDF=pdf_log)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf_log)
            return '{}'.format(e)
        

    ############### SUPERVISION-WATCHDOG ################
    def supervision_watchdog(self):
        try:
            Description = '''enum SUPERVISION-WATCHDOG {
                description
                "Equipment restarted because it's supervision wathcdog timer wasn't reset
                by a NETCONF client (inferring loss of NETCONF connectivity)";
            }'''

            STARTUP.STORE_DATA(Description,Format=True,PDF=pdf_log)
            Test_Step1 = '\t\t TER NETCONF Client responds with <rpc supervision-watchdog-reset></rpc> to the O-RU NETCONF Server'
            xml_data = '''<supervision-watchdog-reset xmlns="urn:o-ran:supervision:1.0">
                <supervision-notification-interval>10</supervision-notification-interval>
                <guard-timer-overhead>5</guard-timer-overhead>
                </supervision-watchdog-reset>'''
            STARTUP.STORE_DATA('{}'.format(Test_Step1),Format='TEST_STEP', PDF=pdf_log)
            STARTUP.STORE_DATA('> user-rpc',Format=True, PDF=pdf_log)
            STARTUP.STORE_DATA('******* Replace with below xml ********',Format=True, PDF=pdf_log)
            STARTUP.STORE_DATA(xml_data,Format='XML', PDF=pdf_log)

            # try:
            d = self.session.dispatch(to_ele(xml_data))
            Test_Step2 = '\t\t O-RU NETCONF Server sends a reply to the TER NETCONF Client <rpc-reply><next-update-at>date-time</next-update-at></rpc-reply>'
            STARTUP.STORE_DATA('{}'.format(Test_Step2),Format='TEST_STEP', PDF=pdf_log)
            STARTUP.STORE_DATA('{}'.format(d),Format='XML', PDF=pdf_log)
            ############## Wait for 30 Sec ##############
            t = time.time()+20

            while time.time()<t:
                STARTUP.STORE_DATA("get --filter-xpath /o-ran-operations:operational-info",Format=True,PDF=pdf_log)
                u_name = '''
                        <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                        <operational-info xmlns="urn:o-ran:operations:1.0">
                        </operational-info>
                        </filter>
                '''
                
                user_name = self.session.get(u_name).data_xml
                x = xml.dom.minidom.parseString(user_name)
                xml_pretty_str = x.toprettyxml()
                restart_couses = xmltodict.parse(user_name)
                restart_cause = restart_couses['data']['operational-info']['operational-state']['restart-cause']
                if restart_cause == 'SUPERVISION-WATCHDOG':
                    STARTUP.STORE_DATA(xml_pretty_str,Format='XML',PDF=pdf_log)
                    return True

        except RPCError as e:
            return [e.type, e.tag, e.severity, e,e.message]

        except Exception as e:
            STARTUP.STORE_DATA('{} Supervision_Watchdog'.format(e), Format=True,PDF=pdf_log)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf_log)
            return '{}'.format(e)


    def session_login(self):
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
            ## Test step 2 Retrival of RU Operational-state
            ###############################################################################
            pdf_log.add_page()
            STARTUP.STORE_DATA('*********** Retrival of RU Operational-state **********',Format=True,PDF=pdf_log)
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
           


    def test_main(self):
        try:
            del self.slots['swRecoverySlot']
            
            for key, val in self.slots.items():
                if val[0] == 'true' and val[1] == 'true':
                    ############################### Test Description #############################
                    Test_Desc = '''Test Description : 1. Open the rpc web based/cli on O-DU/NMS.
2. Send the rpc <get--filter><source><running/><operational-state/> from O-DU/NMS cli.
3. Open the system log in O-DU/NMS to check the state of O-RU.'''
                    CONFIDENTIAL = STARTUP.ADD_CONFIDENTIAL(filename,SW_R = val[2]) 
                    STARTUP.STORE_DATA(CONFIDENTIAL,Format='CONF',PDF= pdf_log)
                    STARTUP.STORE_DATA(Test_Desc,Format='DESC',PDF= pdf_log)
                    pdf_log.add_page()
                    pass


            
            
            time.sleep(5)
            result = self.session_login()

            STARTUP.GET_SYSTEM_LOGS(self.hostname,self.USER_N,self.PSWRD,pdf_log,number=500)
                         
            Exp_Result = '''Expected Result : 1. RPC web based window or cli successfully launched.
2. Verify the O-DU/NMS receive the <rpc-reply> with data with below O-RU state in system log/web based GUI.
a. ro restart-cause? enumeration 
b. ro restart-datetime? yang:date-and-time. 
'''
            STARTUP.STORE_DATA(Exp_Result,Format='DESC',PDF= pdf_log)
            STARTUP.STORE_DATA('\t\t{}'.format('****************** Actual Result ******************'),Format=True,PDF= pdf_log)

            if result:
                if type(result) == list:
                    STARTUP.STORE_DATA(f"ERROR",Format=True,PDF= pdf_log)
                    STARTUP.STORE_DATA(f"{'error-type' : <20}{':' : ^10}{result[0]: ^10}",Format=False,PDF=pdf_log)
                    STARTUP.STORE_DATA(f"{'error-tag' : <20}{':' : ^10}{result[1]: ^10}",Format=False,PDF=pdf_log)
                    STARTUP.STORE_DATA(f"{'error-severity' : <20}{':' : ^10}{result[2]: ^10}",Format=False,PDF=pdf_log)
                    STARTUP.STORE_DATA(f"{'error-path' : <20}{':' : ^10}{result[3]: ^10}",Format=False,PDF=pdf_log)
                    STARTUP.STORE_DATA(f"{'Description' : <20}{':' : ^10}{result[4]: ^10}",Format=False,PDF=pdf_log)
                else:
                    STARTUP.STORE_DATA(f"{'Fail-Reason' : <15}{'=' : ^20}{result : ^20}",Format=False,PDF=pdf_log)
                STARTUP.ACT_RES(f"{'Retrival of RU state' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf_log,COL=(255,0,0))
                return result
                
            else:
                STARTUP.ACT_RES(f"{'Retrival of RU state' : <50}{'=' : ^20}{'PASS' : ^20}",PDF= pdf_log,COL=(105, 224, 113))
                return True    

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


        ############################### MAKE PDF File ####################################################
        finally:
            STARTUP.CREATE_LOGS('M_FTC_ID_{}'.format(filename),PDF=pdf_log)
            try:
                self.session.close_session()
            except Exception as e:
                print(e)

                
                
    
if __name__ == '__main__':
    try:
        obj = retrival_RU_state()
        filename = sys.argv[1]
        Result = obj.test_main()
    except Exception as e:
        STARTUP.STORE_DATA('{}'.format(e), Format = True,PDF=pdf_log)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(
            f"Error occured in line number {exc_tb.tb_lineno}", Format = False,PDF=pdf_log)
        print('Usage: python retrival_RU_state.py <Test_Case_ID>')
