from socket import timeout, socket
import sys, os, warnings
import time
from ncclient import manager
from ncclient.transport import errors
from ncclient.operations.rpc import RPCError
from ncclient.transport import session
from ncclient.transport.errors import SSHError
from ncclient.transport.session import Session
import xmltodict
import xml.dom.minidom
from paramiko.ssh_exception import AuthenticationException
from paramiko.ssh_exception import NoValidConnectionsError
from ncclient.operations.errors import TimeoutExpiredError
from ncclient.transport.errors import SessionCloseError
import lxml.etree
import Config
import STARTUP, DHCP_CONF.Genrate_User_Pass as Genrate_User_Pass

pdf = STARTUP.PDF_CAP()


def Create_user(host, port, nam, pas1,USER_N, PSWRD):
    try:
        with manager.connect(host=host, port=port, username=USER_N, hostkey_verify=False, password=PSWRD, allow_agent = False , look_for_keys = False) as m:

            
            STARTUP.STORE_DATA(
                '\t\t********** Connect to the NETCONF Server ***********', Format='TEST_STEP', PDF=pdf)
            Test_Step1 = "Step 1 and 2: The TER NETCONF Client establishes connection and creates an account for new user using o-ran-user9 mgmt.yang"
            STARTUP.STORE_DATA('{}'.format(Test_Step1),Format='TEST_STEP', PDF=pdf)
            STATUS = STARTUP.STATUS(host, USER_N, m.session_id, port)
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

        

            ########################### Merge New User ############################
            snippet = f"""
                    <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                    <users xmlns="urn:o-ran:user-mgmt:1.0">
                        <user>
                            <name>{nam}</name>
                            <account-type>PASSWORD</account-type>
                            <password>{pas1}</password>
                            <enabled>true</enabled>
                        </user>
                    </users>
                    </config>"""

            
            STARTUP.STORE_DATA('> edit-config  --target running --config --defop merge',Format=True, PDF=pdf)
            STARTUP.STORE_DATA('******* Replace with below xml ********',Format=True, PDF=pdf)
            STARTUP.STORE_DATA(snippet,Format='XML', PDF=pdf)
            data1 = m.edit_config(target="running" , config=snippet)
            dict_data1 = xmltodict.parse(str(data1))
            if dict_data1['nc:rpc-reply']['nc:ok']== None:
                STARTUP.STORE_DATA('\nOk\n',Format=True, PDF=pdf)
            

            ########################### Check Notifications ############################
            while True:
                n = m.take_notification(timeout=5)
                if n == None:
                    break
                notify = n.notification_xml
                dict_n = xmltodict.parse(str(notify))
                try:
                    sid = dict_n['notification']['netconf-config-change']['changed-by']['session-id']
                    # STARTUP.STORE_DATA(sid,OUTPUT_LIST=OUTPUT_LIST)
                    if sid == m.session_id:
                        STARTUP.STORE_DATA("******* NOTIFICATIONS *******",Format=True, PDF=pdf)
                        x = xml.dom.minidom.parseString(notify)
                        xml_pretty_str = x.toprettyxml()
                        STARTUP.STORE_DATA(xml_pretty_str,Format='XML', PDF=pdf)
                        break
                except:
                    pass
        
            pdf.add_page()
            ########################### Post Get Filter ############################
            u_name = '''
                    <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                    <users xmlns="urn:o-ran:user-mgmt:1.0">	
                    </users>
                    </filter>
                    '''

            
            user_name = m.get_config('running', u_name).data_xml
            Test_Step2 = "Step 3 and 4: The TER NETCONF Client retrieves a list of users"
            STARTUP.STORE_DATA('{}'.format(Test_Step2),Format='TEST_STEP', PDF=pdf)
            STARTUP.STORE_DATA("> get --filter-xpath /o-ran-usermgmt:users/user",Format=True, PDF=pdf)
            x = xml.dom.minidom.parseString(user_name)
            xml_pretty_str = x.toprettyxml()



            ########## Check whether users are merge ###########
            user_n = xmltodict.parse(str(user_name))
            USERs_info = user_n['data']['users']['user']
            User_list = []
            for user in USERs_info:
                User_list.append(user['name'])
            if  nam not in User_list:
                STARTUP.STORE_DATA(xml_pretty_str,Format='XML', PDF=pdf)
                return "Users didn't merge..."
            else:
                STARTUP.STORE_DATA(xml_pretty_str,Format='XML', PDF=pdf)

            

            ########## Configure New User in NACM ###########
            ad_us = f'<user-name>{nam}</user-name>'
            nacm_file = open('Yang_xml/nacm_sudo.xml').read()
            nacm_file = nacm_file.format(add_sudo = ad_us)
            

            STARTUP.STORE_DATA('> edit-config  --target running --config --defop merge',Format=True, PDF=pdf)
            STARTUP.STORE_DATA('******* Replace with below xml ********',Format=True, PDF=pdf)
            STARTUP.STORE_DATA(nacm_file,Format='XML', PDF=pdf)
            data2 = m.edit_config(target="running" , config=nacm_file, default_operation = 'merge')
            dict_data2 = xmltodict.parse(str(data2))
            if dict_data2['nc:rpc-reply']['nc:ok']== None:
                STARTUP.STORE_DATA('\nOk\n',Format=True, PDF=pdf)

            ########################### Check Notifications ############################
            while True:
                n = m.take_notification(timeout=5)
                if n == None:
                    break
                notify = n.notification_xml
                dict_n = xmltodict.parse(str(notify))
                try:
                    sid = dict_n['notification']['netconf-config-change']['changed-by']['session-id']
                    # STARTUP.STORE_DATA(sid,OUTPUT_LIST=OUTPUT_LIST)
                    if sid == m.session_id:
                        STARTUP.STORE_DATA("******* NOTIFICATIONS *******",Format=True, PDF=pdf)
                        x = xml.dom.minidom.parseString(notify)
                        xml_pretty_str = x.toprettyxml()
                        STARTUP.STORE_DATA(xml_pretty_str,Format='XML', PDF=pdf)
                        break
                except:
                    pass
                
            
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




########################### Call Home With New User ############################
def Call_Home(host,port,name,pas1):
    
    pdf.add_page()
    Test_Step3 = 'Step 5 and 6: NETCONF Server establishes a TCP connection and performs the Call Home procedure to the TER NETCONF Client using the same IP and VLAN.'
    STARTUP.STORE_DATA('{}'.format(Test_Step3),Format='TEST_STEP', PDF=pdf)
    print(name,pas1)
    m1 = manager.call_home(host = '', port=4334, hostkey_verify=False,username = name, password = pas1, timeout = 60, allow_agent = False , look_for_keys = False)
    li = m1._session._transport.sock.getpeername()   #['ip_address', 'TCP_Port']
    LISTEN = f'''> listen --ssh --login {name}
    Waiting 60s for an SSH Call Home connection on port 4334...'''
    STARTUP.STORE_DATA(LISTEN,Format=False, PDF=pdf)

    try:
        if m1:
            query = 'yes'
            Authenticity =f'''The authenticity of the host '::ffff:{li[0]}' cannot be established.
            ssh-rsa key fingerprint is 59:9e:90:48:f1:d7:6e:35:e8:d1:f6:1e:90:aa:a3:83:a0:6b:98:5a.
            Are you sure you want to continue connecting (yes/no)? yes'''
            STARTUP.STORE_DATA(Authenticity,Format=False, PDF=pdf)
            if query == 'yes':
                STARTUP.STORE_DATA(f'''\n{name}@::ffff:{li[0]} password: \n''',Format=False, PDF=pdf)
                Test_Step4 = "Step 7: TER NETCONF Client and O-RU NETCONF Server exchange capabilities through the NETCONF <hello> messages"
                STARTUP.STORE_DATA('{}'.format(Test_Step4),Format='TEST_STEP', PDF=pdf)
                STATUS = f'''
                    > status
                    Current NETCONF session:
                    ID          : {m1.session_id}
                    Host        : ::ffff:{li[0]}
                    Port        : {li[1]}
                    Transport   : SSH
                    Capabilities:
                    '''
                STARTUP.STORE_DATA(STATUS,Format=False, PDF=pdf)
                for i in m1.server_capabilities:
                    STARTUP.STORE_DATA(i,Format=False, PDF=pdf)
                return int(m1.session_id)
        else:
            m1.close()

    except socket.timeout as e:
        STARTUP.STORE_DATA('{}: Call Home is not initiated....'.format(e),Format=False, PDF=pdf)
        return '{}'.format(e)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(f"Error occured in line number {exc_tb.tb_lineno}",Format=False, PDF=pdf)
        STARTUP.STORE_DATA('{}'.format(e),Format=False, PDF=pdf)
        return '{}'.format(e)

        


########################### Main Function ############################
def test_Main_Func_023():
    
    
    try:
        
        USER_N = Config.details['SUDO_USER']
        PSWRD = Config.details['SUDO_PASS']


        m = manager.call_home(host = '', port=4334, hostkey_verify=False,username = USER_N, password = PSWRD, allow_agent = False , look_for_keys = False)
        li = m._session._transport.sock.getpeername()   #['ip_address', 'TCP_Port']
        sid = m.session_id
        STARTUP.kill_ssn(li[0],830, USER_N, PSWRD,sid)
        if m:   
                RU_Details = STARTUP.demo(li[0],830, USER_N, PSWRD)
                for key, val in RU_Details[1].items():
                    if val[0] == 'true' and val[1] == 'true':
                        ############################### Test Description #############################
                        Test_Desc = '''Test Description : This scenario is MANDATORY for an O-RU supporting the Hierarchical M-plane architecture model.
 This test validates that the O-RU can successfully start up with activated software.
 This scenario corresponds to the following chapters in [3]:
 3.3 SSH Connection Establishment
 3.4 NETCONF Access Control
 3.7 closing a NETCONF Session'''
                        CONFIDENTIAL = STARTUP.ADD_CONFIDENTIAL('23', SW_R=val[2])
                        STARTUP.STORE_DATA(CONFIDENTIAL, Format='CONF', PDF=pdf)
                        STARTUP.STORE_DATA(Test_Desc, Format='DESC', PDF=pdf)
                        pdf.add_page()


                

                name = Genrate_User_Pass.genrate_username()
                pas1 = Genrate_User_Pass.genrate_password()
                time.sleep(5)
                res = Create_user(li[0],830,name,pas1,USER_N, PSWRD)
                time.sleep(5)
                

                '''Check First the Output of Create User if user is successfully created then
                it will go for call home with new user otherwise it will go to else condition.'''
                if res == None: 
                    time.sleep(5)
                    ssid = Call_Home(li[0],li[1],name,pas1)
                    ############################### Expected/Actual Result ####################################################
                    STARTUP.GET_SYSTEM_LOGS(li[0], USER_N, PSWRD, pdf)
                    Exp_Result = 'Expected Result : The TER NETCONF Client establishes a Call Home & SSH session towards the NETCONF Server with new user created above.'
                    STARTUP.STORE_DATA(Exp_Result, Format='DESC', PDF=pdf)

                    STARTUP.STORE_DATA('\t\t{}'.format(
                        '****************** Actual Result ******************'), Format=True, PDF=pdf)

                    if type(ssid) == int:
                        STARTUP.kill_ssn(li[0],830, USER_N, PSWRD,str(ssid))
                        time.sleep(10)
                        STARTUP.ACT_RES(f"{'Sudo on Hierarchical M-plane architecture (positive case)' : <50}{'=' : ^20}{'SUCCESS' : ^20}",PDF= pdf,COL=[0,255,0])
                        return True
                    else:
                        STARTUP.kill_ssn(li[0],830, USER_N, PSWRD,ssid)
                        time.sleep(10)
                        STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
                        STARTUP.ACT_RES(f"{'Sudo on Hierarchical M-plane architecture (positive case)' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=[255,0,0])
                        return True
                        


                else:
                    ############################### Expected/Actual Result ####################################################
                    STARTUP.GET_SYSTEM_LOGS(li[0], USER_N, PSWRD, pdf)
                    Exp_Result = 'Expected Result : The TER NETCONF Client establishes a Call Home & SSH session towards the NETCONF Server with new user created above.'
                    STARTUP.STORE_DATA(Exp_Result, Format='DESC', PDF=pdf)

                    STARTUP.STORE_DATA('\t\t{}'.format(
                        '****************** Actual Result ******************'), Format=True, PDF=pdf)

                    if type(res) == list:
                        STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
                        Error_Info = '''ERROR\n\terror-type \t: \t{}\n\terror-tag \t: \t{}\n\terror-severity \t: \t{}\n\tmessage' \t: \t{}'''.format(*map(str,res))
                        STARTUP.STORE_DATA(Error_Info,Format=False,PDF= pdf)
                        STARTUP.ACT_RES(f"{'Sudo on Hierarchical M-plane architecture (positive case)' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=[255,0,0])
                        return Error_Info

                    elif type(res) == str:
                        STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
                        STARTUP.ACT_RES(f"{'Sudo on Hierarchical M-plane architecture (positive case)' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=[255,0,0])
                        # raise '\t\tFAIL-REASON\t\n {}'.format(res)
                        return res
                        
                    else:
                        STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
                        STARTUP.ACT_RES(f"{'Sudo on Hierarchical M-plane architecture (positive case)' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=[255,0,0])
                        # raise '\t\tFAIL-REASON\t\n {}'.format(res)
                        return res
                        
                        
                    
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
        STARTUP.CREATE_LOGS('M_CTC_ID_023',PDF=pdf)


if __name__ == "__main__":
    result = test_Main_Func_023()
    if result == True:
        pass
    else:
        STARTUP.ACT_RES(f"{'Sudo on Hierarchical M-plane architecture (positive case)' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=[255,0,0])

