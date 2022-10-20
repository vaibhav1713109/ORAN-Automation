########################################################################
# import inbuilds
########################################################################

import re
import sys, os, warnings
import time
import socket
#warnings.simplefilter("ignore", DeprecationWarning)
from ncclient import manager
import string
from ncclient.operations import errors
from ncclient.operations.rpc import RPCError
import xmltodict
import xml.dom.minidom
import paramiko
from ncclient.transport import errors
#xml_1 = open('o-ran-interfaces.xml').read()
import lxml.etree
from paramiko.ssh_exception import NoValidConnectionsError
from ncclient.operations.errors import TimeoutExpiredError
from ncclient.transport.errors import SessionCloseError

########################################################################
# import submodule
########################################################################
# from M_Plane_Conf_04.M_Plane_Sanity import STARTUP, Config
import STARTUP, Config
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from require.calnexRest import calnexInit, calnexGet, calnexSet, calnexCreate, calnexDel,calnexGetVal
from configparser import ConfigParser

########################################################################
# get dirpath for reading input file
########################################################################
directory_path = os.path.dirname(os.path.abspath(__file__))
filename = "{}/input.ini".format(directory_path)
config = ConfigParser()
config.read(filename)

########################################################################
# Initialize PDF
########################################################################
pdf = STARTUP.PDF_CAP()

def session_login(host, port, user, password,P_NEO_PORT):
    
    try:
        with manager.connect(host=host, port=port, username=user, hostkey_verify=False, password=password,key_filename = '/home/vvdn/.ssh/id_rsa.pub', allow_agent = False , look_for_keys = False) as m:
       
            STARTUP.STORE_DATA('\n\n\t\t********** Connect to the NETCONF Server ***********\n\n',Format='TEST_STEP',PDF = pdf)
            STATUS = STARTUP.STATUS(host,user,m.session_id,port)
            STARTUP.STORE_DATA(STATUS,Format=False,PDF = pdf)


            ########################### Server Capabilities ############################
            for i in m.server_capabilities:
                STARTUP.STORE_DATA("\t{}".format(i),Format=False,PDF = pdf)

            
            pdf.add_page()
            Test_Step1 = "STEP 1 and 2 subscribe and check for the <rpc> reply."
            STARTUP.STORE_DATA('{}'.format(Test_Step1),Format='TEST_STEP',PDF = pdf)
            
            
            try:   
                ########################### Create_subscription ############################
                cap=m.create_subscription()
                STARTUP.STORE_DATA('> subscribe', Format=True, PDF=pdf)
                dict_data = xmltodict.parse(str(cap))
                if dict_data['nc:rpc-reply']['nc:ok'] == None:
                    STARTUP.STORE_DATA('\nOk\n', Format=False, PDF=pdf)

                ########################### Check_Notification ############################
                STARTUP.STORE_DATA('{}'.format('################## Check_Notification ##################'),Format=True, PDF=pdf)
                while True:
                    n = m.take_notification()
                    notify=n.notification_xml
                    dict_n = xmltodict.parse(str(notify))
                    try:
                        notf = dict_n['notification']['alarm-notif']
                        if notf:
                            s = xml.dom.minidom.parseString(notify)
                            xml_pretty_str = s.toprettyxml()
                            STARTUP.STORE_DATA(xml_pretty_str,Format='XML', PDF=pdf)
                            STARTUP.STORE_DATA('{}\n'.format('-'*100),Format=False, PDF=pdf)
                            calnexSet(f"app/mse/master/Master{P_NEO_PORT}/stop")
                            calnexSet(f"app/generation/synce/esmc/Port{P_NEO_PORT}/stop")
                            break
                    except:
                        s = xml.dom.minidom.parseString(notify)
                        xml_pretty_str = s.toprettyxml()
                        STARTUP.STORE_DATA(xml_pretty_str,Format='XML', PDF=pdf)
                        STARTUP.STORE_DATA('{}\n'.format('-'*100),Format=False, PDF=pdf)
                
            except RPCError as e:
                return [e.type, e.tag, e.severity, e,e.message]

    ########################### Known Exceptions ############################
    except RPCError as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        return [e.type, e.tag, e.severity, e.path, e.message, exc_tb.tb_lineno]

    except FileNotFoundError as e:
        STARTUP.STORE_DATA("{0} FileNotFoundError {0}".format(
            "*"*30), Format=True, PDF=pdf)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA("\t\tError : {}".format(e), Format=False, PDF=pdf)
        return f'No such file or directory : {e.filename}\nError occured in line number {exc_tb.tb_lineno}'

    except lxml.etree.XMLSyntaxError as e:
        STARTUP.STORE_DATA("{0} XMLSyntaxError {}".format(
            "*"*30), Format=True, PDF=pdf)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA("\t\tError : {}".format(e), Format=False, PDF=pdf)
        return f"{e} \nError occured in line number {exc_tb.tb_lineno}"

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA("\t\tError : {}".format(e), Format=False, PDF=pdf)
        return f"{e} \nError occured in line number {exc_tb.tb_lineno}"
    

def PINGING(hostname):
    STARTUP.STORE_DATA("\t ########### Pinging ###########",Format=True,PDF = pdf)
    response = os.system("ping -c 5 " + hostname)
    #and then check the response...
    if response == 0:
        return True
    else:
        return False

########################### Main Function ############################
def test_MAIN_FUNC_002():
    
    ############################### User Input Details #######################################
    USER_N = config.get('INFO','super_user')
    PSWRD = config.get('INFO','super_user_pswrd')
    P_NEO_IP = config.get('INFO','paragon_ip')
    check_ping = PINGING(P_NEO_IP)
    if check_ping:
        print('\nParagon is ready for configuration...')
    else:
        print('\nParagon IP is not pinging...')
        return 0
    P_NEO_PORT = config.get('INFO','paragon_port')
    try:
        sys.path.append(f'//{P_NEO_IP}/calnex100g/RemoteControl/')
        calnexInit(f"{P_NEO_IP}")

        ############################### Perform Call Home to get IP #######################################
        m = manager.call_home(host = '', port=4334, hostkey_verify=False,username = USER_N, password = PSWRD, allow_agent = False , look_for_keys = False)
        li = m._session._transport.sock.getpeername()   #['ip_address', 'TCP_Port']
        sid = m.session_id
        
        if m:
            
            STARTUP.kill_ssn(li[0],830, USER_N, PSWRD,sid)
            RU_Details = STARTUP.demo(li[0],830, USER_N, PSWRD)
            calnexSet(f"app/mse/master/Master{P_NEO_PORT}/start")
            calnexSet(f"app/generation/synce/esmc/Port{P_NEO_PORT}/start")
            for key, val in RU_Details[1].items():
                    if val[0] == 'true' and val[1] == 'true':
                        ############################### Test Description #############################
                        Test_Desc = '''Test Description : This scenario is MANDATORY.
 This test validates that the O-RU properly handles a NETCONF subscription to notifications.
 This scenario corresponds to the following chapters in [3]:
 8.2 Manage Alarm Requests'''
                        CONFIDENTIAL = STARTUP.ADD_CONFIDENTIAL('07',SW_R = val[2]) 
                        STARTUP.STORE_DATA(CONFIDENTIAL,Format='CONF',PDF= pdf)
                        STARTUP.STORE_DATA(Test_Desc,Format='DESC',PDF= pdf)
                        pdf.add_page()

            
            
            
            time.sleep(5)
            res = session_login(li[0],830,USER_N,PSWRD,P_NEO_PORT)


            ############################### Expected/Actual Result ####################################################
            STARTUP.GET_SYSTEM_LOGS(li[0],USER_N,PSWRD,pdf)
            Exp_Result = 'Expected Result : The O-RU NETCONF Server responds with <rpc-reply><ok/></rpc-reply> to the TER NETCONF Client.'
            STARTUP.STORE_DATA(Exp_Result,Format='DESC',PDF= pdf)

            STARTUP.STORE_DATA('\t\t{}'.format('****************** Actual Result ******************'),Format=True,PDF= pdf)
            
            if res:
                if type(res) == list:
                    STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
                    Error_Info = '''ERROR\n\terror-type \t: \t{}\n\terror-tag \t: \t{}\n\terror-severity \t: \t{}\n\tpath \t: \t{}\n\tmessage' \t: \t{}'''.format(*map(str,res))
                    STARTUP.STORE_DATA(Error_Info,Format=False,PDF= pdf)
                    return Error_Info
                    # raise '\t\tFAIL-REASON\t\n{}'.format(Error_Info)
                else:
                    STARTUP.STORE_DATA(f"{'REJECT-REASON' : <15}{'=' : ^20}{res : ^20}",Format=True,PDF= pdf)
                    # raise '\t\tFAIL-REASON\t\n{}'.format(res)

                STARTUP.ACT_RES(f"{'Subscription to Notifications' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(255,0,0))
                return res
            else:
                STARTUP.ACT_RES(f"{'Subscription to Notifications' : <50}{'=' : ^20}{'SUCCESS' : ^20}",PDF= pdf,COL=(0,255,0))
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
            STARTUP.CREATE_LOGS('M_CTC_ID_007',PDF=pdf)


if __name__ == "__main__":
    test_MAIN_FUNC_002()
