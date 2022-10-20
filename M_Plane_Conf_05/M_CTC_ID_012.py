import socket
import sys, os, warnings
from time import time
#warnings.simplefilter("ignore", DeprecationWarning)
from ncclient import manager
import string
from ncclient.operations.rpc import RPCError
from ncclient.transport.errors import SSHError
import xmltodict
import paramiko
import xml.dom.minidom  
from ncclient.transport import errors
import STARTUP
from calnexRest import calnexInit, calnexGet, calnexSet, calnexCreate, calnexDel,calnexGetVal
from paramiko.ssh_exception import NoValidConnectionsError
from ncclient.operations.errors import TimeoutExpiredError
from ncclient.transport.errors import SessionCloseError
import lxml.etree
import Config

pdf = STARTUP.PDF_CAP()


#xml_1 = open('o-ran-interfaces.xml').read()
def session_login(host, port, user, password):
    
    with manager.connect(host=host, port=port, username=user, hostkey_verify=False, password=password, allow_agent = False , look_for_keys = False) as m:
        try:
            
            STARTUP.STORE_DATA('\t\t********** Connect to the NETCONF Server ***********',Format='TEST_STEP',PDF=pdf)
            STATUS = STARTUP.STATUS(host,user,m.session_id,port)
            STARTUP.STORE_DATA(STATUS,Format=False,PDF=pdf)

            ########################### Server Capabilities ############################
            for i in m.server_capabilities:
                STARTUP.STORE_DATA("\t{}".format(i),Format=False,PDF=pdf)


            ########################### Create_subscription ############################
            cap = m.create_subscription()
            STARTUP.STORE_DATA('>subscribe', Format=True,PDF=pdf)
            dict_data = xmltodict.parse(str(cap))
            if dict_data['nc:rpc-reply']['nc:ok'] == None:
                STARTUP.STORE_DATA('\nOk\n', Format=False,PDF=pdf)

            pdf.add_page()
            ########################### Initial Get ############################
            STARTUP.STORE_DATA("\t\t########### Initial Get#####################",Format='TEST_STEP',PDF=pdf)
            STARTUP.STORE_DATA('\n>get --filter-xpath /o-ran-sync:sync',Format=True,PDF=pdf)
            SYNC = '''<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <sync xmlns="urn:o-ran:sync:1.0">
                </sync>
                </filter>
                '''
            data  = m.get(SYNC).data_xml
            dict_Sync = xmltodict.parse(str(data))
            x = xml.dom.minidom.parseString(data)
            xml_pretty_str = x.toprettyxml()
            STARTUP.STORE_DATA(xml_pretty_str,Format='XML',PDF=pdf)

            pdf.add_page()
            ########################### Get Unitl LOCKED State Reached ############################
            Test_Step1 = 'Step 1 The TER NETCONF Client periodically tests O-RU\'s sync-status until the LOCKED state is reached.'
            STARTUP.STORE_DATA("\t\t{}".format(Test_Step1),Format='TEST_STEP',PDF=pdf)
            STARTUP.STORE_DATA('\n>get --filter-xpath /o-ran-sync:sync',Format=True,PDF=pdf)
            start_time = time() + 1200
            while time() < start_time:
                SYNC = '''<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <sync xmlns="urn:o-ran:sync:1.0">
                </sync>
                </filter>
                '''
                data  = m.get(SYNC).data_xml
                dict_Sync = xmltodict.parse(str(data))
                state = dict_Sync['data']['sync']['sync-status']['sync-state']
                if state == 'LOCKED':

                    x = xml.dom.minidom.parseString(data)
                    

                    xml_pretty_str = x.toprettyxml()

                    STARTUP.STORE_DATA(xml_pretty_str,Format='XML',PDF=pdf)
                    break

            ########################### Turn Off the PTP & SYNCE ############################
            calnexSet(f"app/mse/master/Master{Config.details['PORT']}/stop")
            calnexSet(f"app/generation/synce/esmc/Port{Config.details['PORT']}/stop")


            ########################### Check The Alarm No 17 ############################
            pdf.add_page()
            STARTUP.STORE_DATA('######## NOTIFICATIONS ########',Format=True,PDF=pdf)
            while True:
                n = m.take_notification(timeout=30)
                if n == None:
                    return 1
                notify=n.notification_xml
                dict_n = xmltodict.parse(str(notify))
                try:
                    notf = dict_n['notification']['alarm-notif']['fault-id']
                    type(notf)
                    if notf == '17':
                        Test_Step2 = '\t\tStep 3 After a while (time depends on implementation) the O-RU NETCONF SERVER sends a notification for  alarm 17: No external sync source.'
                        STARTUP.STORE_DATA("{}".format(Test_Step2),Format='TEST_STEP',PDF=pdf)
                        x = xml.dom.minidom.parseString(notify)
                        xml_pretty_str = x.toprettyxml()
                        STARTUP.STORE_DATA(xml_pretty_str,Format='XML',PDF=pdf)
                        break
                    else:
                        x = xml.dom.minidom.parseString(notify)
                        #xml = xml.dom.minidom.parseString(user_name)

                        xml_pretty_str = x.toprettyxml()
                        # STARTUP.STORE_DATA(xml_pretty_str,Format='XML',PDF=pdf)
                        pass
                except:
                    pass
            


        ########################### Known Exceptions ############################
        except RPCError as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            return [e.type, e.tag, e.severity, e.message, exc_tb.tb_lineno]

        except FileNotFoundError as e:
            STARTUP.STORE_DATA("{0} FileNotFoundError {0}".format("*"*30), Format=True,PDF=pdf)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA("\t\tError : {}".format(e), Format=False,PDF=pdf)
            return f'No such file or directory : {e.filename}\nError occured in line number {exc_tb.tb_lineno}'

        except lxml.etree.XMLSyntaxError as e:
            STARTUP.STORE_DATA("{0} XMLSyntaxError {}".format("*"*30), Format=True,PDF=pdf)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA("\t\tError : {}".format(e), Format=False,PDF=pdf)
            return f"{e} \nError occured in line number {exc_tb.tb_lineno}"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA("\t\tError : {}".format(e), Format=False,PDF=pdf)
            return f"{e} \nError occured in line number {exc_tb.tb_lineno}"
    


########################### Main Function ############################
def test_MAIN_FUNC_012():
    
    
    try:
        USER_N = Config.details['SUDO_USER']
        PSWRD = Config.details['SUDO_PASS']
        P_NEO_IP = Config.details['IPADDR_PARAGON']
        P_NEO_PORT = Config.details['PORT']
        sys.path.append(f'//{P_NEO_IP}/calnex100g/RemoteControl/')
        calnexInit(f"{P_NEO_IP}")

        ############################### Perform Call Home to get IP #######################################
        m = manager.call_home(host = '', port=4334, hostkey_verify=False,username = USER_N, password = PSWRD, allow_agent = False , look_for_keys = False)
        li = m._session._transport.sock.getpeername()   #['ip_address', 'TCP_Port']
        sid = m.session_id
        if m:
            STARTUP.kill_ssn(li[0],830, USER_N, PSWRD,sid)
            RU_DETAILS = STARTUP.demo(li[0], 830, USER_N, PSWRD)

            ############################### Enable PTP & SYNCE #######################################
            calnexSet(f"app/mse/master/Master{P_NEO_PORT}/start")
            calnexSet(f"app/generation/synce/esmc/Port{P_NEO_PORT}/start")

            for key, val in RU_DETAILS[1].items():
                    if val[1] == 'true':
                        ############################### Test Description #############################
                        Test_Desc = 'Test Description : The minimum functions of the TER described in section 2.1 that support validation of the M-Plane are operational, configured and connected to the O-RU.'
                        CONFIDENTIAL = STARTUP.ADD_CONFIDENTIAL('12',SW_R = val[2]) 
                        STARTUP.STORE_DATA(CONFIDENTIAL,Format='CONF',PDF= pdf)
                        STARTUP.STORE_DATA(Test_Desc,Format='DESC',PDF= pdf)
                        pdf.add_page()

            
            
            res = session_login(li[0],830,USER_N, PSWRD)


            ############################### Expected/Actual Result ####################################################
            STARTUP.GET_SYSTEM_LOGS(li[0],USER_N,PSWRD,pdf)
            Exp_Result = 'Expected Result : After a while (time depends on implementation) the O-RU NETCONF SERVER sends a notification for alarm 17: No external sync source.'
            STARTUP.STORE_DATA(Exp_Result,Format='DESC',PDF= pdf)

            STARTUP.STORE_DATA('\t\t{}'.format('****************** Actual Result ******************'),Format=True,PDF= pdf)

            if res:
                if type(res) == list:
                    STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
                    Error_Info = '''ERROR\n\terror-type \t: \t{}\n\terror-tag \t: \t{}\n\terror-severity \t: \t{}\n\tmessage' \t: \t{}'''.format(*map(str,res))
                    STARTUP.STORE_DATA(Error_Info,Format=False,PDF= pdf)
                    return Error_Info
                    # raise '\t\tFAIL-REASON\t\n{}'.format(Error_Info)


                else:
                    STARTUP.STORE_DATA(f"{'REJECT-REASON' : <15}{'=' : ^20}{res : ^20}",Format=True,PDF= pdf)
                    # raise '\t\tFAIL-REASON\t\n{}'.format(res)


                STARTUP.ACT_RES(f"{'ALARM_17' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(255,0,0))
                return res


            else:
                STARTUP.ACT_RES(f"{'ALARM_17' : <50}{'=' : ^20}{'SUCCESS' : ^20}",PDF= pdf,COL=(0,255,0))
                return True
                
            
    ############################### Known Exceptions ####################################################
    except socket.timeout as e:
        Error = '{} : Call Home is not initiated, SSH Socket connection lost....'.format(
            e)
        STARTUP.STORE_DATA(Error, Format=True,PDF=pdf)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(
            f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
        return Error
        # raise socket.timeout('{}: SSH Socket connection lost....'.format(e)) from None

    except errors.SSHError as e:
        Error = '{} : SSH Socket connection lost....'.format(e)
        STARTUP.STORE_DATA(Error, Format=True,PDF=pdf)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(
            f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
        return Error
        # raise errors.SSHError('{}: SSH Socket connection lost....'.format(e)) from None

    except errors.AuthenticationError as e:
        Error = "{} : Invalid username/password........".format(e)
        STARTUP.STORE_DATA(Error, Format=True,PDF=pdf)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(
            f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
        return Error
        # raise f'{e} : Invalid username/password........'

    except NoValidConnectionsError as e:
        Error = '{} : ...'.format(e)
        STARTUP.STORE_DATA(Error, Format=True,PDF=pdf)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(
            f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
        return Error
        # raise e

    except TimeoutError as e:
        Error = '{} : Call Home is not initiated, Timout Expired....'.format(e)
        STARTUP.STORE_DATA(Error, Format=True,PDF=pdf)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(
            f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
        return Error
        # raise f'{e} : Call Home is not initiated, Timout Expired....'

    except SessionCloseError as e:
        Error = "{} : Unexpected_Session_Closed....".format(e)
        STARTUP.STORE_DATA(Error, Format=True,PDF=pdf)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(
            f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
        return Error
        # raise f'{e},Unexpected_Session_Closed....'

    except TimeoutExpiredError as e:
        Error = "{} : TimeoutExpiredError....".format(e)
        STARTUP.STORE_DATA(Error, Format=True,PDF=pdf)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(
            f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
        return Error
        # raise e

    except OSError as e:
        Error = '{} : Call Home is not initiated, Please wait for sometime........'.format(
            e)
        STARTUP.STORE_DATA(Error, Format=True,PDF=pdf)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(
            f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
        return Error
        # raise Exception('{} : Please wait for sometime........'.format(e)) from None

    except Exception as e:
        STARTUP.STORE_DATA('{}'.format(e), Format=True,PDF=pdf)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(
            f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
        return e
        # raise Exception('{}'.format(e)) from None


    ############################### MAKE PDF File ####################################################
    finally:
        STARTUP.CREATE_LOGS('M_CTC_ID_012',PDF=pdf)


if __name__ == "__main__":
    test_MAIN_FUNC_012()
