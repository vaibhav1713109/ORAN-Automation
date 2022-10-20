import sys
import os
import warnings
import time
from ncclient import manager
from ncclient.operations.rpc import RPCError
from ncclient.xml_ import to_ele
import xmltodict
import socket
import xml.dom.minidom
import STARTUP
from paramiko.ssh_exception import NoValidConnectionsError
from ncclient.operations.errors import TimeoutExpiredError
from ncclient.transport.errors import SessionCloseError
from ncclient.transport import errors
import lxml.etree
import Config

pdf = STARTUP.PDF_CAP()
# print(OUT_LIST)


def session_login(host, port, user, password, slots):
    try:
        with manager.connect(host=host, port=port, username=user, hostkey_verify=False, password=password, allow_agent=False, look_for_keys=False) as m:

            STARTUP.STORE_DATA(
                '\t\t********** Connect to the NETCONF Server ***********', Format='TEST_STEP', PDF=pdf)
            STATUS = STARTUP.STATUS(host, user, m.session_id, port)
            STARTUP.STORE_DATA(STATUS, Format=False, PDF=pdf)

            ########################### Server Capabilities ############################
            for i in m.server_capabilities:
                STARTUP.STORE_DATA("\t{}".format(i), Format=False, PDF=pdf)

            ########################### Create_subscription ############################
            cap = m.create_subscription()
            STARTUP.STORE_DATA('>subscribe', Format=True, PDF=pdf)
            dict_data = xmltodict.parse(str(cap))
            if dict_data['nc:rpc-reply']['nc:ok'] == None:
                STARTUP.STORE_DATA('\nOk\n', Format=False, PDF=pdf)

            pdf.add_page()
            ########################### Initial Get Filter ############################
            STARTUP.STORE_DATA('\t\tInitial Get Filter',
                               Format='TEST_STEP', PDF=pdf)
            STARTUP.STORE_DATA(
                '\n> get --filter-xpath /o-ran-software-management:software-inventory', Format=True, PDF=pdf)
            sw_inv = '''<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            <software-inventory xmlns="urn:o-ran:software-management:1.0">
            </software-inventory>
            </filter>'''
            slot_names = m.get(sw_inv).data_xml

            ############ Checking The status, active and running value ##############
            s = xml.dom.minidom.parseString(slot_names)
            xml_pretty_str = s.toprettyxml()
            slot_n = xmltodict.parse(str(slot_names))
            SLOTS = slot_n['data']['software-inventory']['software-slot']
            SLOT_INFO = {}
            for SLOT in SLOTS:
                if SLOT['status'] == 'INVALID':
                    STARTUP.STORE_DATA(xml_pretty_str, Format='XML', PDF=pdf)
                    return f'SW slot status is Invalid for {SLOT["name"]}...'
                if (SLOT['name'] != 'swRecoverySlot'):
                    SLOT_INFO[SLOT['name']] = [SLOT['active'], SLOT['running']]

                if (SLOT['active'] == 'true' and SLOT['running'] == 'true') or (SLOT['active'] == 'false' and SLOT['running'] == 'false'):
                    if (SLOT['active'] == 'false' and SLOT['running'] == 'false') and (SLOT['name'] != 'swRecoverySlot'):
                        slot_name = SLOT['name']
                        del SLOT_INFO[SLOT['name']]
                    pass
                else:
                    return f'Slots Active and Running Status are diffrent for {SLOT["name"]}...'

            DEACTIVE_SLOT = list(SLOT_INFO.keys())
            STARTUP.STORE_DATA(xml_pretty_str, Format='XML', PDF=pdf)

            ########################### Configure SW Activate RPC in RU ############################
            Test_Step1 = '\t\tStep 1 : TER NETCONF Client triggers <rpc><software-activate> Slot must have attributes active = FALSE, running = FALSE.'
            STARTUP.STORE_DATA(
                '{}'.format(Test_Step1), Format='TEST_STEP', PDF=pdf)
            xml_data2 = open("Yang_xml/sw_activate.xml").read()
            xml_data2 = xml_data2.format(slot_name=slot_name)

            STARTUP.STORE_DATA('\n> user-rpc\n', Format=True, PDF=pdf)
            STARTUP.STORE_DATA(
                '******* Replace with below xml ********', Format=True, PDF=pdf)
            STARTUP.STORE_DATA(xml_data2, Format='XML', PDF=pdf)
            try:
                d3 = m.dispatch(to_ele(xml_data2))
                Test_Step2 = '\t\tStep 2 : O-RU NETCONF Server responds with <rpc-reply><software-activate><status>. The parameter "status" is set to STARTED.'
                STARTUP.STORE_DATA('{}'.format(Test_Step2),
                                   Format='TEST_STEP', PDF=pdf)
                STARTUP.STORE_DATA('{}'.format(d3), Format='XML', PDF=pdf)

                ########################### Capture_The_Notifications ############################
                while True:
                    n = m.take_notification(timeout=10)
                    if n == None:
                        break
                    notify = n.notification_xml
                    dict_n = xmltodict.parse(str(notify))
                    try:
                        notf = dict_n['notification']['activation-event']
                        if notf:
                            Test_Step3 = '\t\tStep 3 : O-RU NETCONF Server sends <notification><activation-event> with a status COMPLETED.'
                            STARTUP.STORE_DATA('{}'.format(
                                Test_Step3), Format='TEST_STEP', PDF=pdf)
                            x = xml.dom.minidom.parseString(notify)
                            xml_pretty_str = x.toprettyxml()
                            STARTUP.STORE_DATA(
                                xml_pretty_str, Format='XML', PDF=pdf)
                            status = dict_n['notification']['activation-event']['status']
                            if status != 'COMPLETED':
                                return status
                            break
                    except:
                        pass

                time.sleep(5)
                ########################### POST_GET_FILTER ############################
                pdf.add_page()
                STARTUP.STORE_DATA(
                    '\n> get --filter-xpath /o-ran-software-management:software-inventory', Format=True, PDF=pdf)
                sw_inv = '''<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                            <software-inventory xmlns="urn:o-ran:software-management:1.0">
                            </software-inventory>
                            </filter>'''
                slot_names1 = m.get(sw_inv).data_xml
                s = xml.dom.minidom.parseString(slot_names1)
                xml_pretty_str = s.toprettyxml()
                slots.pop(slot_name)
                slot_n1 = xmltodict.parse(str(slot_names1))
                SLOTS1 = slot_n1['data']['software-inventory']['software-slot']
                for slot in SLOTS1:
                    if slot['status'] == 'INVALID':
                        STARTUP.STORE_DATA(
                            xml_pretty_str, Format='XML', PDF=pdf)
                        return f'SW slot status is Invid for {SLOT["name"]}...'
                    if slot['name'] == slot_name:
                        if (slot['active'] == 'true') and slot['running'] == 'false':
                            pass
                        else:
                            STARTUP.STORE_DATA(
                                xml_pretty_str, Format='XML', PDF=pdf)
                            return f"SW Inventory didn't update for {slot_name}..."

                    if slot['name'] == DEACTIVE_SLOT[0]:
                        if (slot['active'] != 'false') and slot['running'] != 'true':
                            STARTUP.STORE_DATA(
                                xml_pretty_str, Format='XML', PDF=pdf)
                            return f"SW Inventory didn't update for {slot['name'] }..."
                STARTUP.STORE_DATA(xml_pretty_str, Format='XML', PDF=pdf)

            except RPCError as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                return [e.type, e.tag, e.severity, e.path, e.message, exc_tb.tb_lineno]

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


########################### Main Function ############################
def test_MAIN_FUNC_016():

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
                if val[0] == 'true' and val[1] == 'true':
                    ############################### Test Description #############################
                    Test_Desc = 'Test Description : The minimum functions of the TER described in section 2.1 that support validation of the M-Plane are operational, configured and connected to the O-RU'
                    CONFIDENTIAL = STARTUP.ADD_CONFIDENTIAL('16', SW_R=val[2])
                    STARTUP.STORE_DATA(CONFIDENTIAL, Format='CONF', PDF=pdf)
                    STARTUP.STORE_DATA(Test_Desc, Format='DESC', PDF=pdf)
                    pdf.add_page()

            del RU_Details[1]['swRecoverySlot']
            time.sleep(5)
            res = session_login(li[0], 830, USER_N, PSWRD, RU_Details[1])
            time.sleep(10)



            ############################### Expected/Actual Result ####################################################
            STARTUP.GET_SYSTEM_LOGS(li[0], USER_N, PSWRD, pdf)
            Exp_Result = 'Expected Result : \n 1. The O-RU NETCONF Server performs a software activation procedure. When the procedure is completed, the O-RU NETCONF Server sends <notification><activation-event> with a status COMPLETED and the slot-name in the activation event corresponds to the slot-name used in the software-activate RPC to the TER NETCONF Client.\n 2. Status of the software slot containing the software still used by device remains VALID, the parameter "active" is set to False. The parameter "running" is True.'
            STARTUP.STORE_DATA(Exp_Result, Format='DESC', PDF=pdf)

            STARTUP.STORE_DATA('\t\t{}'.format(
                '****************** Actual Result ******************'), Format=True, PDF=pdf)

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


                STARTUP.ACT_RES(f"{'O-RU Software Update and Install' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(255,0,0))
                return res


            else:
                STARTUP.ACT_RES(f"{'O-RU Software Update and Install' : <50}{'=' : ^20}{'SUCCESS' : ^20}",PDF= pdf,COL=(0,255,0))
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
        STARTUP.CREATE_LOGS('M_CTC_ID_016', PDF=pdf)


if __name__ == "__main__":
    test_MAIN_FUNC_016()
