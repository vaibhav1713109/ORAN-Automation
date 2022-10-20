import socket
import sys, os, warnings
import time
#warnings.simplefilter("ignore", DeprecationWarning)
from ncclient import manager
from ncclient.operations.rpc import RPC, RPCError
#from netconf_client.ncclient import RPCError
import xmltodict
import xml.dom.minidom
import paramiko
#xml_1 = open('o-ran-interfaces.xml').read()
from ncclient.transport import errors
import STARTUP
import lxml.etree
from paramiko.ssh_exception import NoValidConnectionsError
from ncclient.operations.errors import TimeoutExpiredError
from ncclient.transport.errors import SessionCloseError
import Config

pdf = STARTUP.PDF_CAP()

class M_ctc_id_10:
   
    # init method or constructor 
    def __init__(self,host, port,sid,user2, pswrd2):
        self.host = host
        self.port = port
        self.sid = sid
        self.user2 = user2
        self.pswrd2 = pswrd2
   
    def session_login(self):
    
        with manager.connect(host=self.host, port=self.port, username=self.user2, hostkey_verify=False, password=self.pswrd2, allow_agent = False , look_for_keys = False) as m:
        
            STARTUP.STORE_DATA('\t\t********** Connect to the NETCONF Server ***********',Format='TEST_STEP',PDF = pdf)
            STATUS = STARTUP.STATUS(self.host,self.user2,m.session_id,self.port)
            STARTUP.STORE_DATA(STATUS,Format=False,PDF = pdf)


            ########################### Server Capabilities ############################
            for i in m.server_capabilities:
                STARTUP.STORE_DATA("\t{}".format(i),Format=False,PDF = pdf)
            
            
            pdf.add_page()
            ########################### Test Step ############################
            Test_Step1 = '\t\t***********step 1 and 2 Retrival of ru information with filter **********'
            STARTUP.STORE_DATA('{}'.format(Test_Step1),Format='TEST_STEP',PDF = pdf)
            try:
                STARTUP.STORE_DATA("get --filter-xpath /o-ran-usermgmt:users/user",Format=True,PDF = pdf)
                u_name = '''
                        <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                        <users xmlns="urn:o-ran:user-mgmt:1.0">	
                            <user>                                                        
                                
                            </user>
                        </users>
                        </filter>
                '''
                

                ########################### Get the RU details with filter ############################
                user_name = m.get_config('running', u_name).data_xml
                x = xml.dom.minidom.parseString(user_name)
                xml_pretty_str = x.toprettyxml()
                STARTUP.STORE_DATA(xml_pretty_str,Format='XML',PDF = pdf)


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
def test_MAIN_FUNC_011():
    


    try:
        USER_N = Config.details['SUDO_USER']
        PSWRD = Config.details['SUDO_PASS']


        ############################### Perform Call Home to get IP #######################################
        m = manager.call_home(host = '', port=4334, hostkey_verify=False,username = USER_N, password = PSWRD, allow_agent = False , look_for_keys = False)
        li = m._session._transport.sock.getpeername()   #['ip_address', 'TCP_Port']
        sid = m.session_id


        ############################### Make Object of class ####################################################        
        obj = M_ctc_id_10(li[0],830,sid,USER_N,PSWRD)
        if m:
            STARTUP.kill_ssn(li[0],830, USER_N, PSWRD,sid)
            RU_Details = STARTUP.demo(li[0], 830, USER_N, PSWRD)
            
            for key, val in RU_Details[1].items():
                    if val[0] == 'true' and val[1] == 'true':
                        
                        ############################### Test Description #############################
                        Test_Desc = 'Test Description : This scenario validates that the O-RU NETCONF Server properly executes a get command with a filter applied.'
                        CONFIDENTIAL = STARTUP.ADD_CONFIDENTIAL('11',SW_R = val[2]) 
                        STARTUP.STORE_DATA(CONFIDENTIAL,Format='CONF',PDF= pdf)
                        STARTUP.STORE_DATA(Test_Desc,Format='DESC',PDF= pdf)
                        pdf.add_page()


            
            
            time.sleep(5)
            res = obj.session_login()

            ############################### Expected/Actual Result ####################################################
            STARTUP.GET_SYSTEM_LOGS(li[0],USER_N,PSWRD,pdf)
            Exp_Result = 'Expected Result : The O-RU NETCONF Server responds with <rpc-reply><data> where <data> contains details for objects as conforming to the <filter>.'
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



                STARTUP.ACT_RES(f"{'GET_FILTER' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(255,0,0))
                return res


            else:
                STARTUP.ACT_RES(f"{'GET_FILTER' : <50}{'=' : ^20}{'SUCCESS' : ^20}",PDF= pdf,COL=(0,255,0))
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
        STARTUP.CREATE_LOGS('M_CTC_ID_011',PDF=pdf)


if __name__ == "__main__":
    test_MAIN_FUNC_011()