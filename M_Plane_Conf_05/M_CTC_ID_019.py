import socket
import sys, os, warnings
import time
#warnings.simplefilter("ignore", DeprecationWarning)
from ncclient import manager
import string
from ncclient.operations.rpc import RPCError
from ncclient.transport.errors import SSHError
import xmltodict
import paramiko
import xml.dom.minidom  
from ncclient.transport import errors
from paramiko.ssh_exception import NoValidConnectionsError
from ncclient.operations.errors import TimeoutExpiredError
from ncclient.transport.errors import SessionCloseError
import STARTUP
import lxml.etree
import Config

pdf = STARTUP.PDF_CAP()



def session_login(host, port, user, password):
    try:
        with manager.connect(host=host, port=port, username=user, hostkey_verify=False, password=password, allow_agent = False , look_for_keys = False) as m:
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
            try:

                ########################### Initial Get Filter ############################
                u_name = '''
                        <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                        <users xmlns="urn:o-ran:user-mgmt:1.0">	
                        </users>
                        </filter>
                        '''
                user_name = m.get_config('running', u_name).data_xml
                dict_u = xmltodict.parse(str(user_name))
                
                Test_STEP1 = "###########Step 2 and 3 O-RU NETCONF server replies by silently omitting data nodes#####################"
                STARTUP.STORE_DATA('{}'.format(Test_STEP1),Format='TEST_STEP', PDF=pdf)
                STARTUP.STORE_DATA("> get --filter-xpath /o-ran-usermgmt:users/user",Format=True, PDF=pdf)
                s = xml.dom.minidom.parseString(user_name)
                xml_pretty_str = s.toprettyxml()
                STARTUP.STORE_DATA(xml_pretty_str,Format='XML', PDF=pdf)
                try:
                    pswrd = dict_u['data']['users']['user'][1]['password']  
                    if pswrd:
                        return pswrd
                except:
                    pass



            except RPCError as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                return [e.type, e.tag, e.severity ,e.message,exc_tb.tb_lineno]



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
def test_MAIN_FUNC_019():
    try:

        USER_N = Config.details['SUDO_USER']
        PSWRD = Config.details['SUDO_PASS']
        
        
        ############################### Perform Call Home to get IP #######################################
        m = manager.call_home(host = '192.168.4.15', port=4334, hostkey_verify=False,username = USER_N, password = PSWRD, timeout = 60, allow_agent = False , look_for_keys = False)
        li = m._session._transport.sock.getpeername()
        sid = m.session_id


        if m:
            
            STARTUP.kill_ssn(li[0],830, USER_N, PSWRD,sid)
            time.sleep(10)
            RU_Details = STARTUP.demo(li[0],830, USER_N, PSWRD)
            
            for key, val in RU_Details[1].items():
                    if val[0] == 'true' and val[1] == 'true':
                        ############################### Test Description #############################
                        Test_Desc = '''Test Description : This scenario is MANDATORY for an O-RU supporting the Hybrid M-plane architecture model.
 This test validates that the O-RU correctly implements NETCONF Access Control security aspects.
 The scenario corresponds to the following chapters in [3]:
 3.3 SSH Connection Establishment
 3.4 NETCONF Access Control'''
                        CONFIDENTIAL = STARTUP.ADD_CONFIDENTIAL('19', SW_R=val[2])
                        STARTUP.STORE_DATA(CONFIDENTIAL, Format='CONF', PDF=pdf)
                        STARTUP.STORE_DATA(Test_Desc, Format='DESC', PDF=pdf)
                        pdf.add_page()


            
            
            time.sleep(5)
            res = session_login(li[0],830,USER_N,PSWRD)
            time.sleep(5)


            ############################### Expected/Actual Result ####################################################
            STARTUP.GET_SYSTEM_LOGS(li[0], USER_N, PSWRD, pdf)
            Exp_Result = 'Expected Result : The O-RU NETCONF server replies by silently omitting data nodes and their descendants to which the client does not have read access from the <rpc-reply> message'
            STARTUP.STORE_DATA(Exp_Result, Format='DESC', PDF=pdf)

            STARTUP.STORE_DATA('\t\t{}'.format(
                '****************** Actual Result ******************'), Format=True, PDF=pdf)

            if res == None :
                STARTUP.ACT_RES(f"{'Access Control Sudo (negative case)' : <50}{'=' : ^20}{'SUCCESS' : ^20}",PDF= pdf,COL=(0,255,0))
                return True

            elif type(res) == list:
                STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
                Error_Info = '''ERROR\n\terror-type \t: \t{}\n\terror-tag \t: \t{}\n\terror-severity \t: \t{}\n\tmessage' \t: \t{}'''.format(*map(str,res))
                STARTUP.STORE_DATA(Error_Info,Format=False,PDF= pdf)
                STARTUP.ACT_RES(f"{'Access Control Sudo (negative case)' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(255,0,0))
                return Error_Info
   
                
            elif type(res) == str:
                STARTUP.STORE_DATA(f"{'REJECT-REASON' : <15}{'=' : ^20}{res : ^20}",Format=True,PDF= pdf)
                # raise '\t\tFAIL-REASON\t\n {}'.format(res)
                STARTUP.ACT_RES(f"{'Access Control Sudo (negative case)' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(255,0,0))
                return res
            
                
            else:
                STARTUP.STORE_DATA(f"{'REJECT-REASON' : <15}{'=' : ^20}{res : ^20}",Format=True,PDF= pdf)
                STARTUP.ACT_RES(f"{'Access Control Sudo (negative case)' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(255,0,0))
                # raise '\t\tFAIL-REASON\t\n {}'.format(res)
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
        STARTUP.CREATE_LOGS('M_CTC_ID_019', PDF=pdf)

if __name__ == "__main__":
    result = test_MAIN_FUNC_019()
    if result == True:
        pass
    else:
        STARTUP.ACT_RES(f"{'Access Control Sudo (negative case)' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(255,0,0))
        # raise Exception(''.format(result)) from None

