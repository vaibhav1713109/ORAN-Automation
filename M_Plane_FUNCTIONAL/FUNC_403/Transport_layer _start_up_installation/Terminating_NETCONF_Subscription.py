from socket import socket
import sys, os, warnings
from ncclient import manager, operations
import string
from ncclient.operations import rpc
from ncclient.operations.rpc import RPCError
from ncclient.xml_ import to_ele
import xmltodict
from ncclient.transport import errors
import re , time
from paramiko.ssh_exception import NoValidConnectionsError
from ncclient.operations.errors import TimeoutExpiredError
from ncclient.transport.errors import SessionCloseError
import STARTUP, Config
pdf = STARTUP.PDF_CAP()


def session_login(host, port, user, password):
    try:
        with manager.connect(host=host, port=port, username=user, hostkey_verify=False, password=password,allow_agent = False , look_for_keys = False) as m:

            
            STARTUP.STORE_DATA('********** Connect to the NETCONF Server ***********',Format='TEST_STEP',PDF=pdf)
            STATUS = STARTUP.STATUS(host,user,m.session_id,port)
            STARTUP.STORE_DATA(STATUS,Format=False,PDF=pdf)

            for i in m.server_capabilities:
                STARTUP.STORE_DATA('{}'.format(i),Format=False,PDF=pdf)
            


            pdf.add_page()
            #################### create subscription ####################                 
            cap = m.create_subscription()
            STARTUP.STORE_DATA('********** Create Subscription ***********',Format=True,PDF=pdf)
            STARTUP.STORE_DATA('>subscribe',Format=True,PDF=pdf)
            dict_data = xmltodict.parse(str(cap))
            if dict_data['nc:rpc-reply']['nc:ok']== None:
                STARTUP.STORE_DATA('\nOk\n',Format=False,PDF=pdf)
            


            
            try:
                xml_data = open("xml/M_FTC_ID_122.xml").read()
                # xml_data = xml_data.format(remote_file_path=rmt,pas=pswrd,public_key= pub_key ,ll_path=ll_path)
            except FileNotFoundError as e:
                STARTUP.STORE_DATA('{0} FileNotFoundError {0}'.format('*'*30),Format=False,PDF=pdf)
                STARTUP.STORE_DATA('{}'.format(e),Format=False,PDF=pdf)
                return e


            STARTUP.STORE_DATA('\t\t********* Configure CLOSE SESSION RPC *************',Format=True,PDF=pdf)
            STARTUP.STORE_DATA('> user-rpc',Format=True,PDF=pdf)
            STARTUP.STORE_DATA('\t\t******* Replace with below xml ********',Format=True,PDF=pdf)
            STARTUP.STORE_DATA(xml_data,Format='XML',PDF=pdf)
            STARTUP.STORE_DATA('\t\t*********** RPC Reply ***************',Format=True,PDF=pdf)
            try:
                d = m.dispatch(to_ele(xml_data))
                STARTUP.STORE_DATA('{}'.format(d),Format='XML',PDF=pdf)
                # print('\t\t******* O-RU NETCONF Server sends <notification><download> with status SUCCESS to TER NETCONF Client *******')
                # print('*'*100)
                # while True:
                #     n = m.take_notification()
                #     if n == None:
                #         break
                #     notify = n.notification_xml
                #     dict_n = xmltodict.parse(str(notify))
                #     try:
                #         notf = dict_n['notification']['file-download-event']
                #         if notf:
                #             x = xml.dom.minidom.parseString(notify)
                #             #xml = xml.dom.minidom.parseString(user_name)

                #             xml_pretty_str = x.toprettyxml()

                #             print(xml_pretty_str)
                #             print('-'*100)
                #             status = dict_n['notification']['file-download-event']['status']
                #             if status != 'SUCCESS':
                #                 return status
                #             break
                #     except:
                #         pass
            except RPCError as e:
                    return [e.type, e.tag, e.severity, e,e.message]

    except Exception as e:
        pass
            

        
       

        


def test_Subcription_terminate():
   #give the input configuration in xml file format
   #xml_1 = open('o-ran-hardware.xml').read()
   #give the input in the format hostname, port, username, password 
    user = Config.details['SUDO_USER']
    pswd = Config.details['SUDO_PASS']
    try:

        
        m = manager.call_home(host = '', port=4334, hostkey_verify=False,username = user, password = pswd ,allow_agent = False , look_for_keys = False)
        li = m._session._transport.sock.getpeername()
        #print(li)
        sid = m.session_id
        #print(sid)
        
    
        print('-'*100)
        print('-'*100)
        Data = STARTUP.demo(m)
        STARTUP.kill_ssn(li[0],830, user,pswd,sid)
        if m:
            users, slots= Data[0],Data[1]
            
            del slots['swRecoverySlot']
            
            for key, val in slots.items():
                if val[0] == 'true' and val[1] == 'true':
                    ############################### Test Description #############################
                    Test_Desc = '''Test Description : Test to verify the subscription is Terminating properly.'''
                    CONFIDENTIAL = STARTUP.ADD_CONFIDENTIAL('122',SW_R = val[2]) 
                    STARTUP.STORE_DATA(CONFIDENTIAL,Format='CONF',PDF= pdf)
                    STARTUP.STORE_DATA(Test_Desc,Format='DESC',PDF= pdf)
                    pdf.add_page()
            
            
            res = session_login(li[0],830,user,pswd)
            
            STARTUP.GET_SYSTEM_LOGS(li[0],user,pswd,pdf)             
            Exp_Result = '''Expected Result : 1. All kind of Subscriptions should be terminated'''
            STARTUP.STORE_DATA(Exp_Result,Format='DESC',PDF= pdf)

            STARTUP.STORE_DATA('\t\t{}'.format('****************** Actual Result ******************'),Format=True,PDF= pdf)

            if res:
                
                
                time.sleep(5)
                if type(res) == list:
                    STARTUP.STORE_DATA(f"ERROR",Format=True,PDF= pdf)
                    STARTUP.STORE_DATA(f"{'error-type' : <20}{':' : ^10}{res[0]: ^10}",Format=False,PDF=pdf)
                    STARTUP.STORE_DATA(f"{'error-tag' : <20}{':' : ^10}{res[1]: ^10}",Format=False,PDF=pdf)
                    STARTUP.STORE_DATA(f"{'error-severity' : <20}{':' : ^10}{res[2]: ^10}",Format=False,PDF=pdf)
                    #print(f"{'error-info' : <20}{':' : ^10}{res[3]: ^10}")
                    STARTUP.STORE_DATA(f"{'Description' : <20}{':' : ^10}{res[4]: ^10}",Format=False,PDF=pdf)
                    return res[5]
                else:
                    STARTUP.STORE_DATA(f"{'file-download-status' : <15}{'=' : ^20}{res : ^20}",Format=False,PDF=pdf)
                STARTUP.ACT_RES(f"{'STATUS' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(255,0,0))
                return res
                
            else:
                time.sleep(5)
                STARTUP.ACT_RES(f"{'STATUS' : <50}{'=' : ^20}{'PASS' : ^20}",PDF= pdf,COL=(105, 224, 113))
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
        li = sys.argv[0].split('.')
        STARTUP.CREATE_LOGS(li[0],PDF=pdf)

                
                
    
if __name__ == '__main__':
    Result = test_Subcription_terminate()
    if Result == True:
        pass
    else:
        pass
    