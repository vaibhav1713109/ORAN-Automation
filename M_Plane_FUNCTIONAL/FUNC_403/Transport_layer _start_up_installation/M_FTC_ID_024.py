import sys
from ncclient import manager
from ncclient.xml_ import to_ele
from lxml import etree
from ncclient.operations.rpc import RPCError
import xml.dom.minidom, xmltodict
from ncclient.transport import errors
import time, socket
from paramiko.ssh_exception import NoValidConnectionsError
from ncclient.operations.errors import TimeoutExpiredError
from ncclient.transport.errors import SessionCloseError
import STARTUP,Config


pdf_log = STARTUP.PDF_CAP()

class RetrivalOf_RU_State():

    def __init__(self) -> None:
        try:
            self.port = 830
            self.USER_N = Config.details['SUDO_USER']
            self.PSWRD = Config.details['SUDO_PASS']
            self.du_password = Config.details['DU_PASS']
            self.session = manager.call_home(host = '', port=4334, hostkey_verify=False,username = self.USER_N, password = self.PSWRD ,allow_agent = False , look_for_keys = False)
            li = self.session._session._transport.sock.getpeername()
            sid = self.session.session_id
            self.host = li[0]
            data = STARTUP.demo(self.session)
            self.users, self.slots, self.macs = data[0], data[1], data[2]
            
        except Exception as e:
            STARTUP.STORE_DATA('{}'.format(e), Format = True,PDF=pdf_log)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format = False,PDF=pdf_log)
            return '{}'.format(e)
        pass


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


    ################################ Get 4 operational state [Power-on, mplane-triggered, supervision-watchdog, other watchdog trigger]
    def session_login(self,*args):
        try:
            STARTUP.STORE_DATA('********** Connect to the NETCONF Server ***********',Format='TEST_STEP',PDF=pdf_log)
            STATUS = STARTUP.STATUS(self.host,self.USER_N,self.session.session_id,self.port)
            STARTUP.STORE_DATA(STATUS,Format=False,PDF=pdf_log)

            for i in self.session.server_capabilities:
                STARTUP.STORE_DATA('{}'.format(i),Format=False,PDF=pdf_log)


            ################ Create Subscription ###############                   
            cap = self.session.create_subscription()
            STARTUP.STORE_DATA('********** Create Subscription ***********',Format=True,PDF=pdf_log)
            STARTUP.STORE_DATA('>subscribe',Format=True,PDF=pdf_log)
            dict_data = xmltodict.parse(str(cap))
            if dict_data['nc:rpc-reply']['nc:ok']== None:
                STARTUP.STORE_DATA('\nOk\n',Format=False,PDF=pdf_log)


            pdf_log.add_page()
            STARTUP.STORE_DATA('*********** Retrival of RU Operational-state **********',Format=True,PDF=pdf_log)

            return [args[0],args[1],args[2]]


        except Exception as e:
            STARTUP.STORE_DATA('{} session_login'.format(e), Format=True,PDF=pdf_log)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf_log)
            return '{}'.format(e)

    def Retrival_of_RU_State(self,Test_Case_ID):
        try:

            del self.slots['swRecoverySlot']
            
            for key, val in self.slots.items():
                if val[0] == 'true' and val[1] == 'true':
                    ############################### Test Description #############################
                    Test_Desc = '''Test Description : Verify the O-RU connection state and the synchronisation information from O-RU.'''
                    CONFIDENTIAL = STARTUP.ADD_CONFIDENTIAL(Test_Case_ID,SW_R = val[2]) 
                    STARTUP.STORE_DATA(CONFIDENTIAL,Format='CONF',PDF= pdf_log)
                    STARTUP.STORE_DATA(Test_Desc,Format='DESC',PDF= pdf_log)
                    pdf_log.add_page()

            time.sleep(5)
            result = self.session_login()


            STARTUP.GET_SYSTEM_LOGS(self.host,self.USER_N,self.PSWRD,pdf_log)
                    
            Exp_Result = '''Expected Result : 1. RPC web based window or cli successfully launched.
2. Verify the O-DU/NMS receive the <rpc-reply> with data with below O-RU state in system log/web based GUI.
a. ro restart-cause? enumeration 
b. ro restart-datetime? yang:date-and-time'''
            STARTUP.STORE_DATA(Exp_Result,Format='DESC',PDF= pdf_log)

            STARTUP.STORE_DATA('\t\t{}'.format('****************** Actual Result ******************'),Format=True,PDF= pdf_log)

            if result:                
                time.sleep(5)
                if type(result) == list:
                    STARTUP.STORE_DATA(f"ERROR",Format=True,PDF= pdf_log)
                    STARTUP.STORE_DATA(f"{'error-type' : <20}{':' : ^10}{result[0]: ^10}",Format=False,PDF=pdf_log)
                    STARTUP.STORE_DATA(f"{'error-tag' : <20}{':' : ^10}{result[1]: ^10}",Format=False,PDF=pdf_log)
                    STARTUP.STORE_DATA(f"{'error-severity' : <20}{':' : ^10}{result[2]: ^10}",Format=False,PDF=pdf_log)
                    #print(f"{'error-info' : <20}{':' : ^10}{res[3]: ^10}")
                    STARTUP.STORE_DATA(f"{'Description' : <20}{':' : ^10}{result[4]: ^10}",Format=False,PDF=pdf_log)
                    return result[5]
                else:
                    STARTUP.STORE_DATA(f"{'Retrival_Of_RU_state' : <15}{'=' : ^20}{result : ^20}",Format=False,PDF=pdf_log)
                STARTUP.ACT_RES(f"{'Retrival_Of_RU_state' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf_log,COL=(255,0,0))
                return result
                
            else:
                time.sleep(5)
                STARTUP.ACT_RES(f"{'Retrival_Of_RU_state' : <50}{'=' : ^20}{'PASS' : ^20}",PDF= pdf_log,COL=(105, 224, 113))
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

        except errors.SSHError as e:
            Error = '{} : SSH Socket connection lost....'.format(e)
            STARTUP.STORE_DATA(Error, Format=True,PDF=pdf_log)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf_log)
            return Error
            # raise errors.SSHError('{}: SSH Socket connection lost....'.format(e)) from None

        except errors.AuthenticationError as e:
            Error = "{} : Invalid username/password........".format(e)
            STARTUP.STORE_DATA(Error, Format=True,PDF=pdf_log)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf_log)
            return Error
            # raise f'{e} : Invalid username/password........'

        except NoValidConnectionsError as e:
            Error = '{} : ...'.format(e)
            STARTUP.STORE_DATA(Error, Format=True,PDF=pdf_log)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf_log)
            return Error
            # raise e

        except TimeoutError as e:
            Error = '{} : Call Home is not initiated, Timout Expired....'.format(e)
            STARTUP.STORE_DATA(Error, Format=True,PDF=pdf_log)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf_log)
            return Error
            # raise f'{e} : Call Home is not initiated, Timout Expired....'

        except SessionCloseError as e:
            Error = "{} : Unexpected_Session_Closed....".format(e)
            STARTUP.STORE_DATA(Error, Format=True,PDF=pdf_log)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf_log)
            return Error
            # raise f'{e},Unexpected_Session_Closed....'

        except TimeoutExpiredError as e:
            Error = "{} : TimeoutExpiredError....".format(e)
            STARTUP.STORE_DATA(Error, Format=True,PDF=pdf_log)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf_log)
            return Error
            # raise e

        except OSError as e:
            Error = '{} : Call Home is not initiated, Please wait for sometime........'.format(
                e)
            STARTUP.STORE_DATA(Error, Format=True,PDF=pdf_log)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf_log)
            return Error
            # raise Exception('{} : Please wait for sometime........'.format(e)) from None

        except Exception as e:
            STARTUP.STORE_DATA('{}'.format(e), Format=True,PDF=pdf_log)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf_log)
            return e
            # raise Exception('{}'.format(e)) from None


        ############################### MAKE PDF File ####################################################
        finally:
            STARTUP.CREATE_LOGS('M_CTC_ID_024',PDF=pdf_log)

                
                
    
if __name__ == '__main__':
    try:
        ############### Power On and M Plane Triggered ###############
        obj = RetrivalOf_RU_State()
        filename = sys.argv[0].split('.')
        Power_On = obj.Power_On()
        M_Plane_Tr = obj.M_Plane_Triggered()
        time.sleep(100)
        ############### Supervision Watchdog ###############
        obj = RetrivalOf_RU_State()
        Svision_Wd = obj.supervision_watchdog()
        time.sleep(100)
        ############### Result Declaration ###############
        obj1 = RetrivalOf_RU_State()
        obj1.session_login(Power_On,M_Plane_Tr,Svision_Wd)


    except Exception as e:
        STARTUP.STORE_DATA('{}'.format(e), Format = True,PDF=pdf_log)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(
            f"Error occured in line number {exc_tb.tb_lineno}", Format = False,PDF=pdf_log)
        print('Usage: python Too_Big.py <Test_Case_ID>')