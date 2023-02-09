###############################################################################
##@ FILE NAME:      Error-tag : bad-attribute
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

class Bad_attribute():

    def __init__(self) -> None:
        try:
            self.port = 830
            self.USER_N = configur.get('INFO', 'sudo_user')
            self.PSWRD = configur.get('INFO', 'sudo_pass')
            self.du_password = Config.details['DU_PASS']
            self.session = manager.call_home(host = '', port=4334, hostkey_verify=False,username = self.USER_N, password = self.PSWRD ,allow_agent = False , look_for_keys = False)
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
            STARTUP.STORE_DATA("########### The TER NETCONF Client periodically tests O-RU’s sync-status until the LOCKED state is reached.#####################",Format='TEST_STEP',PDF=pdf_log)
            STARTUP.STORE_DATA('>get --filter-xpath /o-ran-sync:sync',Format=True,PDF=pdf_log)
            while True:
                SYNC = '''<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <sync xmlns="urn:o-ran:sync:1.0">
                </sync>
                </filter>
                '''
                data  = self.session.get(SYNC).data_xml
                dict_Sync = xmltodict.parse(str(data))
                state = dict_Sync['data']['sync']['sync-status']['sync-state']
                if state == 'LOCKED':
                    x = xml.dom.minidom.parseString(data)
                    xml_pretty_str = x.toprettyxml()
                    STARTUP.STORE_DATA(xml_pretty_str,Format='XML',PDF=pdf_log)
                    break


            
            STARTUP.STORE_DATA('********** User_mgmt GET FILTER***********',Format=True,PDF=pdf_log)
            STARTUP.STORE_DATA('>get --filter-xpath /o-ran-usermgmt:users/user',Format=True,PDF=pdf_log)
            v_name1 = '''
                    <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                    <users xmlns="urn:o-ran:user-mgmt:1.0">
                    </interfaces>
                    </users>
            '''
            users_s = self.session.get(v_name1).data_xml
            x = xml.dom.minidom.parseString(users_s)
            xml_pretty_str = x.toprettyxml()
            STARTUP.STORE_DATA(xml_pretty_str,Format='XML',PDF=pdf_log)
            



            xml_data = open("xml/M_FTC_ID_056.xml").read()
            u1 =f'''
                    <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                    {xml_data}
                    </config>'''


            ###############################################################################
            ## Test step for genrating the bad attribute
            ############################################################################### 
            STARTUP.STORE_DATA('\t\t******* Create NEW USER ********',Format='TEST_STEP',PDF=pdf_log)
            STARTUP.STORE_DATA('> edit-config --target running --config --defop merge',Format=True,PDF=pdf_log)
            STARTUP.STORE_DATA('\t\t*******  Replace with XMl ********',Format=True,PDF=pdf_log)
            STARTUP.STORE_DATA(xml_data,Format='XML',PDF=pdf_log)
            d = self.session.edit_config(target='running',config=u1)
            STARTUP.STORE_DATA('{}'.format(d),Format='XML',PDF=pdf_log)
            dict_data = xmltodict.parse(str(d))
            '''d = m.dispatch(to_ele(xml_data))
            print('-'*100)  print('-'*100)
            print(d)
            print('*'*100)
            dict_data = xmltodict(str(d))
            if dict_data ['nc:rpc-reply']['nc:reject-reason']== ' [bad-attribute] Username not valid!!':
                pass
            else :
                return ['nc:rpc-reply']['nc:reject-reason']
                
            '''


        ###############################################################################
        ## Corresponding error tag will come
        ###############################################################################
        except RPCError as e:
            #print(e.message[0:15])
            if e.message[0:15] == '[bad-attribute]':
                STARTUP.STORE_DATA("###########  Rpc Reply ####################",Format=True,PDF=pdf_log)
                STARTUP.STORE_DATA('ERROR',Format=False,PDF=pdf_log)
                STARTUP.STORE_DATA(f"\t{'type' : <20}{':' : ^10}{e.type: ^10}\n",Format=False,PDF=pdf_log)
                STARTUP.STORE_DATA(f"\t{'tag' : <20}{':' : ^10}{e.tag: ^10}\n",Format=False,PDF=pdf_log)
                STARTUP.STORE_DATA(f"\t{'severity' : <20}{':' : ^10}{e.severity: ^10}\n",Format=False,PDF=pdf_log)
                STARTUP.STORE_DATA(f"\t{'message' : <20}{':' : ^10}{e.message: ^10}\n",Format=False,PDF=pdf_log)
            else:
                return [e.type, e.tag, e.severity, e,e.message]
           


    def Error_Tag(self,filename,Test_Case_ID):
        try:
            del self.slots['swRecoverySlot']
            
            for key, val in self.slots.items():
                if val[0] == 'true' and val[1] == 'true':
                    ############################### Test Description #############################
                    Test_Desc = '''Test Description : Test to verify whether from the NETCONF Error List with tag bad-attribute.'''
                    CONFIDENTIAL = STARTUP.ADD_CONFIDENTIAL(Test_Case_ID,SW_R = val[2]) 
                    STARTUP.STORE_DATA(CONFIDENTIAL,Format='CONF',PDF= pdf_log)
                    STARTUP.STORE_DATA(Test_Desc,Format='DESC',PDF= pdf_log)
                    pdf_log.add_page()
                    pass


            
            
            time.sleep(5)
            result = self.session_login()

            STARTUP.GET_SYSTEM_LOGS(self.host,self.USER_N,self.PSWRD,pdf_log)
                         
            Exp_Result = '''Expected Result : The request or response have an expected attribute missing.same of the element that is supposed  to contain the missing attribute

                error-tag:      bad-attribute
                error-type:     rpc, protocol, application
                error-severity: error  
                error-info:<bad-attribute> : name of the attribute w/ bad value
                <bad-element> : name of the element that contains the attribute with the bad value
                Description: An attribute value is not correct; e.g., wrong type, out of range, pattern mismatch.
                '''
            STARTUP.STORE_DATA(Exp_Result,Format='DESC',PDF= pdf_log)
            STARTUP.STORE_DATA('\t\t{}'.format('****************** Actual Result ******************'),Format=True,PDF= pdf_log)

            if result:
                if type(result) == list:
                    STARTUP.STORE_DATA(f"ERROR",Format=True,PDF= pdf_log)
                    STARTUP.STORE_DATA(f"{'error-type' : <20}{':' : ^10}{result[0]: ^10}",Format=False,PDF=pdf_log)
                    STARTUP.STORE_DATA(f"{'error-tag' : <20}{':' : ^10}{result[1]: ^10}",Format=False,PDF=pdf_log)
                    STARTUP.STORE_DATA(f"{'error-severity' : <20}{':' : ^10}{result[2]: ^10}",Format=False,PDF=pdf_log)
                    #print(f"{'error-info' : <20}{':' : ^10}{res[3]: ^10}")
                    STARTUP.STORE_DATA(f"{'Description' : <20}{':' : ^10}{result[4]: ^10}",Format=False,PDF=pdf_log)
                    return result[5]
                else:
                    STARTUP.STORE_DATA(f"{'Error_Tag_Mismatch' : <15}{'=' : ^20}{result : ^20}",Format=False,PDF=pdf_log)
                STARTUP.ACT_RES(f"{'Error_Tag[bad-attribute]' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf_log,COL=(255,0,0))
                return result
                
            else:
                STARTUP.ACT_RES(f"{'Error_Tag[bad-attribute]' : <50}{'=' : ^20}{'PASS' : ^20}",PDF= pdf_log,COL=(105, 224, 113))
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
            STARTUP.CREATE_LOGS('{}'.format(filename),PDF=pdf_log)
            try:
                self.session.close_session()
            except Exception as e:
                print(e)
                
                
    
if __name__ == '__main__':
    try:
        obj = Bad_attribute()
        filename = sys.argv[0].split('.')
        Result = obj.Error_Tag(filename[0],sys.argv[1])
    except Exception as e:
        STARTUP.STORE_DATA('{}'.format(e), Format = True,PDF=pdf_log)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(
            f"Error occured in line number {exc_tb.tb_lineno}", Format = False,PDF=pdf_log)
        print('Usage: python bad-attribute.py <Test_Case_ID>')
    
    