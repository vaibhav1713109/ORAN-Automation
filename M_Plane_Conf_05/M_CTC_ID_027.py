from logging import exception
import socket
import sys, os, warnings
#warnings.simplefilter("ignore", DeprecationWarning)
from ncclient import manager
from lxml import etree
import xmltodict
import xml.dom.minidom
from ncclient.transport.errors import SSHError
from ncclient.operations.rpc import RPCError
import re
from ncclient.transport import errors
from paramiko.ssh_exception import NoValidConnectionsError
from ncclient.operations.errors import TimeoutExpiredError
from ncclient.transport.errors import SessionCloseError
import lxml.etree
import Config, STARTUP, DHCP_CONF.Genrate_User_Pass as Genrate_User_Pass
import re

pdf = STARTUP.PDF_CAP()





def FETCH_MAC(host, port, user, password):
    with manager.connect(host=host, port=port, username=user, hostkey_verify=False, password=password, allow_agent = False , look_for_keys = False) as m:
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
        
        return ma
    

def session_login(host, port, user, password,ru_mac,du_mac,ip_adr):
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

                
                ########################### Configure Interface Yang ############################
                n = ip_adr[3]
                xml_data = open('Yang_xml/interface.xml').read()
                xml_data = xml_data.format(interface_name= ip_adr,mac = ru_mac, number= n)
                u1 =f'''
                        <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                        {xml_data}
                        </config>'''
                try:
                    Data = m.edit_config(u1, target='running')

                except RPCError as e:
                    STARTUP.STORE_DATA('{0} RPCError {0}'.format('*'*30),Format=False, PDF=pdf)
                    STARTUP.STORE_DATA("\t\t Not able to push interface xml {}".format(e),Format=False, PDF=pdf)
                    return '{}'.format(e)
                

                ########################### Configure Processing Yang ############################
                xml_data1 = open('Yang_xml/processing.xml').read()
                xml_data1 = xml_data1.format(int_name= ip_adr,ru_mac = ru_mac,du_mac = du_mac, element_name= 'element0')
                u2 =f'''
                        <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                        {xml_data1}
                        </config>'''
                try:
                    Data = m.edit_config(u2, target='running')
                except RPCError as e:
                    STARTUP.STORE_DATA('{0} RPCError {0}'.format('*'*30),Format=False, PDF=pdf)
                    STARTUP.STORE_DATA("\t\t Not able to push processing xml {}".format(e),Format=False, PDF=pdf)
                    return '{}'.format(e)
                
                
                pdf.add_page() 
                ########################### Pre get filter ###########################
                STARTUP.STORE_DATA('################# Pre get filter #################',Format=True, PDF=pdf)
                STARTUP.STORE_DATA('>get --filter-xpath /o-ran-uplane-conf:user-plane-configuration',Format=True, PDF=pdf)
                    
                up ='''
                    <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                    <user-plane-configuration xmlns="urn:o-ran:uplane-conf:1.0">
                    </user-plane-configuration>
                    </filter>
                    '''
                Cap = m.get(up).data_xml
                x = xml.dom.minidom.parseString(Cap)
                xml_pretty_str = x.toprettyxml()
                STARTUP.STORE_DATA(xml_pretty_str,Format='XML', PDF=pdf)

                
                ########################### Configure Uplane Yang ###########################  
                pdf.add_page()        
                Test_Step1 = 'STEP 1 The TER NETCONF Client assigns eAxC_IDs to low-level-rx-endpoints. The same eAxC_ID is assigned to more than one low-level-tx-endpoint or/and more than one low-level-rx-endpoint. The NETCONF Client uses <rpc><edit-config>.'
                STARTUP.STORE_DATA('{}'.format(Test_Step1),Format='TEST_STEP', PDF=pdf)
                
                STARTUP.STORE_DATA('> edit-config  --target running --config --defop replace',Format=True, PDF=pdf)
                STARTUP.STORE_DATA('******* Replace with below xml ********',Format=True, PDF=pdf)
                
                xml_1 = open(Config.details['TC_27_xml']).read()
                xml_1 = xml_1.format(element_name= 'element0')
                snippet = f"""
                            <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                            {xml_1}
                            </config>"""
                
                STARTUP.STORE_DATA(snippet,Format='XML', PDF=pdf)

                try:
                    data1 = m.edit_config(target="running", config=snippet, default_operation = 'replace')
                    dict_data1 = xmltodict.parse(str(data1))
                    if dict_data1['nc:rpc-reply']['nc:ok']== None:
                        STARTUP.STORE_DATA('\nOk\n',Format=False, PDF=pdf)
                        return f'\t\t******COnfiguration are pushed********\n {data1}'

                except RPCError as e:
                    if "[operation-not-supported]Duplicate value '1' found for eaxc-id" in e.message:
                        pdf.add_page()
                        ########################### Check Access Denied ###########################              
                        Test_Step2 = 'STEP 2 The O-RU NETCONF Sever responds with the <rpc-reply> message indicating rejection of the requested procedure.'
                        STARTUP.STORE_DATA('{}'.format(Test_Step2),Format='TEST_STEP', PDF=pdf)
                        STARTUP.STORE_DATA('ERROR\n',Format=False, PDF=pdf)
                        STARTUP.STORE_DATA(f"{'type' :^20}{':' : ^10}{e.type: ^10}\n",Format=False, PDF=pdf)
                        STARTUP.STORE_DATA(f"{'tag' : ^20}{':' : ^10}{e.tag: ^10}\n",Format=False, PDF=pdf)
                        STARTUP.STORE_DATA(f"{'severity' : ^20}{':' : ^10}{e.severity: ^10}\n",Format=False, PDF=pdf)
                        STARTUP.STORE_DATA(f"{'path' : ^20}{':' : ^10}{e.path: ^10}\n",Format=False, PDF=pdf)
                        STARTUP.STORE_DATA(f"{'message' : ^20}{':' : ^10}{e.message: ^10}\n",Format=False, PDF=pdf)
                    else:
                        return 'Description : {}'.format(e.message)


    ########################### Known Exceptions ############################
    except RPCError as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        return [e.tag, e.type, e.severity, e.path, e.message, exc_tb.tb_lineno]

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

   

########################### Check MAC is Valid/Not ############################
def isValidMACAddress(str):
 
    # Regex to check valid MAC address
    regex = ("^([0-9A-Fa-f]{2}[:-])" +
             "{5}([0-9A-Fa-f]{2})|" +
             "([0-9a-fA-F]{4}\\." +
             "[0-9a-fA-F]{4}\\." +
             "[0-9a-fA-F]{4})$")
 
    # Compile the ReGex
    p = re.compile(regex)
 
    # If the string is empty
    # return false
    if (str == None):
        return False
 
    # Return if the string
    # matched the ReGex
    if(re.search(p, str)):
        return True
    else:
        return False



########################### Main Function ############################
def test_Main_Func_027():
    

    try:
        
        USER_N = Config.details['SUDO_USER']
        PSWRD = Config.details['SUDO_PASS']
        
        

        m = manager.call_home(host = '', port=4334, hostkey_verify=False,username = USER_N, password = PSWRD, allow_agent = False , look_for_keys = False)
        li = m._session._transport.sock.getpeername()
        sid = m.session_id
        if m:
            STARTUP.kill_ssn(li[0],830, USER_N, PSWRD,sid)
            RU_Details = STARTUP.demo(li[0],830, USER_N, PSWRD)
            for key, val in RU_Details[1].items():
                    if val[0] == 'true' and val[1] == 'true':
                        ############################### Test Description #############################
                        Test_Desc = '''Test Description : This scenario is MANDATORY.
The test scenario is intentionally limited to scope that shall be testable without a need to modify test scenario
according O-RU's hardware design.
This test verifies that the O-RU NETCONF Server supports configurability with validation.
This scenario corresponds to the following chapters in [3]:
6 Configuration Management
12.2 User plane message routing'''
                        CONFIDENTIAL = STARTUP.ADD_CONFIDENTIAL('27', SW_R=val[2])
                        STARTUP.STORE_DATA(CONFIDENTIAL, Format='CONF', PDF=pdf)
                        STARTUP.STORE_DATA(Test_Desc, Format='DESC', PDF=pdf)
                        pdf.add_page()
            
            
            for i in range(5):
                du_mac = Config.details['DU_MAC']
                val = isValidMACAddress(du_mac)
                if val == True:
                    break
                else:
                    STARTUP.STORE_DATA('Please provide valid mac address :\n',Format=False, PDF=pdf)
            
            
            macs = FETCH_MAC(li[0],830, USER_N, PSWRD)
            ip_a = 'eth0'
            mac = macs[ip_a]            
            res = session_login(li[0],830,USER_N, PSWRD,mac,du_mac,ip_a)



            # For Capturing the logs  
            ############################### Expected/Actual Result ####################################################
            STARTUP.GET_SYSTEM_LOGS(li[0], USER_N, PSWRD, pdf)
            Exp_Result = 'Expected Result : The O-RU NETCONF Sever responds with the <rpc-reply> message indicating rejection of the requested procedure'
            STARTUP.STORE_DATA(Exp_Result, Format='DESC', PDF=pdf)

            STARTUP.STORE_DATA('\t\t{}'.format(
                '****************** Actual Result ******************'), Format=True, PDF=pdf)

            if res:  
                if type(res) == list:
                    STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
                    Error_Info = '''ERROR\n\terror-type \t: \t{}\n\terror-tag \t: \t{}\n\terror-severity \t: \t{}\n\tpath \t: \t{}\n\tDescription' \t: \t{}'''.format(*map(str,res))
                    STARTUP.STORE_DATA(Error_Info,Format=False,PDF= pdf)
                    STARTUP.ACT_RES(f"{'O-RU Configurability Test (negative case)' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=[255,0,0])
                    return Error_Info
                    # raise '\t\tFAIL-REASON\t\n{}'.format(Error_Info)
                else:
                    STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
                    # raise '\t\tFAIL-REASON\t\n {}'.format(res)
                STARTUP.ACT_RES(f"{'O-RU Configurability Test (negative case)' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=[255,0,0])
                return res

            else: 
                STARTUP.ACT_RES(f"{'O-RU Configurability Test (negative case)' : <50}{'=' : ^20}{'SUCCESS' : ^20}",PDF= pdf,COL=[0,255,0])
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

    # except Exception as e:
    #     STARTUP.STORE_DATA('{}'.format(e), Format=True,PDF=pdf)
    #     exc_type, exc_obj, exc_tb = sys.exc_info()
    #     STARTUP.STORE_DATA(
    #         f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
    #     return e
        # raise Exception('{}'.format(e)) from None



    ############################### MAKE PDF File ####################################################
    finally:
        STARTUP.CREATE_LOGS('M_CTC_ID_027',PDF=pdf)


if __name__ == "__main__":
    test_Main_Func_027()
