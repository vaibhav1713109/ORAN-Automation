###############################################################################
##@ FILE NAME:      M_CTC_ID_022
##@ TEST SCOPE:     M PLANE O-RAN CONFORMANCE
##@ Version:        V_1.0.0
##@ Support:        @Ramiyer, @VaibhavDhiman, @PriyaSharma
###############################################################################

###############################################################################
## Package Imports 
###############################################################################

import sys, os, time, xmltodict, xml.dom.minidom, lxml.etree, paramiko, socket
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
parent = os.path.dirname(dir_name)
# print(parent)
sys.path.append(parent)

########################################################################
## For reading data from .ini file
########################################################################
configur = ConfigParser()
configur.read('{}/inputs.ini'.format(dir_name))

###############################################################################
## Related Imports
###############################################################################
from Conformance.Notification import *
from require.Vlan_Creation import *
from require import STARTUP, Config
from require.Genrate_User_Pass import *

pdf = STARTUP.PDF_CAP()      

def check_swm(hostname,new_user,new_pswrd):
    try:
            with manager.connect(host=hostname, port=830, username=new_user, hostkey_verify=False, password=new_pswrd, allow_agent = False , look_for_keys = False, timeout = 60) as new_session:
                pdf.add_page()
                Test_Step1 = 'STEP 1 TER NETCONF client establishes a connection using a user account with swm privileges.'
                STARTUP.STORE_DATA('{}'.format(Test_Step1),Format='TEST_STEP', PDF=pdf)
                STARTUP.STORE_DATA('\t\t********** Connect to the NETCONF Server ***********', Format='TEST_STEP', PDF=pdf)
                server_key_obj = new_session._session._transport.get_remote_server_key()
                fingerprint = STARTUP.colonify(STARTUP.hexlify(server_key_obj.get_fingerprint()))
                login_info = f'''> connect --ssh --host {hostname} --port 830 --login {new_user}
                        ssh-rsa key fingerprint is {fingerprint}
                        Interactive SSH Authentication done. 
                                '''
                STARTUP.STORE_DATA(login_info,Format=False,PDF = pdf)                
                STATUS = STARTUP.STATUS(hostname,new_user,new_session.session_id,830)       
                STARTUP.STORE_DATA(STATUS,Format=False,PDF = pdf)
                notification("Netconf Session Established")
                ###############################################################################
                ## Server Capabilities
                ###############################################################################
                for cap in new_session.server_capabilities:
                    STARTUP.STORE_DATA("\t{}".format(cap),Format=False,PDF = pdf)
                    
                ###############################################################################
                ## Create_subscription
                ###############################################################################
                filter = """<filter type="xpath" xmlns="urn:ietf:params:xml:ns:netconf:notification:1.0" xmlns:notf_c="urn:ietf:params:xml:ns:yang:ietf-netconf-notifications" select="/notf_c:*"/>"""
                cap=new_session.create_subscription(filter=filter)
                STARTUP.STORE_DATA('> subscribe --filter-xpath /ietf-netconf-notifications:*', Format=True, PDF=pdf)
                dict_data = xmltodict.parse(str(cap))
                if dict_data['nc:rpc-reply']['nc:ok'] == None:
                    STARTUP.STORE_DATA('\nOk\n', Format=False, PDF=pdf)
        
                
                ###############################################################################
                ## Test Procedure 2 : Configure a new o-ran-sync.yang
                ############################################################################### 
                proc_xml = open('{}/require/Yang_xml/sync.xml'.format(parent)).read() 
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
                    data3 = new_session.edit_config(target="running" , config=pro, default_operation = 'replace')
                    if data3:
                        return f'\t*******Configuration are pushed*******\n{data3}'
                except RPCError as e:

                    ###############################################################################
                    ## Check Access Denied
                    ###############################################################################
                    if e.tag == 'access-denied':
                        Test_Step4 = 'Step 3 NETCONF server replies rejecting the protocol operation with an \'access-denied\' error.'
                        STARTUP.STORE_DATA('{}'.format(Test_Step4),Format='TEST_STEP', PDF=pdf)
                        STARTUP.STORE_DATA('ERROR\n',Format=False, PDF=pdf)
                        STARTUP.STORE_DATA(f"{'type' : ^20}{':' : ^10}{e.tag: ^10}\n",Format=False, PDF=pdf)
                        STARTUP.STORE_DATA(f"{'tag' : ^20}{':' : ^10}{e.type: ^10}\n",Format=False, PDF=pdf)
                        STARTUP.STORE_DATA(f"{'severity' : ^20}{':' : ^10}{e.severity: ^10}\n",Format=False, PDF=pdf)
                        STARTUP.STORE_DATA(f"{'path' : ^20}{':' : ^10}{e.path: ^10}\n",Format=False, PDF=pdf)
                        STARTUP.STORE_DATA(f"{'message' : ^20}{':' : ^10}{e.message: ^10}\n",Format=False, PDF=pdf)
                        return True

                    else:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        return [e.type, e.tag, e.severity ,e.message,exc_tb.tb_lineno]
                    
                finally:
                    pass
                    # new_session.close_session()

    ########################### Known Exceptions ############################
    except RPCError as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        # new_session.close_session()
        return [e.type, e.tag, e.severity, e.message, exc_tb.tb_lineno]

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA("\t\tError : {}".format(e), Format=False, PDF=pdf)
        # new_session.close_session()
        return f"{e} \nError occured in line number {exc_tb.tb_lineno}"



check_swm('192.168.4.49','operator429298006246159886060','!eQ{ooXgxHK~Imn[WT1nEq2r_QCLF)(+2KQ1%z}EAXqSt3(X{_2tr(lLasuRpUfnHu-WRdF%Je)tthpp5q{oRY4WNlNZ7LrNsZ)p0FWwhv1o7CJDbCn3')