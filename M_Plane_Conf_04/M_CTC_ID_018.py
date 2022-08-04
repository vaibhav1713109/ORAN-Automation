import socket
import sys
import os
import warnings
import time
from ncclient import manager
import string
from ncclient.operations.rpc import RPCError
from ncclient.transport.errors import SSHError
import paramiko
import xmltodict
from paramiko.ssh_exception import NoValidConnectionsError
from ncclient.operations.errors import TimeoutExpiredError
from ncclient.transport.errors import SessionCloseError
import lxml.etree
import xml.dom.minidom
from ncclient.transport import errors
import STARTUP
import Config
import DHCP_CONF.Genrate_User_Pass as Genrate_User_Pass


pdf = STARTUP.PDF_CAP()


def session_login(host, port, user, pswrd):
    try:
        with manager.connect(host=host, port=port, username=user, hostkey_verify=False, password=pswrd, allow_agent=False, look_for_keys=False) as m:
            Test_Step1 = 'STEP 1. The TER NETCONF Client establishes a connection with the O-RU NETCONF Server.'
            STARTUP.STORE_DATA("{}".format(Test_Step1), Format='TEST_STEP', PDF=pdf)
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
            u_name = '''
                    <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                    <users xmlns="urn:o-ran:user-mgmt:1.0">	
                    </users>
                    </filter>
                    '''

            user_name = m.get(u_name).data_xml
            STARTUP.STORE_DATA(
                "######### Initial Get #########", Format=True, PDF=pdf)
            STARTUP.STORE_DATA("> get --filter-xpath /o-ran-usermgmt:users/user", Format=True, PDF=pdf)
            x = xml.dom.minidom.parseString(user_name)
            xml_pretty_str = x.toprettyxml()
            STARTUP.STORE_DATA(xml_pretty_str, Format='XML', PDF=pdf)
            Test_Step2 = 'STEP 2. The TER NETCONF Client configures three new user accounts in addition to the default sudo account already present and passwords these three accounts using o-ran-user.mgmt.yang'
            STARTUP.STORE_DATA('{}'.format(Test_Step2),Format='TEST_STEP', PDF=pdf)

            
            ########################### Genrate Random Username & Password with ORAN credential ############################
            usrs = {}
            for i in range(1, 4):

                nam = Genrate_User_Pass.genrate_username()
                pas = Genrate_User_Pass.genrate_password()
                usrs[nam] = pas
            added_users = list(usrs.items())
            snippet = f"""
                    <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                    <users xmlns="urn:o-ran:user-mgmt:1.0">
                        <user>
                            <name>{added_users[0][0]}</name>
                            <account-type>PASSWORD</account-type>
                            <password>{added_users[0][1]}</password>
                            <enabled>true</enabled>
                        </user>
                        <user>
                            <name>{added_users[1][0]}</name>
                            <account-type>PASSWORD</account-type>
                            <password>{added_users[1][1]}</password>
                            <enabled>true</enabled>
                        </user>
                        <user>
                            <name>{added_users[2][0]}</name>
                            <account-type>PASSWORD</account-type>
                            <password>{added_users[2][1]}</password>
                            <enabled>true</enabled>
                        </user>
                    </users>
                    </config>"""

            ########################### Merge 3 Users ############################
            STARTUP.STORE_DATA('> edit-config  --target running --config --defop merge', Format=True, PDF=pdf)
            STARTUP.STORE_DATA('******* Replace with below xml ********', Format=True, PDF=pdf)
            STARTUP.STORE_DATA(snippet, Format='XML', PDF=pdf)
            data1 = m.edit_config(target="running", config=snippet)
            dict_data1 = xmltodict.parse(str(data1))
            STARTUP.STORE_DATA('''######### RPC Reply #########''', Format=True, PDF=pdf)
            if dict_data1['nc:rpc-reply']['nc:ok'] == None:
                STARTUP.STORE_DATA('\nOk\n', Format=False, PDF=pdf)

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
                        STARTUP.STORE_DATA(" ############# NOTIFICATIONS #############", Format=True, PDF=pdf)
                        x = xml.dom.minidom.parseString(notify)
                        xml_pretty_str = x.toprettyxml()
                        STARTUP.STORE_DATA(xml_pretty_str, Format='XML', PDF=pdf)
                        break
                except:
                    pass


            ########################### Give Configured 3 users diffrent privilege ############################
            pdf.add_page()
            Test_Step3 = '''######### STEP 3. The TER NETCONF Client configures user account to group mappings for the three
            new accounts using ietf-netconf-acm.yang respectively one with "nms", one with "fm-pm" and one 
            with "swm" privilege. #########'''
            STARTUP.STORE_DATA('{}'.format(Test_Step3),Format='TEST_STEP', PDF=pdf)
            STARTUP.STORE_DATA('> edit-config  --target running --config --defop merge', Format=True, PDF=pdf)
            STARTUP.STORE_DATA('******* Replace with below xml ********', Format=True, PDF=pdf)

            add_fm = f'<user-name>{added_users[0][0]}</user-name>'
            add_nms = f'<user-name>{added_users[1][0]}</user-name>'
            add_swm = f'<user-name>{added_users[2][0]}</user-name>'

            nacm_file = open('Yang_xml/M_CTC_ID_18.xml').read()
            nacm_file = nacm_file.format(
                add_swm=add_swm, add_fm=add_fm, add_nms=add_nms)
            STARTUP.STORE_DATA(nacm_file, Format='XML', PDF=pdf)
            data2 = m.edit_config(
                target="running", config=nacm_file, default_operation='merge')
            dict_data2 = xmltodict.parse(str(data2))


            ########################### Check the RPC Reply ############################
            Test_Step4 = 'STEP 4. The O-RU NETCONF Server confirms the operations for the above transactions.'
            STARTUP.STORE_DATA(
                '{}'.format(Test_Step4), Format='TEST_STEP', PDF=pdf)
            if dict_data2['nc:rpc-reply']['nc:ok'] == None:
                STARTUP.STORE_DATA('\nOk\n', Format=False, PDF=pdf)


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
                        STARTUP.STORE_DATA(" ############# NOTIFICATIONS #############", Format=True, PDF=pdf)
                        x = xml.dom.minidom.parseString(notify)
                        xml_pretty_str = x.toprettyxml()
                        STARTUP.STORE_DATA(
                            xml_pretty_str, Format='XML', PDF=pdf)
                        break
                except:
                    pass


            ########################### Post Get Filter of NACM ############################    
            STARTUP.STORE_DATA("> get --filter-xpath /ietf-netconf-acm:nacm/groups", Format=True, PDF=pdf)
            u_name = '''
                <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <nacm xmlns="urn:ietf:params:xml:ns:yang:ietf-netconf-acm">
                    <groups>
                    </groups>
                </nacm>
                </filter>
                '''
            user_name = m.get_config('running', u_name).data_xml
            s = xml.dom.minidom.parseString(user_name)
            xml_pretty_str = s.toprettyxml()



            ################# Check whether users add in nacm or not #################
            ADDED_USERS = list(usrs.keys())
            group_n = xmltodict.parse(str(user_name))
            group_name = group_n['data']['nacm']['groups']['group']
            j = 0
            for i in group_name:
                if i['name'] == 'sudo':
                    pass
                elif i['name'] in ['fm-pm', 'nms', 'swm']:
                    if ADDED_USERS[j] not in i['user-name']:
                        STARTUP.STORE_DATA(
                            xml_pretty_str, Format='XML', PDF=pdf)
                        return f"User didn't merge in {i['name']} privilege"
                    j += 1
                    added_users[True]
                else:
                    STARTUP.STORE_DATA(xml_pretty_str, Format='XML', PDF=pdf)
                    return "User didn't merge in except these privilege ['sudo', 'fm-pm', 'nms', 'swm'] privilege"

            STARTUP.STORE_DATA(xml_pretty_str, Format='XML', PDF=pdf)


            ########################### Post Get Filter of USERS ############################    
            Test_Step5 = 'STEP 5. The TER NETCONF Client retrieves a list of users from O-RU NETCONF Server. The newly created user accounts and mappings are validated.'
            STARTUP.STORE_DATA(
                '{}'.format(Test_Step5), Format='TEST_STEP', PDF=pdf)
            u_name = '''
                    <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                    <users xmlns="urn:o-ran:user-mgmt:1.0">	
                    </users>
                    </filter>
                    '''
            user_name = m.get_config('running', u_name).data_xml

            STARTUP.STORE_DATA("> get --filter-xpath /o-ran-usermgmt:users/user", Format=True, PDF=pdf)
            s = xml.dom.minidom.parseString(user_name)
            xml_pretty_str = s.toprettyxml()



            ########## Check whether users are merge ###########
            user_n = xmltodict.parse(str(user_name))
            USERs_info = user_n['data']['users']['user']
            ADDED_USERS_R = ADDED_USERS[::-1]  # Reeverse of added_users
            LIST_User = []
            for _ in range(3):
                user1 = USERs_info.pop()
                LIST_User.append(user1['name'])

            if LIST_User != ADDED_USERS_R:
                STARTUP.STORE_DATA(xml_pretty_str, Format='XML', PDF=pdf)
                return "Users didn't merge..."
            else:
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
def test_MAIN_FUNC_018():
    try:
        USER_N = Config.details['SUDO_USER']
        PSWRD = Config.details['SUDO_PASS']


        ############################### Perform Call Home to get IP #######################################
        m = manager.call_home(host='192.168.4.15', port=4334, hostkey_verify=False,
                              username=USER_N, password=PSWRD, timeout=60,allow_agent=False, look_for_keys=False)
        li = m._session._transport.sock.getpeername()
        sid = m.session_id
        if m:
            STARTUP.kill_ssn(li[0], 830, USER_N, PSWRD, sid)
            time.sleep(10)
            RU_Details = STARTUP.demo(li[0], 830, USER_N, PSWRD)

            for key, val in RU_Details[1].items():
                if val[0] == 'true' and val[1] == 'true':
                    ############################### Test Description #############################
                    Test_Desc = '''Test Description : This scenario is MANDATORY for an O-RU supporting the Hybrid M-plane architecture model.
                    This test validates that user management model can be used to add users to the O-RU
                    This scenario corresponds to the following chapters in [3]:
                    3.3 SSH Connection Establishment
                    3.4 NETCONF Access Control'''
                    CONFIDENTIAL = STARTUP.ADD_CONFIDENTIAL('18', SW_R=val[2])
                    STARTUP.STORE_DATA(CONFIDENTIAL, Format='CONF', PDF=pdf)
                    STARTUP.STORE_DATA(Test_Desc, Format='DESC', PDF=pdf)
                    pdf.add_page()
        


            time.sleep(5)
            res = session_login(li[0], 830, USER_N, PSWRD)
            time.sleep(5)
            ############################### Expected/Actual Result ####################################################
            STARTUP.GET_SYSTEM_LOGS(li[0], USER_N, PSWRD, pdf)
            Exp_Result = 'Expected Result : The TER NETCONF Client retrieves a list of users from O-RU NETCONF Server. The newly created user accounts and mappings are validated.'
            STARTUP.STORE_DATA(Exp_Result, Format='DESC', PDF=pdf)

            STARTUP.STORE_DATA('\t\t{}'.format(
                '****************** Actual Result ******************'), Format=True, PDF=pdf)

            if res == None:
                STARTUP.ACT_RES(f"{'Sudo on Hybrid M-plane Architecture (positive case)' : <50}{'=' : ^20}{'SUCCESS' : ^20}",PDF= pdf,COL=(0,255,0))
                return True

            elif type(res) == list:
                STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
                Error_Info = '''ERROR\n\terror-type \t: \t{}\n\terror-tag \t: \t{}\n\terror-severity \t: \t{}\n\tmessage' \t: \t{}'''.format(*map(str,res))
                STARTUP.STORE_DATA(Error_Info,Format=False,PDF= pdf)
                STARTUP.ACT_RES(f"{'Sudo on Hybrid M-plane Architecture (positive case)' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(255,0,0))
                return Error_Info

            elif type(res) == str:
                STARTUP.STORE_DATA(f"{'REJECT-REASON' : <15}{'=' : ^20}{res : ^20}",Format=True,PDF= pdf)
                # raise '\t\tFAIL-REASON\t\n {}'.format(res)
                STARTUP.ACT_RES(f"{'Sudo on Hybrid M-plane Architecture (positive case)' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(255,0,0))
                return res

            else:
                STARTUP.STORE_DATA(f"{'REJECT-REASON' : <15}{'=' : ^20}{res : ^20}",Format=True,PDF= pdf)
                # raise '\t\tFAIL-REASON\t\n {}'.format(res)
                STARTUP.ACT_RES(f"{'Sudo on Hybrid M-plane Architecture (positive case)' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(255,0,0))
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
        STARTUP.CREATE_LOGS('M_CTC_ID_018', PDF=pdf)


if __name__ == "__main__":
    result = test_MAIN_FUNC_018()
    if result == True:
        pass
    else:
        STARTUP.ACT_RES(f"{'Sudo on Hybrid M-plane Architecture (positive case)' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(255,0,0))
        raise Exception(''.format(result)) from None

