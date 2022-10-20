import socket
import sys, os, warnings
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
import lxml.etree
import Config,STARTUP, DHCP_CONF.Genrate_User_Pass as Genrate_User_Pass

pdf = STARTUP.PDF_CAP()

def FETCH_DATA(host, port, user, password):
    with manager.connect(host=host, port=port, username=user, hostkey_verify=False, password=password, allow_agent = False , look_for_keys = False) as m:
        
        
        # Fetching all the users
        u_name = '''
        <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            <users xmlns="urn:o-ran:user-mgmt:1.0">	
            </users>
        </filter>'''


        get_u = m.get(u_name).data_xml
        dict_u = xmltodict.parse(str(get_u))
        #STARTUP.STORE_DATA(user_name,OUTPUT_LIST=OUTPUT_LIST)
        s = xml.dom.minidom.parseString(get_u)
        #xml = xml.dom.minidom.parseString(user_name)

        xml_pretty_str = s.toprettyxml()

        
        # Fetching all the interface
        v_name1 = '''
                <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
                </interfaces>
                </filter>
        '''

        interface_name = m.get_config('running', v_name1).data_xml
        dict_interface = xmltodict.parse(str(interface_name))
        Interfaces = dict_interface['data']['interfaces']['interface']
        #STARTUP.STORE_DATA(Interfaces,OUTPUT_LIST=OUTPUT_LIST)
        d = {}
        ma = {}

        
        for i in Interfaces:
            name = i['name']
            mac = i['mac-address']['#text']
            try:
                IP_ADD = i['ipv4']['address']['ip']
                if name:
                    d[name] = IP_ADD
                    ma[name] = mac
            except:
                pass

        
        return ma, xml_pretty_str
        

def session_login(host,port,name,pas1,USER_N, PSWRD):
    try:
        with manager.connect(host=host, port=port, username=USER_N, hostkey_verify=False, password=PSWRD, allow_agent = False , look_for_keys = False) as m:    
            STARTUP.STORE_DATA(
                '\t\t********** Connect to the NETCONF Server ***********', Format='TEST_STEP', PDF=pdf)
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
            

            pdf.add_page()
            ########################### Initial Get Filter ############################
            u_name = '''
                    <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                    <users xmlns="urn:o-ran:user-mgmt:1.0">	
                    </users>
                    </filter>
                    '''

            
            user_name = m.get_config('running', u_name).data_xml
            STARTUP.STORE_DATA("######### Initial Get Filter #########",Format=True, PDF=pdf)
            STARTUP.STORE_DATA("> get --filter-xpath /o-ran-usermgmt:users/user",Format=True, PDF=pdf)
            x = xml.dom.minidom.parseString(user_name)
            xml_pretty_str = x.toprettyxml()
            STARTUP.STORE_DATA(xml_pretty_str,Format='XML', PDF=pdf)



            ########################### Merge New User ############################
            snippet = f"""
                    <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                    <users xmlns="urn:o-ran:user-mgmt:1.0">
                        <user>
                            <name>{name}</name>
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
                STARTUP.STORE_DATA('\n{}\n'.format('-'*100),Format=False, PDF=pdf)
                STARTUP.STORE_DATA('Ok\n',Format=False, PDF=pdf)
                STARTUP.STORE_DATA('{}'.format('-'*100),Format=False, PDF=pdf)



            ########################### Check_Notifications ############################
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
            ########################### Configure New User In NACM ############################
            ad_us = f'<user-name>{name}</user-name>'
            nacm_file = open('Yang_xml/nacm_swm.xml').read()
            nacm_file = nacm_file.format(add_swm = ad_us)
            
            STARTUP.STORE_DATA('> edit-config  --target running --config --defop merge',Format=True, PDF=pdf)
            STARTUP.STORE_DATA('******* Replace with below xml ********',Format=True, PDF=pdf)
            STARTUP.STORE_DATA(nacm_file,Format='XML', PDF=pdf)
        
            data2 = m.edit_config(target="running" , config=nacm_file, default_operation = 'merge')
            dict_data2 = xmltodict.parse(str(data2))
            if dict_data2['nc:rpc-reply']['nc:ok']== None:
                STARTUP.STORE_DATA('\n{}\n'.format('-'*100),Format=False, PDF=pdf)
                STARTUP.STORE_DATA('Ok\n',Format=False, PDF=pdf)
                STARTUP.STORE_DATA('{}'.format('-'*100),Format=False, PDF=pdf)

            ########################### Check_Notifications ############################
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
                        pdf.add_page()
                        STARTUP.STORE_DATA("******* NOTIFICATIONS *******",Format=True, PDF=pdf)
                        x = xml.dom.minidom.parseString(notify)
                        xml_pretty_str = x.toprettyxml()
                        STARTUP.STORE_DATA(xml_pretty_str,Format='XML', PDF=pdf)
                        break
                except:
                    pass
            
            STARTUP.STORE_DATA("> get --filter-xpath /ietf-netconf-acm:nacm/groups",Format=True, PDF=pdf)
            u_name = '''
                <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <nacm xmlns="urn:ietf:params:xml:ns:yang:ietf-netconf-acm">
                    <groups>
                    </groups>
                </nacm>
                </filter>
                '''
            user_name = m.get_config('running', u_name).data_xml
            #STARTUP.STORE_DATA(user_name,OUTPUT_LIST=OUTPUT_LIST)
            s = xml.dom.minidom.parseString(user_name)
            #xml = xml.dom.minidom.parseString(user_name)

            xml_pretty_str = s.toprettyxml()

            ################# Check whether users add in nacm or not #################
            # group_n = xmltodict.parse(str(user_name))
            # group_name = group_n['data']['nacm']['groups']['group']
            # for i in group_name:
            #     STARTUP.STORE_DATA(i['name'],Format=False, PDF=pdf)
            #     if i['name'] == 'swm':
            #         if name not in i['user-name']:
            #             STARTUP.STORE_DATA(xml_pretty_str,Format='XML', PDF=pdf)
            #             return "User didn't merge in 'nms' privilege"
            #     else:
            #         return "User didn't merge in except these privilege ['sudo', 'fm-pm', 'nms', 'swm'] privilege"

            STARTUP.STORE_DATA(xml_pretty_str,Format='XML', PDF=pdf)
        
            pdf.add_page()
            ########################### Get Filter of NACM ############################
            u_name = '''
                    <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                    <users xmlns="urn:o-ran:user-mgmt:1.0">	
                    </users>
                    </filter>
                    '''
            user_name = m.get_config('running', u_name).data_xml
            STARTUP.STORE_DATA("> get --filter-xpath /o-ran-usermgmt:users/user",Format=True, PDF=pdf)
            s = xml.dom.minidom.parseString(user_name)
            xml_pretty_str = s.toprettyxml()
            
            ########## Check whether users are merge ###########
            user_n = xmltodict.parse(str(user_name))
            USERs_info = user_n['data']['users']['user']
            User_list = []
            for user in USERs_info:
                User_list.append(user['name'])
            if  name not in User_list:
                STARTUP.STORE_DATA(xml_pretty_str,Format='XML', PDF=pdf)
                return "Users didn't merge..."
            else:
                STARTUP.STORE_DATA(xml_pretty_str,Format='XML', PDF=pdf)


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



    ########################### Login With New User ############################
    try:
        with manager.connect(host=host, port=port, username=name, hostkey_verify=False, password=pas1, allow_agent = False , look_for_keys = False) as ms:
            
            ########################### Try to Configure Processing Yang ############################
            pdf.add_page()
            Test_Step1 = 'STEP 1 TER NETCONF client establishes a connection using a user account with swm privileges.'
            STARTUP.STORE_DATA('{}'.format(Test_Step1),Format='TEST_STEP', PDF=pdf)
            STARTUP.STORE_DATA(
                '\t\t********** Connect to the NETCONF Server ***********', Format='TEST_STEP', PDF=pdf)
            cmd = f'''
            > connect --ssh --host {host} --port 830 --login {name}
            Interactive SSH Authentication
            Type your password:
            Password: 
            '''
            STARTUP.STORE_DATA(cmd,Format=False, PDF=pdf)          
            proc_xml = open('Yang_xml/sync.xml').read()  
            Test_Step2 = 'Step 2 TER NETCONF client attempts to configure a new o-ran-sync.yang on the NETCONF server.'
            STARTUP.STORE_DATA("{}".format(Test_Step2), Format='TEST_STEP', PDF=pdf)
            pro = f'''
            <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                {proc_xml}
            </config>
            '''
            STARTUP.STORE_DATA('> edit-config  --target running --config --defop replace',Format=True, PDF=pdf)
            STARTUP.STORE_DATA('******* Replace with below xml ********',Format=True, PDF=pdf)

            STARTUP.STORE_DATA(proc_xml,Format='XML', PDF=pdf)



            try:
                data3 = ms.edit_config(target="running" , config=pro, default_operation = 'replace')
                if data3:
                    return f'\t*******Configuration are pushed*******\n{data3}'
            except RPCError as e:

                ########################### Check Access Denied ############################
                if e.tag == 'access-denied':
                    Test_Step4 = 'Step 3 NETCONF server replies rejecting the protocol operation with an \'access-denied\' error.'
                    STARTUP.STORE_DATA('{}'.format(Test_Step4),Format='TEST_STEP', PDF=pdf)
                    STARTUP.STORE_DATA('ERROR\n',Format=False, PDF=pdf)
                    STARTUP.STORE_DATA(f"{'type' : ^20}{':' : ^10}{e.tag: ^10}\n",Format=False, PDF=pdf)
                    STARTUP.STORE_DATA(f"{'tag' : ^20}{':' : ^10}{e.type: ^10}\n",Format=False, PDF=pdf)
                    STARTUP.STORE_DATA(f"{'severity' : ^20}{':' : ^10}{e.severity: ^10}\n",Format=False, PDF=pdf)
                    STARTUP.STORE_DATA(f"{'path' : ^20}{':' : ^10}{e.path: ^10}\n",Format=False, PDF=pdf)
                    STARTUP.STORE_DATA(f"{'message' : ^20}{':' : ^10}{e.message: ^10}\n",Format=False, PDF=pdf)

                else:
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
def test_Main_Func_022():
    
    
    try:
        USER_N = Config.details['SUDO_USER']
        PSWRD = Config.details['SUDO_PASS']

        m = manager.call_home(host = '', port=4334, hostkey_verify=False,username = USER_N, password = PSWRD, allow_agent = False , look_for_keys = False)
        li = m._session._transport.sock.getpeername()   #['ip_address', 'TCP_Port']
        sid = m.session_id
        if m:
            STARTUP.kill_ssn(li[0],830, USER_N, PSWRD,sid)
            RU_Details = STARTUP.demo(li[0],830,  USER_N, PSWRD)
            for key, val in RU_Details[1].items():
                    if val[0] == 'true' and val[1] == 'true':
                        ############################### Test Description #############################
                        Test_Desc = '''Test Description : This scenario is MANDATORY for an O-RU supporting the Hybrid M-plane architecture model.
 This test validates that the O-RU correctly implements NETCONF Access Control user privileges.
 The scenario corresponds to the following chapters in [3]:
 3.4 NETCONF Access Control'''
                        CONFIDENTIAL = STARTUP.ADD_CONFIDENTIAL('22', SW_R=val[2])
                        STARTUP.STORE_DATA(CONFIDENTIAL, Format='CONF', PDF=pdf)
                        STARTUP.STORE_DATA(Test_Desc, Format='DESC', PDF=pdf)
                        pdf.add_page()


            
            name = Genrate_User_Pass.genrate_username()
            pas1 = Genrate_User_Pass.genrate_password()
            time.sleep(5)
            res = session_login(li[0],830,name,pas1,USER_N, PSWRD)
            time.sleep(5)


            
            ############################### Expected/Actual Result ####################################################
            STARTUP.GET_SYSTEM_LOGS(li[0], USER_N, PSWRD, pdf)
            Exp_Result = 'Expected Result : The NETCONF server replies rejecting the protocol operation with an "access-denied" error.'
            STARTUP.STORE_DATA(Exp_Result, Format='DESC', PDF=pdf)

            STARTUP.STORE_DATA('\t\t{}'.format(
                '****************** Actual Result ******************'), Format=True, PDF=pdf)


            if res:
                if type(res) == list:
                    STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
                    Error_Info = '''ERROR\n\terror-type \t: \t{}\n\terror-tag \t: \t{}\n\terror-severity \t: \t{}\n\tmessage' \t: \t{}'''.format(*map(str,res))
                    STARTUP.STORE_DATA(Error_Info,Format=False,PDF= pdf)
                    STARTUP.ACT_RES(f"{'Access Control SWM (negative case)' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=[255,0,0])
                    return Error_Info
                else:
                    STARTUP.STORE_DATA(f"{'REJECT-REASON' : <15}{'=' : ^20}{res : ^20}",Format=True,PDF= pdf)
                    STARTUP.ACT_RES(f"{'Access Control SWM (negative case)' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=[255,0,0])
                    return res
                    # raise '\t\tFAIL-REASON\t\n {}'.format(res)

                
            else:
                STARTUP.ACT_RES(f"{'Access Control SWM (negative case)' : <50}{'=' : ^20}{'SUCCESS' : ^20}",PDF= pdf,COL=[0,255,0])
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
        STARTUP.CREATE_LOGS('M_CTC_ID_022',PDF=pdf)


if __name__ == "__main__":
    result = test_Main_Func_022()
    if result == True:
        pass
    else:
        STARTUP.ACT_RES(f"{'Access Control SWM (negative case)' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(255,0,0))

