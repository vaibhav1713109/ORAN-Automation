from random import randint
from socket import socket
import sys, os, warnings
import lxml.etree
from ncclient import manager
from ncclient.operations.rpc import RPCError
from ncclient.transport import errors
from ncclient.xml_ import to_ele
import xmltodict
import STARTUP
import paramiko
from paramiko.ssh_exception import NoValidConnectionsError
from ncclient.operations.errors import TimeoutExpiredError
from ncclient.transport.errors import SessionCloseError
import time
import Config

pdf = STARTUP.PDF_CAP()

def session_login(host, port, user, password,s_n_i,g_t):
    with manager.connect(host=host, port=port, username=user, hostkey_verify=False, password=password, allow_agent = False , look_for_keys = False) as m:
        STARTUP.STORE_DATA(
                '\t\t********** Connect to the NETCONF Server ***********', Format='TEST_STEP', PDF=pdf)
        STATUS = STARTUP.STATUS(host, user, m.session_id, port)
        STARTUP.STORE_DATA(STATUS, Format=False, PDF=pdf)

        ########################### Server Capabilities ############################
        for i in m.server_capabilities:
            STARTUP.STORE_DATA("\t{}".format(i), Format=False, PDF=pdf)

        
        pdf.add_page()
        try:
            ########################### Create_subscription ############################
            sub = """<create-subscription xmlns="urn:ietf:params:xml:ns:netconf:notification:1.0">
                        <filter type="subtree">
                                <supervision-notification xmlns="urn:o-ran:supervision:1.0"></supervision-notification>                            
                        </filter>
                    </create-subscription>
            """
            cap = m.dispatch(to_ele(sub))
            
            STARTUP.STORE_DATA('> subscribe', Format=True, PDF=pdf)
            dict_data = xmltodict.parse(str(cap))
            if dict_data['nc:rpc-reply']['nc:ok'] == None:
                STARTUP.STORE_DATA('\nOk\n', Format=False, PDF=pdf)
            
            
            
            ########################### Configure Supervision Yang ############################
            xml_data = open("Yang_xml/supervision.xml").read()
            xml_data = xml_data.format(super_n_i= s_n_i, guard_t_o= g_t)
            
            Test_Step1 = '\t\t TER NETCONF Client responds with <rpc supervision-watchdog-reset></rpc> to the O-RU NETCONF Server'
            STARTUP.STORE_DATA('{}'.format(Test_Step1),Format='TEST_STEP', PDF=pdf)
            STARTUP.STORE_DATA('> user-rpc',Format=True, PDF=pdf)
            STARTUP.STORE_DATA('******* Replace with below xml ********',Format=True, PDF=pdf)
            STARTUP.STORE_DATA('{}\n'.format(xml_data),Format='XML', PDF=pdf)
            try:
                d = m.dispatch(to_ele(xml_data))
                
                Test_Step2 = '\t\t O-RU NETCONF Server sends a reply to the TER NETCONF Client <rpc-reply><next-update-at>date-time</next-update-at></rpc-reply>'
                STARTUP.STORE_DATA('{}'.format(Test_Step2),Format='TEST_STEP', PDF=pdf)
                STARTUP.STORE_DATA('{}'.format(d),Format='XML', PDF=pdf)
                
                # n = m.take_notification()
                # notify = n.notification_xml
                # dict_n = xmltodict.parse(str(notify))
                # try:
                    
                #     notf = dict_n['notification']['supervision-notification']
                #     if notf:
                #         Test_Step3 = '\t\t O-RU NETCONF Server sends a supervision notification towards the TER NETCONF Client.'
                #         STARTUP.STORE_DATA('{}'.format(Test_Step3),Format='TEST_STEP', PDF=pdf)
                #         x = xml.dom.minidom.parseString(notify)
                #         #xml = xml.dom.minidom.parseString(user_name)
                #         xml_pretty_str = x.toprettyxml()
                #         STARTUP.STORE_DATA(xml_pretty_str,Format='XML', PDF=pdf)
                            
                            
                # except exception as e:
                #     return e



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
def test_MAIN_FUNC_009():
   

    try:
        
        USER_N = Config.details['SUDO_USER']
        PSWRD = Config.details['SUDO_PASS']
        s_n_i = randint(1,10)
        g_t = randint(1,s_n_i)
        
        
        ############################### Perform Call Home to get IP #######################################
        m = manager.call_home(host = '', port=4334, hostkey_verify=False,username = USER_N, password = PSWRD, allow_agent = False , look_for_keys = False, timeout = 60)
        li = m._session._transport.sock.getpeername()   #['ip_address', 'TCP_Port']
        sid = m.session_id

        if m:
            STARTUP.kill_ssn(li[0],830, USER_N, PSWRD,sid)
            RU_Details = STARTUP.demo(li[0], 830, USER_N, PSWRD)
            
            for key, val in RU_Details[1].items():
                    if val[0] == 'true' and val[1] == 'true':
                        ############################### Test Description #############################
                        Test_Desc = 'Test Description : This test validates that the O-RU manages the connection supervision process correctly.'
                        CONFIDENTIAL = STARTUP.ADD_CONFIDENTIAL('09',SW_R = val[2]) 
                        STARTUP.STORE_DATA(CONFIDENTIAL,Format='CONF',PDF= pdf)
                        STARTUP.STORE_DATA(Test_Desc,Format='DESC',PDF= pdf)
                        pdf.add_page()
            
           

            time.sleep(10)
            res = session_login(li[0],830,USER_N, PSWRD, s_n_i,g_t)
            # time.sleep(10)


            if res:
                # For Capturing the logs
                ############################### Expected/Actual Result ####################################################
                STARTUP.GET_SYSTEM_LOGS(li[0],USER_N,PSWRD,pdf)
                Exp_Result = 'Expected Result : The TER NETCONF Client does not issue <rpc supervision-watchdog-reset></rpc> to the O-RU NETCONF Server and causes the watchdog timer to expire on the O-RU.'
                STARTUP.STORE_DATA(Exp_Result,Format='DESC',PDF= pdf)

                STARTUP.STORE_DATA('\t\t{}'.format('****************** Actual Result ******************'),Format=True,PDF= pdf)
            

                if type(res) == list:
                    STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
                    Error_Info = '''ERROR\n\terror-type \t: \t{}\n\terror-tag \t: \t{}\n\terror-severity \t: \t{}\n\tmessage' \t: \t{}'''.format(*map(str,res))
                    STARTUP.STORE_DATA(Error_Info,Format=False,PDF= pdf)
                    return Error_Info
                    # raise '\t\tFAIL-REASON\t\n{}'.format(Error_Info)


                else:
                    STARTUP.STORE_DATA(f"{'REJECT-REASON' : <15}{'=' : ^20}{res : ^20}",Format=True,PDF= pdf)
                    # raise '\t\tFAIL-REASON\t\n{}'.format(res)



                STARTUP.ACT_RES(f"{'M-Plane Connection Supervision (negative case)' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(255,0,0))
                return res
                
            else:
                # time.sleep(100)
                # For Capturing the logs
                # time.sleep(130)
                host = li[0]
                port = 22
                username = USER_N
                password = PSWRD
                pdf.add_page()
                STARTUP.STORE_DATA('\t\t\t\tSYSTEM LOGS',Format=True,PDF= pdf)

                command = "cd {0}; cat {1}".format(Config.details['SYSLOG_PATH'],Config.details['syslog_name'])
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(host, port, username, password)

                stdin, stdout, stderr = ssh.exec_command(command)
                lines = stdout.readlines()
                for i in lines:
                    STARTUP.STORE_DATA(i,Format=False,PDF= pdf)

                pdf.add_page()
                ############################### Expected/Actual Result ####################################################
                Exp_Result = 'Expected Result : The TER NETCONF Client does not issue <rpc supervision-watchdog-reset></rpc> to the O-RU NETCONF Server and causes the watchdog timer to expire on the O-RU.'
                STARTUP.STORE_DATA(Exp_Result,Format='DESC',PDF= pdf)

                STARTUP.STORE_DATA('\t\t{}'.format('****************** Actual Result ******************'),Format=True,PDF= pdf)
            
                STARTUP.ACT_RES(f"{'M-Plane Connection Supervision (negative case)' : <50}{'=' : ^20}{'SUCCESS' : ^20}",PDF= pdf,COL=(0,255,0))
                return True

    ############################### Known Exceptions ####################################################
    # except socket.timeout as e:
    #     Error = '{} : Call Home is not initiated, SSH Socket connection lost....'.format(
    #         e)
    #     STARTUP.STORE_DATA(Error, Format=True,PDF=pdf)
    #     exc_type, exc_obj, exc_tb = sys.exc_info()
    #     STARTUP.STORE_DATA(
    #         f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
    #     return Error
    #     # raise socket.timeout('{}: SSH Socket connection lost....'.format(e)) from None

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
        STARTUP.CREATE_LOGS('M_CTC_ID_009',PDF=pdf)


if __name__ == "__main__":
    test_MAIN_FUNC_009()