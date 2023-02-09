###############################################################################
##@ FILE NAME:      Error-tag : bad-element
##@ TEST SCOPE:     M PLANE O-RAN Functional
##@ Version:        V_1.0.0
##@ Support:        @Ramiyer, @VaibhavDhiman, @PriyaSharma
###############################################################################

###############################################################################
## Package Imports 
###############################################################################

import sys, os, time, xmltodict, xml.dom.minidom, lxml.etree, ifcfg
from ncclient import manager
from ncclient.operations.rpc import RPC, RPCError
from ncclient.transport import errors
from paramiko.ssh_exception import NoValidConnectionsError
from ncclient.operations.errors import TimeoutExpiredError
from ncclient.transport.errors import SessionCloseError
from ncclient.xml_ import to_ele
from configparser import ConfigParser
from scapy.all import *

###############################################################################
## Directory Path
###############################################################################
dir_name = os.path.dirname(os.path.abspath(__file__))
parent = os.path.dirname(dir_name)
print(parent)
sys.path.append(parent)

########################################################################
## For reading data from .ini file
########################################################################
configur = ConfigParser()
configur.read('{}/inputs.ini'.format(dir_name))

###############################################################################
## Related Imports
###############################################################################
from require import STARTUP, Config
from require.Vlan_Creation import *



###############################################################################
## Initiate PDF
###############################################################################
pdf_log = STARTUP.PDF_CAP()

class bad_element(vlan_Creation):

    def __init__(self) -> None:
        super().__init__()
        try:
            Check1 = self.linked_detected()
            if Check1 == False or Check1 == None:
                return Check1

            sniff(iface = self.interface, stop_filter = self.check_tcp_ip, timeout = 100)
            STARTUP.delete_system_log(host= self.hostname)
            time.sleep(4)
            self.port = 830
            self.USER_N = configur.get('INFO', 'sudo_user')
            self.PSWRD = configur.get('INFO', 'sudo_pass')
            self.du_password = Config.details['DU_PASS']
            self.session = STARTUP.call_home(host = '', port=4334, hostkey_verify=False,username = self.USER_N, password = self.PSWRD ,allow_agent = False , look_for_keys = False, timeout = 60)
            li = self.session._session._transport.sock.getpeername()
            sid = self.session.session_id
            self.host = li[0]
            data = STARTUP.demo(self.session)
            self.users, self.slots, self.macs = data[0], data[1], data[2]
            pass
        except Exception as e:
            STARTUP.STORE_DATA('{}'.format(e), Format = True,PDF=pdf_log)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format = False,PDF=pdf_log)
            return '{}'.format(e)

    def session_login(self):
        try:
            ###############################################################################
            ## Connect to the Netconf-Server
            ###############################################################################
            STARTUP.STORE_DATA('********** Connect to the NETCONF Server ***********',Format='TEST_STEP',PDF=pdf_log)
            STATUS = STARTUP.STATUS(self.host,self.USER_N,self.session.session_id,self.port)
            STARTUP.STORE_DATA(STATUS,Format=False,PDF=pdf_log)

            for i in self.session.server_capabilities:
                STARTUP.STORE_DATA('{}'.format(i),Format=False,PDF=pdf_log)


            ###############################################################################
            ## Create Subscription
            ###############################################################################                
            cap = self.session.create_subscription()
            STARTUP.STORE_DATA('********** Create Subscription ***********',Format=True,PDF=pdf_log)
            STARTUP.STORE_DATA('>subscribe',Format=True,PDF=pdf_log)
            dict_data = xmltodict.parse(str(cap))
            if dict_data['nc:rpc-reply']['nc:ok']== None:
                STARTUP.STORE_DATA('\nOk\n',Format=False,PDF=pdf_log)



            ###############################################################################
            ## Test wether sync state locked or unlocked
            ###############################################################################                
            # STARTUP.STORE_DATA("########### The TER NETCONF Client periodically tests O-RU’s sync-status until the LOCKED state is reached.#####################",Format='TEST_STEP',PDF=pdf_log)
            # STARTUP.STORE_DATA('>get --filter-xpath /o-ran-sync:sync',Format=True,PDF=pdf_log)
            # while True:
            #     SYNC = '''<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            #     <sync xmlns="urn:o-ran:sync:1.0">
            #     </sync>
            #     </filter>
            #     '''
            #     data  = self.session.get(SYNC).data_xml
            #     dict_Sync = xmltodict.parse(str(data))
            #     state = dict_Sync['data']['sync']['sync-status']['sync-state']
            #     if state == 'LOCKED':
            #         x = xml.dom.minidom.parseString(data)
            #         xml_pretty_str = x.toprettyxml()
            #         STARTUP.STORE_DATA(xml_pretty_str,Format='XML',PDF=pdf_log)
            #         break

              
            ###############################################################################
            ## Test step for genrating the bad_element
            ###############################################################################                
<<<<<<< HEAD
            xml_data = """<retrieve-file-list xmlns="urn:o-ran:file-management:1.0">
            <logical-path>/home/root/</logical-path>
            <file-name-filter>O-RAN-WG4.MP.0-v04.00.pdf</file-name-filter>
            </retrieve-file-list>"""

            STARTUP.STORE_DATA('\n> user-rpc\n', Format=True,PDF=pdf_log)


            STARTUP.STORE_DATA('\t\t******* Replace with below xml ********', Format=True,PDF=pdf_log)
            STARTUP.STORE_DATA(xml_data, Format='XML',PDF=pdf_log)
            
            rpc_command = to_ele(xml_data)
            rpc_reply = self.session.rpc(rpc_command)
            if 'bad-element' in str(rpc_reply):
                STARTUP.STORE_DATA('******* RPC Reply ********',Format=True,PDF=pdf_log)
                STARTUP.STORE_DATA('{}'.format(rpc_reply), Format='XML',PDF=pdf_log)
                return True
=======
            xml_data = open("xml/bad_element.xml").read()
            u1 =f'''
                    <config>
                    {xml_data}
                    </config>'''


            STARTUP.STORE_DATA('\t\t******* Configure Inteface yang********',Format='TEST_STEP',PDF=pdf_log)
            STARTUP.STORE_DATA('> edit-config --target running --config --defop merge',Format=True,PDF=pdf_log)
            STARTUP.STORE_DATA('\t\t*******  Replace with XMl ********',Format=True,PDF=pdf_log)
            STARTUP.STORE_DATA(xml_data,Format='XML',PDF=pdf_log)
            rpc_reply = self.session.edit_config(target='running',config=u1)
            STARTUP.STORE_DATA('{}'.format(rpc_reply),Format='XML',PDF=pdf_log)
            dict_data = xmltodict.parse(str(rpc_reply))
            return 'Configuration are pushed...'
>>>>>>> v0.0.1


        ###############################################################################
        ## Corresponding error tag will come
        ###############################################################################                
        except RPCError as e:
            #print(e.message[0:15])
<<<<<<< HEAD
            if 'bad-element' in e.message:
=======
            if 'Missing element' in e.message:
>>>>>>> v0.0.1
                STARTUP.STORE_DATA("###########  Rpc Reply ####################",Format=True,PDF=pdf_log)
                STARTUP.STORE_DATA('\nERROR',Format=False,PDF=pdf_log)
                STARTUP.STORE_DATA(f"\t{'type' : <20}{':' : ^10}{e.type: ^10}\n",Format=False,PDF=pdf_log)
                STARTUP.STORE_DATA(f"\t{'tag' : <20}{':' : ^10}{e.tag: ^10}\n",Format=False,PDF=pdf_log)
                STARTUP.STORE_DATA(f"\t{'severity' : <20}{':' : ^10}{e.severity: ^10}\n",Format=False,PDF=pdf_log)
                # STARTUP.STORE_DATA(f"\t{'path' : <20}{':' : ^10}{e.path: ^10}\n",Format=False,PDF=pdf_log)
                STARTUP.STORE_DATA(f"\t{'message' : <20}{':' : ^10}{e.message: ^10}\n",Format=False,PDF=pdf_log)
                return True
            else:
                # STARTUP.STORE_DATA("###########  Rpc Reply ####################",Format=True,PDF=pdf_log)
                # STARTUP.STORE_DATA('\nERROR',Format=False,PDF=pdf_log)
                # STARTUP.STORE_DATA(f"\t{'type' : <20}{':' : ^10}{e.type: ^10}\n",Format=False,PDF=pdf_log)
                # STARTUP.STORE_DATA(f"\t{'tag' : <20}{':' : ^10}{e.tag: ^10}\n",Format=False,PDF=pdf_log)
                # STARTUP.STORE_DATA(f"\t{'severity' : <20}{':' : ^10}{e.severity: ^10}\n",Format=False,PDF=pdf_log)
                # # STARTUP.STORE_DATA(f"\t{'path' : <20}{':' : ^10}{e.path: ^10}\n",Format=False,PDF=pdf_log)
                # STARTUP.STORE_DATA(f"\t{'message' : <20}{':' : ^10}{e.message: ^10}\n",Format=False,PDF=pdf_log)
                return [e.type, e.tag, e.severity, e.path ,e.message]
        
        except Exception as e:
            STARTUP.STORE_DATA(e, Format=True,PDF=pdf_log)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf_log)
            return e
           


    def test_main(self):
        try:
            del self.slots['swRecoverySlot']
            
            for key, val in self.slots.items():
                if val[0] == 'true' and val[1] == 'true':
                    ############################### Test Description #############################
                    Test_Desc = '''Test Description : Test to verify whether from the NETCONF Error List with tag bad-element'''
                    CONFIDENTIAL = STARTUP.ADD_CONFIDENTIAL(filename,SW_R = val[2]) 
                    STARTUP.STORE_DATA(CONFIDENTIAL,Format='CONF',PDF= pdf_log)
                    STARTUP.STORE_DATA(Test_Desc,Format='DESC',PDF= pdf_log)
                    pdf_log.add_page()
                    pass


            
            
            time.sleep(5)
            result = self.session_login()

            STARTUP.GET_SYSTEM_LOGS(self.host,self.USER_N,self.PSWRD,pdf_log)
                         
            Exp_Result = '''Expected Result : An expected element is missing.

error-tag:      bad-element
error-type:     protocol, application
error-severity: error
error-info:     <bad-element> : name of the missing element
Description:    An expected element is missing.

                '''
            STARTUP.STORE_DATA(Exp_Result,Format='DESC',PDF= pdf_log)
            STARTUP.STORE_DATA('\t\t{}'.format('****************** Actual Result ******************'),Format=True,PDF= pdf_log)

            if result != True:
                if type(result) == list:
                    STARTUP.STORE_DATA(f"ERROR",Format=True,PDF= pdf_log)
                    STARTUP.STORE_DATA(f"{'error-type' : <20}{':' : ^10}{result[0]: ^10}",Format=False,PDF=pdf_log)
                    STARTUP.STORE_DATA(f"{'error-tag' : <20}{':' : ^10}{result[1]: ^10}",Format=False,PDF=pdf_log)
                    STARTUP.STORE_DATA(f"{'error-severity' : <20}{':' : ^10}{result[2]: ^10}",Format=False,PDF=pdf_log)
                    # STARTUP.STORE_DATA(f"{'error-path' : <20}{':' : ^10}{result[3]: ^10}",Format=False,PDF=pdf_log)
                    STARTUP.STORE_DATA(f"{'Description' : <20}{':' : ^10}{result[4]: ^10}",Format=False,PDF=pdf_log)
                else:
                    STARTUP.STORE_DATA(f"{'Fail-Reason' : <15}{'=' : ^20}{result : ^20}",Format=False,PDF=pdf_log)
                STARTUP.ACT_RES(f"{'Error_Tag[bad-element]' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf_log,COL=(255,0,0))
                return result
                
            else:
                STARTUP.ACT_RES(f"{'Error_Tag[bad-element]' : <50}{'=' : ^20}{'PASS' : ^20}",PDF= pdf_log,COL=(105, 224, 113))
                return True    

        ############################### Known Exceptions ####################################################
        except socket.timeout as e:
            Error = '{} : Call Home is not initiated, SSH Socket connection lost....'.format(
                e)
            STARTUP.STORE_DATA(Error, Format=True,PDF=pdf_log)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf_log)
            return Error
            # raise socket.timeout('{}: SSH Socket connection lost....'.format(e)) from None

        except Exception as e:
            STARTUP.STORE_DATA('{}'.format(e), Format=True,PDF=pdf_log)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf_log)
            return '{}'.format(e)
            # raise Exception('{}'.format(e)) from None


        ############################### MAKE PDF File ####################################################
        finally:
            STARTUP.CREATE_LOGS('M_FTC_ID_{}'.format(filename),PDF=pdf_log)
            try:
                self.session.close_session()
            except Exception as e:
                print(e)

                
                
    
if __name__ == '__main__':
    try:
        obj = bad_element()
        filename = sys.argv[1]
        Result = obj.test_main()
    except Exception as e:
        STARTUP.STORE_DATA('{}'.format(e), Format = True,PDF=pdf_log)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(
            f"Error occured in line number {exc_tb.tb_lineno}", Format = False,PDF=pdf_log)
        print('Usage: python bad_element.py <Test_Case_ID>')
    

