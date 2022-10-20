from logging import exception
import socket
import sys
#warnings.simplefilter("ignore", DeprecationWarning)
from ncclient import manager
from ncclient.operations.rpc import RPCError
from ncclient.transport.errors import SSHError
import xmltodict
import time
import xml.dom.minidom
from ncclient.transport import errors
from paramiko.ssh_exception import NoValidConnectionsError
from ncclient.operations.errors import TimeoutExpiredError
from ncclient.transport.errors import SessionCloseError
import STARTUP
import lxml.etree
import Config
import DHCP_CONF.Genrate_User_Pass as Genrate_User_Pass

pdf = STARTUP.PDF_CAP()


def FETCH_DATA(host, port, user, password):
    # Fetching all the interface
    with manager.connect(host=host, port=port, username=user, hostkey_verify=False, password=password, allow_agent=False, look_for_keys=False) as m:
        u_name = '''
        <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            <users xmlns="urn:o-ran:user-mgmt:1.0">	
            </users>
        </filter>'''

        get_u = m.get(u_name).data_xml
        dict_u = xmltodict.parse(str(get_u))
        # STARTUP.STORE_DATA(user_name,OUTPUT_LIST=OUTPUT_LIST)
        s = xml.dom.minidom.parseString(get_u)
        #xml = xml.dom.minidom.parseString(user_name)

        xml_pretty_str = s.toprettyxml()

        return xml_pretty_str


def session_login(host, port, user, password, new_user, new_pswrd):
    try:
        with manager.connect(host=host, port=port, username=user, hostkey_verify=False, password=password, allow_agent=False, look_for_keys=False) as m:

            STARTUP.STORE_DATA(
                '\t\t********** Connect to the NETCONF Server ***********', Format='TEST_STEP', PDF=pdf)
            
            Test_Step1 = 'STEP 1 TER NETCONF client establishes a connection using a user account with nms privileges.'
            STARTUP.STORE_DATA('{}'.format(Test_Step1), Format='TEST_STEP', PDF=pdf)
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
            Test_Step2 = 'Step 2 TER NETCONF client attempts to configure a new user/password.'
            STARTUP.STORE_DATA('{}'.format(Test_Step2), Format='TEST_STEP', PDF=pdf)
            STARTUP.STORE_DATA('> edit-config  --target running --config --defop merge', Format=True, PDF=pdf)
            STARTUP.STORE_DATA('******* Replace with below xml ********', Format=True, PDF=pdf)


            ########################### Merge New User ############################
            snip = f"""
                    <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                    <users xmlns="urn:o-ran:user-mgmt:1.0">
                        <user>
                            <name>{new_user}</name>
                            <account-type>PASSWORD</account-type>
                            <password>{new_pswrd}</password>
                            <enabled>true</enabled>
                        </user>
                    </users>
                    </config>"""

            STARTUP.STORE_DATA(snip, Format='XML', PDF=pdf)
            try:
                data3 = m.edit_config(
                    target="running", config=snip, default_operation='merge')
                dict_data1 = xmltodict.parse(str(data3))
                STARTUP.STORE_DATA('''######### RPC Reply #########''', Format=True, PDF=pdf)
                if dict_data1['nc:rpc-reply']['nc:ok'] == None:
                    return data3, 'Addition of new is complete...'

            ########################### Check Access Denied ############################
            except RPCError as e:
                if e.tag == 'access-denied':
                    Test_Step3 = 'Step 3 NETCONF server replies rejecting the protocol operation with an \'access-denied\' error'
                    STARTUP.STORE_DATA('{}'.format(Test_Step3), Format='TEST_STEP', PDF=pdf)
                    STARTUP.STORE_DATA('ERROR\n', Format=False, PDF=pdf)
                    STARTUP.STORE_DATA(
                        f"{'type' : ^20}{':' : ^10}{e.type: ^10}\n", Format=False, PDF=pdf)
                    STARTUP.STORE_DATA(
                        f"{'tag' : ^20}{':' : ^10}{e.tag: ^10}\n", Format=False, PDF=pdf)
                    STARTUP.STORE_DATA(
                        f"{'severity' : ^20}{':' : ^10}{e.severity: ^10}\n", Format=False, PDF=pdf)
                    STARTUP.STORE_DATA(
                        f"{'path' : ^20}{':' : ^10}{e.path: ^10}\n", Format=False, PDF=pdf)
                    STARTUP.STORE_DATA(
                        f"{'message' : ^20}{':' : ^10}{e.message: ^10}\n", Format=False, PDF=pdf)
                else:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    return [e.type, e.tag, e.severity, e.message, exc_tb.tb_lineno]

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
def test_Main_Func_020():
    
    
    
    new_user = Genrate_User_Pass.genrate_username()
    new_pswrd = Genrate_User_Pass.genrate_password()
    try:

        USER_SUDO = Config.details['SUDO_USER']
        PSWRD_SUDO = Config.details['SUDO_PASS']
        USER_N = Config.details['NMS_USER']
        PSWRD = Config.details['NMS_PASS']

        ############################### Perform Call Home to get IP #######################################
        m = manager.call_home(host='192.168.4.15', port=4334, hostkey_verify=False, timeout= 60,
                              username=USER_N, password=PSWRD, allow_agent=False, look_for_keys=False)
        # ['ip_address', 'TCP_Port']
        li = m._session._transport.sock.getpeername()
        sid = m.session_id



        if m:
            STARTUP.kill_ssn(li[0], 830, USER_SUDO, PSWRD_SUDO, sid)
            time.sleep(10)
            RU_Details = STARTUP.demo(li[0], 830, USER_SUDO, PSWRD_SUDO)

            for key, val in RU_Details[1].items():
                if val[0] == 'true' and val[1] == 'true':
                    ############################### Test Description #############################
                    Test_Desc = '''Test Description : This scenario is MANDATORY for an O-RU supporting the Hybrid M-plane architecture model.
 This test validates that the O-RU correctly implements NETCONF Access Control user privileges.
 The scenario corresponds to the following chapters in [3]:
 3.4 NETCONF Access Control'''
                    CONFIDENTIAL = STARTUP.ADD_CONFIDENTIAL('20', SW_R=val[2])
                    STARTUP.STORE_DATA(CONFIDENTIAL, Format='CONF', PDF=pdf)
                    STARTUP.STORE_DATA(Test_Desc, Format='DESC', PDF=pdf)
                    pdf.add_page()


            ########################### Initial Get Filter ############################
            STARTUP.STORE_DATA(
                '********** Initial Get ***********', Format='TEST_STEP',PDF=pdf)
            STARTUP.STORE_DATA(f'''> connect --ssh --host {li[0]} --port 830 --login {USER_SUDO}
                    Interactive SSH Authentication
                    Type your password:
                    Password: 
                    ''', Format=False,PDF=pdf)
            STARTUP.STORE_DATA("> get --filter-xpath /o-ran-usermgmt:users/user", Format=True,PDF=pdf)
            get_filter = FETCH_DATA(li[0], 830, USER_SUDO, PSWRD_SUDO)
            STARTUP.STORE_DATA(get_filter, Format='XML',PDF=pdf)
            pdf.add_page()
            time.sleep(5)
            res = session_login(li[0], 830, USER_N, PSWRD, new_user, new_pswrd)




            ############################### Expected/Actual Result ####################################################
            STARTUP.GET_SYSTEM_LOGS(li[0], USER_N, PSWRD, pdf)
            Exp_Result = 'Expected Result : The NETCONF server replies rejecting the protocol operation with an "access-denied" error.'
            STARTUP.STORE_DATA(Exp_Result, Format='DESC', PDF=pdf)

            STARTUP.STORE_DATA('\t\t{}'.format(
                '****************** Actual Result ******************'), Format=True, PDF=pdf)

            if res == None:
                STARTUP.ACT_RES(f"{'Access Control NMS (negative case)' : <50}{'=' : ^20}{'SUCCESS' : ^20}",PDF= pdf,COL=(0,255,0))
                return True

            elif type(res) == list:
                STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
                Error_Info = '''ERROR\n\terror-type \t: \t{}\n\terror-tag \t: \t{}\n\terror-severity \t: \t{}\n\tmessage' \t: \t{}'''.format(*map(str,res))
                STARTUP.STORE_DATA(Error_Info,Format=False,PDF= pdf)
                STARTUP.ACT_RES(f"{'Access Control NMS (negative case)' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(255,0,0))
                return Error_Info

            elif type(res) == str:
                STARTUP.STORE_DATA(f"{'REJECT-REASON' : <15}{'=' : ^20}{res : ^20}",Format=True,PDF= pdf)
                # raise '\t\tFAIL-REASON\t\n {}'.format(res)
                STARTUP.ACT_RES(f"{'Access Control NMS (negative case)' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(255,0,0))
                return res

            else:
                STARTUP.STORE_DATA(f"{'REJECT-REASON' : <15}{'=' : ^20}{res : ^20}",Format=True,PDF= pdf)
                # raise '\t\tFAIL-REASON\t\n {}'.format(res)
                STARTUP.ACT_RES(f"{'Access Control NMS (negative case)' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(255,0,0))
                return res
        # m.close_session()



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
        STARTUP.CREATE_LOGS('M_CTC_ID_020', PDF=pdf)


if __name__ == "__main__":
    result = test_Main_Func_020()
    if result == True:
        pass
    else:
        STARTUP.ACT_RES(f"{'Access Control NMS (negative case)' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(255,0,0))
        # raise Exception(''.format(result)) from None


