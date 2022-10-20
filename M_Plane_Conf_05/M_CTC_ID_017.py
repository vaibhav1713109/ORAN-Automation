import socket
import sys
import os
import warnings
import time
from ncclient import manager, operations
import string
from ncclient.operations import rpc
from ncclient.operations.errors import TimeoutExpiredError
from ncclient.operations.rpc import RPCError
from ncclient.transport.errors import SessionCloseError
from ncclient.xml_ import to_ele
import paramiko
from paramiko.ssh_exception import NoValidConnectionsError
import xmltodict
import xml.dom.minidom
import STARTUP
from ncclient.transport import errors
import lxml.etree
import Config

pdf = STARTUP.PDF_CAP()

def session_login(host, port, user, password):
    try:
        with manager.connect(host=host, port=port, username=user, hostkey_verify=False, password=password, allow_agent=False, look_for_keys=False) as m:

            STARTUP.STORE_DATA(
                '\t\t********** Connect to the NETCONF Server ***********', Format='TEST_STEP', PDF=pdf)
            STATUS = STARTUP.STATUS(host, user, m.session_id, port)
            STARTUP.STORE_DATA(STATUS, Format=False, PDF=pdf)

            ########################### Server Capabilities ############################
            for i in m.server_capabilities:
                STARTUP.STORE_DATA("\t{}".format(i), Format=False, PDF=pdf)

            try:
                ########################### Create_subscription ############################
                cap = m.create_subscription()
                STARTUP.STORE_DATA('>subscribe', Format=True, PDF=pdf)
                dict_data = xmltodict.parse(str(cap))
                if dict_data['nc:rpc-reply']['nc:ok'] == None:
                    STARTUP.STORE_DATA('\nOk\n', Format=False, PDF=pdf)



                pdf.add_page()
                ########################### Initial Get Filter ############################
                STARTUP.STORE_DATA('> get --filter-xpath /o-ran-software-management:software-inventory',Format=True, PDF=pdf)
                sw_inv = '''<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <software-inventory xmlns="urn:o-ran:software-management:1.0">
                </software-inventory>
                </filter>'''
                slot_names = m.get(sw_inv).data_xml
                s = xml.dom.minidom.parseString(slot_names)
                xml_pretty_str = s.toprettyxml()
                slot_n = xmltodict.parse(str(slot_names))
                li = ['INVALID', 'EMPTY']
                slots_info1 = slot_n['data']['software-inventory']['software-slot']
                for SLOT in slots_info1:
                    if SLOT['status'] in li:
                        STARTUP.STORE_DATA(xml_pretty_str,Format='XML', PDF=pdf)

                        return f'SW slot status is Invalid for {SLOT["name"]}...'
                STARTUP.STORE_DATA(xml_pretty_str, Format='XML', PDF=pdf)



                ########################### Configure Reset RPC in RU ############################
                Test_Step1 = '\t\tStep 1 : TER NETCONF Client sends <rpc><reset></rpc> to the O-RU NETCONF Server..'
                STARTUP.STORE_DATA('{}'.format(Test_Step1),Format='TEST_STEP', PDF=pdf)
                STARTUP.STORE_DATA('\n> user-rpc\n',Format=True, PDF=pdf)
                STARTUP.STORE_DATA('******* Replace with below xml ********',Format=True, PDF=pdf)
                xml_data3 = '''<reset xmlns="urn:o-ran:operations:1.0"></reset>'''
                STARTUP.STORE_DATA(xml_data3,Format='XML', PDF=pdf)
                d3 = m.dispatch(to_ele(xml_data3))

                Test_Step2 = '\t\tStep 2 : O-RU NETCONF Server responds with rpc-reply.'
                STARTUP.STORE_DATA('{}'.format(Test_Step2),Format='TEST_STEP', PDF=pdf)
                STARTUP.STORE_DATA('{}'.format(d3),Format='XML', PDF=pdf)

                Test_Step3 = '\t\tStep 3 : O-RU restarts with a new software version running matching the version activated.'
                STARTUP.STORE_DATA(
                    '{}'.format(Test_Step3),Format='TEST_STEP', PDF=pdf)


            except RPCError as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                return [e.type, e.tag, e.severity, e.message, exc_tb.tb_lineno]

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




########################### Get Filter after Reboot the RU ############################
def get_config_detail(host, port, user, password):
    try:
        with manager.connect(host=host, port=port, username=user, hostkey_verify=False, password=password, allow_agent=False, look_for_keys=False) as m:

            sw_inv = '''<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <software-inventory xmlns="urn:o-ran:software-management:1.0">
                </software-inventory>
                </filter>'''

            slot_names = m.get(sw_inv).data_xml
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

    ########################### Known Exceptions ############################
    except RPCError as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        return [e.type, e.tag, e.severity, e.message, exc_tb.tb_lineno]

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





########################### Main Function ############################
def test_MAIN_FUNC_017():
   
   

    try:
        USER_N = Config.details['SUDO_USER']
        PSWRD = Config.details['SUDO_PASS']

        ############################### Perform Call Home to get IP #######################################
        m = manager.call_home(host='', port=4334, hostkey_verify=False,
                              username=USER_N, password=PSWRD, allow_agent=False, look_for_keys=False)
        # ['ip_address', 'TCP_Port']
        li = m._session._transport.sock.getpeername()
        sid = m.session_id
        if m:
            STARTUP.kill_ssn(li[0], 830, USER_N, PSWRD, sid)
            time.sleep(10)
            RU_Details = STARTUP.demo(li[0], 830, USER_N, PSWRD)
            for key, val in RU_Details[1].items():
                if val[1] == 'true':
                    ############################### Test Description #############################
                    Test_Desc = '''Test Description : This scenario is MANDATORY
                    This test validates that the O-RU can successfully start up with activated software.
                    This scenario corresponds to the following chapters in [3]:
                    5. Software Management'''
                    CONFIDENTIAL = STARTUP.ADD_CONFIDENTIAL('17', SW_R=val[2])
                    STARTUP.STORE_DATA(CONFIDENTIAL, Format='CONF', PDF=pdf)
                    STARTUP.STORE_DATA(Test_Desc, Format='DESC', PDF=pdf)
                    pdf.add_page()

            
            del RU_Details[1]['swRecoverySlot']
            time.sleep(10)
            res = session_login(li[0], 830, USER_N, PSWRD)
            time.sleep(5)

            ############################### Check the result of session login #############################
            '''If None is return from session login (Reset RPC configure successfully then it will wait 
            untill RU comes up and then start call home for fetching IP Address and then get the details 
            of newly update/activate SW[This is applicable in case of if SW is activated{M_CTC_ID_016}..])'''
            if res == None:
                host = li[0]
                port = 22
                username = USER_N
                password = PSWRD
                command1 = f"cd {Config.details['SYSLOG_PATH']}; cat {Config.details['syslog_name']};"
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(host, port, username, password)

                stdin, stdout, stderr = ssh.exec_command(command1)
                lines1 = stdout.readlines()
                time.sleep(120)

                ############################### Perform Call Home to get IP after RU comes up#######################################
                m1 = manager.call_home(host='', port=4334, hostkey_verify=False, username=USER_N,
                                       password=PSWRD, allow_agent=False, look_for_keys=False, timeout=60)
                # ['ip_address', 'TCP_Port']
                li1 = m1._session._transport.sock.getpeername()


                if m1:
                    ssid = m1.session_id
                    host = li1[0]
                    STARTUP.kill_ssn(li1[0], 830, USER_N, PSWRD, ssid)
                    time.sleep(10)
                    # For getting software inventory
                    slot_s = get_config_detail(li1[0], 830, USER_N, PSWRD)
                    STARTUP.STORE_DATA('\t\t\t\tSYSTEM LOGS',Format=True, PDF=pdf)
                    command = "cd {}; cat {};".format(Config.details['SYSLOG_PATH'],Config.details['syslog_name'])
                    ssh = paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    ssh.connect(host, port, USER_N, PSWRD)

                    stdin, stdout, stderr = ssh.exec_command(command)
                    lines2 = stdout.readlines()
                    for i in lines1:
                        STARTUP.STORE_DATA('{}'.format(i),Format=False, PDF=pdf)
                    for i in lines2:
                        STARTUP.STORE_DATA('{}'.format(i),Format=False, PDF=pdf)



                    ############################### Expected/Actual Result ####################################################
                    pdf.add_page()
                    Exp_Result = '''Expected Result : 1. The status of the software slot used for software activation remains VALID (it is unchanged) and the parameter "active" remains "True". The parameter "running" is set to True.
2. Status of the software slot containing the previous version of software used by device remains VALID, the parameter "active" remains False. The parameter "running" is set to False.'''
                    STARTUP.STORE_DATA(Exp_Result, Format='DESC', PDF=pdf)

                    STARTUP.STORE_DATA('\t\t{}'.format(
                        '****************** Actual Result ******************'), Format=True, PDF=pdf)

     
                    if slot_s:
                        if type(slot_s) == list:
                            STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
                            Error_Info = '''ERROR\n\terror-type \t: \t{}\n\terror-tag \t: \t{}\n\terror-severity \t: \t{}\n\tmessage' \t: \t{}'''.format(*map(str,res))
                            STARTUP.STORE_DATA(Error_Info,Format=False,PDF= pdf)
                            return Error_Info
                            # raise '\t\tFAIL-REASON\t\n{}'.format(Error_Info)
                        
                        else:
                            STARTUP.STORE_DATA(f"{'activation-event-status' : <15}{'=' : ^20}{slot_s : ^20}",Format=True,PDF= pdf)
                            # raise '\t\tFAIL-REASON\t\n activation-event-status :{}'.format(res)
                        STARTUP.ACT_RES(f"{'Supplemental Reset after Software Activation' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(255,0,0))
                        return res


                    else:
                        STARTUP.ACT_RES(f"{'Supplemental Reset after Software Activation' : <50}{'=' : ^20}{'SUCCESS' : ^20}",PDF= pdf,COL=(0,255,0))
                        return True



            else:
                ############################### Expected/Actual Result ####################################################
                pdf.add_page()
                STARTUP.GET_SYSTEM_LOGS(li[0], USER_N, PSWRD, pdf)
                Exp_Result = '''Expected Result : 1. The status of the software slot used for software activation remains VALID (it is unchanged) and the parameter "active" remains "True". The parameter "running" is set to True.
2. Status of the software slot containing the previous version of software used by device remains VALID, the parameter "active" remains False. The parameter "running" is set to False.'''
                STARTUP.STORE_DATA(Exp_Result, Format='DESC', PDF=pdf)

                STARTUP.STORE_DATA('\t\t{}'.format(
                    '****************** Actual Result ******************'), Format=True, PDF=pdf)

                if type(res) == list:
                    STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
                    Error_Info = '''ERROR\n\terror-type \t: \t{}\n\terror-tag \t: \t{}\n\terror-severity \t: \t{}\n\tmessage' \t: \t{}'''.format(*map(str,res))
                    STARTUP.STORE_DATA(Error_Info,Format=False,PDF= pdf)
                    return Error_Info
                    # raise '\t\tFAIL-REASON\t\n{}'.format(Error_Info)


                else:
                    STARTUP.STORE_DATA(f"{'REJECT-REASON' : <15}{'=' : ^20}{res : ^20}",Format=True,PDF= pdf)
                    # raise '\t\tFAIL-REASON\t\n{}'.format(res)


                STARTUP.ACT_RES(f"{'Supplemental Reset after Software Activation' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(255,0,0))
                return res



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
        STARTUP.CREATE_LOGS('M_CTC_ID_017',PDF=pdf)


if __name__ == "__main__":
    test_MAIN_FUNC_017()
