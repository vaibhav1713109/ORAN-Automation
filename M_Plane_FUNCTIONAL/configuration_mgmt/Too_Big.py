###############################################################################
## Package Imports 
###############################################################################

import sys, os, time, xmltodict, xml.dom.minidom, socket
from ncclient import manager
from ncclient.operations.rpc import RPC, RPCError
from ncclient.transport import errors
from paramiko.ssh_exception import NoValidConnectionsError
from ncclient.operations.errors import TimeoutExpiredError
from ncclient.transport.errors import SessionCloseError
from ncclient.xml_ import to_ele
from configparser import ConfigParser

###############################################################################
## Directory Path
###############################################################################
dir_name = os.path.dirname(os.path.abspath(__file__))
parent = (os.path.dirname(dir_name))
print(dir_name)
sys.path.append(parent)


########################################################################
## For reading data from .ini file
########################################################################
configur = ConfigParser()
configur.read('{}/inputs.ini'.format(dir_name))

###############################################################################
## Related Imports
###############################################################################
from require.Vlan_Creation import *
from require import STARTUP, Config
from require.Genrate_User_Pass import *


###############################################################################
## Initiate PDF
###############################################################################
pdf = STARTUP.PDF_CAP()

class M_CTC_ID_020(vlan_Creation):
    # init method or constructor 
    def __init__(self):
        super().__init__()
        self.hostname, self.call_home_port = '',''
        self.USER_N = ''
        self.PSWRD = ''
        self.session = ''
        self.RU_Details = ''


    ###############################################################################
    ## Login with sudo user for getting user details
    ###############################################################################
    def FETCH_DATA(self):
        # Fetching all the interface
        with manager.connect(host=self.hostname, port=830, username=self.USER_N, hostkey_verify=False, password=self.PSWRD, allow_agent=False, look_for_keys=False) as session:
            u_name = '''
            <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <users xmlns="urn:o-ran:user-mgmt:1.0">	
                </users>
            </filter>'''

            get_u = session.get(u_name).data_xml
            dict_u = xmltodict.parse(str(get_u))
            # STARTUP.STORE_DATA(user_name,OUTPUT_LIST=OUTPUT_LIST)
            s = xml.dom.minidom.parseString(get_u)
            #xml = xml.dom.minidom.parseString(user_name)

            xml_pretty_str = s.toprettyxml()
            # session.close_session()
            return xml_pretty_str


    ###############################################################################
    ## Test Procedure
    ###############################################################################
    def test_procedure(self):
        ###############################################################################
        ## Test Procedure 1 : Connect to netopeer server 
        ###############################################################################
        STARTUP.STORE_DATA(
            '\t\t********** Connect to the NETCONF Server ***********', Format='TEST_STEP', PDF=pdf)
        
        # Test_Step1 = 'STEP 1 1. Using the "edit-config" cli use the o-ran-usermgmt.yang Module format.'
        STARTUP.STORE_DATA('\n\n\t\t********** Connect to the NETCONF Server ***********\n\n',Format='TEST_STEP',PDF = pdf)
        STATUS = STARTUP.STATUS(self.hostname,self.USER_N,self.session.session_id,830)
        STARTUP.STORE_DATA(STATUS,Format=False,PDF = pdf)


        ###############################################################################
        ## Server Capabilities
        ###############################################################################
        for cap in self.session.server_capabilities:
            STARTUP.STORE_DATA("\t{}".format(cap),Format=False,PDF = pdf)
            
        ###############################################################################
        ## Create_subscription
        ###############################################################################
        cap=self.session.create_subscription()
        STARTUP.STORE_DATA('> subscribe', Format=True, PDF=pdf)
        dict_data = xmltodict.parse(str(cap))
        if dict_data['nc:rpc-reply']['nc:ok'] == None:
            STARTUP.STORE_DATA('\nOk\n', Format=False, PDF=pdf)
        


        ###############################################################################
        ## Test Procedure 2 : Configure new user\password.
        ###############################################################################
        pdf.add_page()
        Test_Step2 = '''Test Procedure : Verify using "edit-config" add any argument in a leaf more than the limit
'''
        
        STARTUP.STORE_DATA('{}'.format(Test_Step2), Format='TEST_STEP', PDF=pdf)
        xml_data = open("{}/require/Yang_xml/M_FTC_ID_054.xml".format(parent)).read()
        u1 =f'''
                <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                {xml_data}
                </config>'''
        STARTUP.STORE_DATA('> edit-config  --target running --config --defop merge', Format=True, PDF=pdf)
        STARTUP.STORE_DATA('******* Replace with below xml ********', Format=True, PDF=pdf)


        STARTUP.STORE_DATA(xml_data, Format='XML',PDF=pdf)

        try:
            rpc_reply = self.session.edit_config(target='running',config=u1)    
            dict_data = xmltodict.parse(str(rpc_reply))   
            STARTUP.STORE_DATA(rpc_reply, Format='XML',PDF=pdf) 
            return 'RPC is configured..'
            
        except RPCError as e:
            if '[too-big/too-small]' in e.message:
                
                Test_Step3 = 'RPC Reply'
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
                return True
            else:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                return [e.type, e.tag, e.severity, e.path, e.message, exc_tb.tb_lineno]

        


    ###############################################################################
    ## Main Function
    ###############################################################################
    def test_Main_020(self):
        
        Check1 = self.linked_detected()
        
        
        ###############################################################################
        ## Read User Name and password from Config.INI of Config.py
        ############################################################################### 
        self.USER_N = configur.get('INFO','sudo_user')
        self.PSWRD = configur.get('INFO','sudo_pass')
        if Check1 == False or Check1 == None:
            return Check1
        
        sniff(iface = self.interface, stop_filter = self.check_tcp_ip, timeout = 100)
        try:
            STARTUP.delete_system_log(host= self.hostname)
            time.sleep(2)
            ###############################################################################
            ## Perform call home to get ip_details
            ###############################################################################
            self.session = STARTUP.call_home(host = '0.0.0.0', port=4334, hostkey_verify=False,username = self.USER_N, password = self.PSWRD,timeout = 60,allow_agent = False , look_for_keys = False)
            self.hostname, self.call_home_port = self.session._session._transport.sock.getpeername()   #['ip_address', 'TCP_Port']
            
            if self.session:
                self.RU_Details = STARTUP.demo(session = self.session)

                for key, val in self.RU_Details[1].items():
                    if val[0] == 'true' and val[1] == 'true':
                        ###############################################################################
                        ## Test Description
                        ###############################################################################
                        Test_Desc = 'Test Description : Test to verify whether from the NETCONF Error List with tag too-big.'
                        CONFIDENTIAL = STARTUP.ADD_CONFIDENTIAL(filename, SW_R=val[2])
                        STARTUP.STORE_DATA(CONFIDENTIAL, Format='CONF', PDF=pdf)
                        STARTUP.STORE_DATA(Test_Desc, Format='DESC', PDF=pdf)
                        

                
                pdf.add_page()
                
                time.sleep(5)
                result = self.test_procedure()
                time.sleep(5)
                # self.session.close_session()
                if result == True:
                    return True
                else:
                    return result


        ###############################################################################
        ## Exception
        ###############################################################################
        except socket.timeout as e:
            Error = '{} : Call Home is not initiated, SSH Socket connection lost....'.format(
                e)
            STARTUP.STORE_DATA(Error, Format=True,PDF=pdf)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
            return Error
            
        except RPCError as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
            # self.session.close_session()
            return [e.type, e.tag, e.severity, e.path, e.message, exc_tb.tb_lineno]

        except Exception as e:
            STARTUP.STORE_DATA('{}'.format(e), Format=True,PDF=pdf)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
            # self.session.close_session()
            return e    

        finally:
            try:
                self.session.close_session()
            except Exception as e:
                print(e) 


def test_m_ctc_id_020():
    tc020_obj = M_CTC_ID_020()
    Check = tc020_obj.test_Main_020()
    if Check == False:
        STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
        STARTUP.STORE_DATA('SFP link not detected...',Format=False,PDF= pdf)
        STARTUP.ACT_RES(f"{'User Account Provisioning ' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(255,0,0))
        return False
    ###############################################################################
    ## Expected/Actual Result
    ###############################################################################
    STARTUP.GET_SYSTEM_LOGS(tc020_obj.hostname,tc020_obj.USER_N,tc020_obj.PSWRD,pdf)
    Exp_Result = '''Expected Result : The request or response (that would be generated) is too large for the implementation to handle.

error-tag:      too-big
error-type:     transport, rpc, protocol, application
error-severity: error
error-info:     none
Description: The request or response (that would be generated) is too large for the implementation to handle.
 '''
    STARTUP.STORE_DATA(Exp_Result, Format='DESC', PDF=pdf)

    STARTUP.STORE_DATA('\t\t{}'.format('****************** Actual Result ******************'), Format=True, PDF=pdf)
    try:
        if Check == True:
            STARTUP.ACT_RES(f"{'too-big' : <50}{'=' : ^20}{'SUCCESS' : ^20}",PDF= pdf,COL=(0,255,0))
            return True

        elif type(Check) == list:
            STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
            Error_Info = '''ERROR\n\terror-type \t: \t{}\n\terror-tag \t: \t{}\n\terror-severity \t: \t{}\n\tmessage' \t: \t{}'''.format(*map(str,Check))
            STARTUP.STORE_DATA(Error_Info,Format=False,PDF= pdf)
            STARTUP.ACT_RES(f"{'too-big ' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(255,0,0))
            return False
        else:
            STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
            STARTUP.STORE_DATA('{}'.format(Check),Format=False,PDF= pdf)
            STARTUP.ACT_RES(f"{'too-big )' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(255,0,0))
            return False


    except Exception as e:
            STARTUP.STORE_DATA('{}'.format(e), Format=True,PDF=pdf)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
            return False

    ###############################################################################
    ## For Capturing the logs
    ###############################################################################
    finally:
        STARTUP.CREATE_LOGS('M_FTC_ID_{}'.format(filename),PDF=pdf)


if __name__ == "__main__":
    try:
        filename = sys.argv[1]
        obj = test_m_ctc_id_020()
    except Exception as e:
        print('Usage: python netconf_session.py <Test_Case_ID>')









   











# from logging import exception
# import socket
# import sys
# from ncclient import manager
# from ncclient.operations.rpc import RPCError
# import xmltodict
# import xml.dom.minidom
# import time , os
# from ncclient.transport import errors
# from paramiko.ssh_exception import NoValidConnectionsError
# from ncclient.operations.errors import TimeoutExpiredError
# from ncclient.transport.errors import SessionCloseError

# from configparser import ConfigParser


# ###############################################################################
# ## Directory Path
# ###############################################################################
# dir_name = os.path.dirname(os.path.abspath(__file__))
# parent = (os.path.dirname(dir_name))
# print(dir_name)
# sys.path.append(parent)


# ########################################################################
# ## For reading data from .ini file
# ########################################################################
# configur = ConfigParser()
# configur.read('{}/inputs.ini'.format(dir_name))

# ###############################################################################
# ## Related Imports
# ###############################################################################
# from require.Vlan_Creation import *
# from require import STARTUP, Config
# from require.Genrate_User_Pass import *


# ###############################################################################
# ## Initiate PDF
# ###############################################################################



# pdf_log = STARTUP.PDF_CAP()


# class TOO_BIG():
    
#     def __init__(self) -> None:
#         try:
#             self.port = 830
#             self.USER_N = Config.details['SUDO_USER']
#             self.PSWRD = Config.details['SUDO_PASS']
#             self.du_password = Config.details['DU_PASS']
#             self.session = manager.call_home(host = '', port=4334, hostkey_verify=False,username = self.USER_N, password = self.PSWRD ,allow_agent = False , look_for_keys = False)
#             li = self.session._session._transport.sock.getpeername()
#             sid = self.session.session_id
#             self.host = li[0]
#             data = STARTUP.demo(self.session)
#             self.users, self.slots, self.macs = data[0], data[1], data[2]
            
#         except Exception as e:
#             STARTUP.STORE_DATA('{}'.format(e), Format = True,PDF=pdf_log)
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             STARTUP.STORE_DATA(
#                 f"Error occured in line number {exc_tb.tb_lineno}", Format = False,PDF=pdf_log)
#             return '{}'.format(e)



#     def session_login(self):
#             try:
#                 STARTUP.STORE_DATA('********** Connect to the NETCONF Server ***********',Format='TEST_STEP',PDF=pdf_log)
#                 STATUS = STARTUP.STATUS(self.host,self.USER_N,self.session.session_id,self.port)
#                 STARTUP.STORE_DATA(STATUS,Format=False,PDF=pdf_log)

#                 for i in self.session.server_capabilities:
#                     STARTUP.STORE_DATA('{}'.format(i),Format=False,PDF=pdf_log)


#                 ################ Create Subscription ###############                   
#                 cap = self.session.create_subscription()
#                 STARTUP.STORE_DATA('********** Create Subscription ***********',Format=True,PDF=pdf_log)
#                 STARTUP.STORE_DATA('>subscribe',Format=True,PDF=pdf_log)
#                 dict_data = xmltodict.parse(str(cap))
#                 if dict_data['nc:rpc-reply']['nc:ok']== None:
#                     STARTUP.STORE_DATA('\nOk\n',Format=False,PDF=pdf_log)




#                 # pdf_log.add_page()
#                 # STARTUP.STORE_DATA("###########Step 1 The TER NETCONF Client periodically tests O-RU’s sync-status until the LOCKED state is reached.#####################",Format='TEST_STEP',PDF=pdf_log)
#                 # STARTUP.STORE_DATA('>get --filter-xpath /o-ran-sync:sync',Format=True,PDF=pdf_log)
#                 # while True:
#                 #     SYNC = '''<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
#                 #     <sync xmlns="urn:o-ran:sync:1.0">
#                 #     </sync>
#                 #     </filter>
#                 #     '''
#                 #     data  = self.session.get(SYNC).data_xml
#                 #     dict_Sync = xmltodict.parse(str(data))
#                 #     state = dict_Sync['data']['sync']['sync-status']['sync-state']
#                 #     if state == 'LOCKED':
#                 #         x = xml.dom.minidom.parseString(data)
#                 #         xml_pretty_str = x.toprettyxml()
#                 #         STARTUP.STORE_DATA(xml_pretty_str,Format=True,PDF=pdf_log)
#                 #         break
        

                
#                 STARTUP.STORE_DATA('\t\t********** User_mgmt GET FILTER***********',Format=True,PDF=pdf_log)
#                 STARTUP.STORE_DATA('>get --filter-xpath /o-ran-usermgmt:users/user',Format=True,PDF=pdf_log)
#                 v_name1 = '''
#                         <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
#                 <users xmlns="urn:o-ran:user-mgmt:1.0">	
#                 </users>
#             </filter>'''
#                 users_s = self.session.get(v_name1).data_xml
#                 x = xml.dom.minidom.parseString(users_s)
#                 xml_pretty_str = x.toprettyxml()
#                 STARTUP.STORE_DATA(xml_pretty_str,Format='XML',PDF=pdf_log)




#                 xml_data = open("{}/require/Yang_xml/M_FTC_ID_054.xml".format(parent)).read()
#                 # xml_data = open("xml/M_FTC_ID_054.xml").read()
#                 u1 =f'''
#                     <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
#                     {xml_data}
#                     </config>'''
#                 STARTUP.STORE_DATA('\t\t*******  Create NEW USER ********',Format='TEST_STEP',PDF=pdf_log)
#                 STARTUP.STORE_DATA('> edit-config --target running --config --defop merge',Format=True,PDF=pdf_log)
#                 STARTUP.STORE_DATA('\t\t*******  Replace with XMl ********',Format=True,PDF=pdf_log)
#                 STARTUP.STORE_DATA(xml_data,Format=True,PDF=pdf_log)
#                 d = self.session.edit_config(target='running',config=u1)
#                 STARTUP.STORE_DATA(d,Format=True,PDF=pdf_log)
#                 dict_data = xmltodict.parse(str(d))
#                 print(dict_data)
#                 '''d = m.dispatch(to_ele(xml_data))
#                 STARTUP.STORE_DATA(d,Format=True,PDF=pdf_log)
#                 dict_data = xmltodict(str(d))
#                 if dict_data ['nc:rpc-reply']['nc:reject-reason']== ' [too-big/too-small] Username not valid, The request or response (that would be generated) istoo big/small for the implementation to handle.!!':
#                     pass
#                 else :
#                     return ['nc:rpc-reply']['nc:reject-reason']
                    
#                 '''
#                 return 'Configuration are pushed...'

#             except RPCError as e:
#                 if '[too-big/too-small]' in e.message:
#                 # if e.message[0:20] == '[too-big/too-small]':
#                     STARTUP.STORE_DATA("###########  Rpc Reply ####################",Format=True,PDF=pdf_log)
#                     STARTUP.STORE_DATA('ERROR\n',Format=False,PDF=pdf_log)
#                     STARTUP.STORE_DATA(f"\t{'type' : <20}{':' : ^10}{e.type: ^10}\n",Format=False,PDF=pdf_log)
#                     STARTUP.STORE_DATA(f"\t{'tag' : <20}{':' : ^10}{e.tag: ^10}\n",Format=False,PDF=pdf_log)
#                     STARTUP.STORE_DATA(f"\t{'severity' : <20}{':' : ^10}{e.severity: ^10}\n",Format=False,PDF=pdf_log)
#                     STARTUP.STORE_DATA(f"\t{'path' : <20}{':' : ^10}{e.path: ^10}\n",Format=False,PDF=pdf_log)
#                     STARTUP.STORE_DATA(f"\t{'message' : <20}{':' : ^10}{e.message: ^10}\n",Format=False,PDF=pdf_log)
#                     return True
#                 else:
#                     exc_type, exc_obj, exc_tb = sys.exc_info()
#                     return [e.type, e.tag, e.severity, e.path, e.message, exc_tb.tb_lineno]

#                     # return [e.type, e.tag, e.severity,e.path, e,e.message]



#     def Error_Tag(self,filename,Test_Case_ID):
#     #give the input configuration in xml file format
#     #xml_1 = open('o-ran-hardware.xml').read()
#     #give the input in the format hostname, port, username, password 
#         try:
#             del self.slots['swRecoverySlot']
            
#             for key, val in self.slots.items():
#                 if val[0] == 'true' and val[1] == 'true':
#                     ############################### Test Description #############################
#                     Test_Desc = '''Test Description : Test to verify whether from the NETCONF Error List with tag too-big.'''
#                     CONFIDENTIAL = STARTUP.ADD_CONFIDENTIAL(Test_Case_ID,SW_R = val[2]) 
#                     STARTUP.STORE_DATA(CONFIDENTIAL,Format='CONF',PDF= pdf_log)
#                     STARTUP.STORE_DATA(Test_Desc,Format='DESC',PDF= pdf_log)
#                     pdf_log.add_page()
#                     pass


            
            
#             time.sleep(5)
#             result = self.session_login()

#             STARTUP.GET_SYSTEM_LOGS(self.host,self.USER_N,self.PSWRD,pdf_log)
                         
#             Exp_Result = '''Expected Result : The request or response (that would be generated) is too large for the implementation to handle.

# error-tag:      too-big
# error-type:     transport, rpc, protocol, application
# error-severity: error
# error-info:     none
# Description: The request or response (that would be generated) is too large for the implementation to handle.
# '''
#             STARTUP.STORE_DATA(Exp_Result,Format='DESC',PDF= pdf_log)

#             STARTUP.STORE_DATA('\t\t{}'.format('****************** Actual Result ******************'),Format=True,PDF= pdf_log)

#             if result != True:                
#                 time.sleep(5)
#                 if type(result) == list:
#                     STARTUP.STORE_DATA(f"ERROR",Format=True,PDF= pdf_log)
#                     STARTUP.STORE_DATA(f"{'error-type' : <20}{':' : ^10}{result[0]: ^10}",Format=False,PDF=pdf_log)
#                     STARTUP.STORE_DATA(f"{'error-tag' : <20}{':' : ^10}{result[1]: ^10}",Format=False,PDF=pdf_log)
#                     STARTUP.STORE_DATA(f"{'error-severity' : <20}{':' : ^10}{result[2]: ^10}",Format=False,PDF=pdf_log)
#                     STARTUP.STORE_DATA(f"{'error-path' : <20}{':' : ^10}{result[3]: ^10}",Format=False,PDF=pdf_log)
#                     #print(f"{'error-info' : <20}{':' : ^10}{res[3]: ^10}")
#                     STARTUP.STORE_DATA(f"{'error-message' : <20}{':' : ^10}{result[4]: ^10}",Format=False,PDF=pdf_log)
#                     return result[5]
#                 else:
#                     STARTUP.STORE_DATA(f"{'Error_Tag_Mismatch' : <15}{'=' : ^20}{result : ^20}",Format=False,PDF=pdf_log)
#                 STARTUP.ACT_RES(f"{'Error_Tag[too-big]' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf_log,COL=(255,0,0))
#                 return result
                
#             else:
#                 time.sleep(5)
#                 STARTUP.ACT_RES(f"{'Error_Tag[too-big]' : <50}{'=' : ^20}{'PASS' : ^20}",PDF= pdf_log,COL=(105, 224, 113))
#                 return True    

#         ############################### Known Exceptions ####################################################
#         except socket.timeout as e:
#             Error = '{} : Call Home is not initiated, SSH Socket connection lost....'.format(
#                 e)
#             STARTUP.STORE_DATA(Error, Format=True,PDF=pdf_log)
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             STARTUP.STORE_DATA(
#                 f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf_log)
#             return Error
#             # raise socket.timeout('{}: SSH Socket connection lost....'.format(e)) from None

#         except errors.SSHError as e:
#             Error = '{} : SSH Socket connection lost....'.format(e)
#             STARTUP.STORE_DATA(Error, Format=True,PDF=pdf_log)
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             STARTUP.STORE_DATA(
#                 f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf_log)
#             return Error
#             # raise errors.SSHError('{}: SSH Socket connection lost....'.format(e)) from None

#         except errors.AuthenticationError as e:
#             Error = "{} : Invalid username/password........".format(e)
#             STARTUP.STORE_DATA(Error, Format=True,PDF=pdf_log)
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             STARTUP.STORE_DATA(
#                 f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf_log)
#             return Error
#             # raise f'{e} : Invalid username/password........'

#         except NoValidConnectionsError as e:
#             Error = '{} : ...'.format(e)
#             STARTUP.STORE_DATA(Error, Format=True,PDF=pdf_log)
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             STARTUP.STORE_DATA(
#                 f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf_log)
#             return Error
#             # raise e

#         except TimeoutError as e:
#             Error = '{} : Call Home is not initiated, Timout Expired....'.format(e)
#             STARTUP.STORE_DATA(Error, Format=True,PDF=pdf_log)
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             STARTUP.STORE_DATA(
#                 f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf_log)
#             return Error
#             # raise f'{e} : Call Home is not initiated, Timout Expired....'

#         except SessionCloseError as e:
#             Error = "{} : Unexpected_Session_Closed....".format(e)
#             STARTUP.STORE_DATA(Error, Format=True,PDF=pdf_log)
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             STARTUP.STORE_DATA(
#                 f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf_log)
#             return Error
#             # raise f'{e},Unexpected_Session_Closed....'

#         except TimeoutExpiredError as e:
#             Error = "{} : TimeoutExpiredError....".format(e)
#             STARTUP.STORE_DATA(Error, Format=True,PDF=pdf_log)
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             STARTUP.STORE_DATA(
#                 f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf_log)
#             return Error
#             # raise e

#         except OSError as e:
#             Error = '{} : Call Home is not initiated, Please wait for sometime........'.format(
#                 e)
#             STARTUP.STORE_DATA(Error, Format=True,PDF=pdf_log)
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             STARTUP.STORE_DATA(
#                 f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf_log)
#             return Error
#             # raise Exception('{} : Please wait for sometime........'.format(e)) from None

#         except Exception as e:
#             STARTUP.STORE_DATA('{}'.format(e), Format=True,PDF=pdf_log)
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             STARTUP.STORE_DATA(
#                 f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf_log)
#             return '{}'.format(e)
#             # raise Exception('{}'.format(e)) from None


#         ############################### MAKE PDF File ####################################################
#         finally:
#             STARTUP.CREATE_LOGS('{}'.format(filename),PDF=pdf_log)

                
                
    
# if __name__ == '__main__':
#     try:
#         obj = TOO_BIG()
#         filename = sys.argv[0].split('.')
#         Result = obj.Error_Tag(filename[0],sys.argv[1])
#     except Exception as e:
#         STARTUP.STORE_DATA('{}'.format(e), Format = True,PDF=pdf_log)
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         STARTUP.STORE_DATA(
#             f"Error occured in line number {exc_tb.tb_lineno}", Format = False,PDF=pdf_log)
#         print('Usage: python Too_Big.py <Test_Case_ID>')
    
    