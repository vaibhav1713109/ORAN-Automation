from logging import exception
import socket
import sys
from ncclient import manager
from ncclient.operations.rpc import RPCError
import xmltodict
import xml.dom.minidom
import time
from ncclient.transport import errors
from paramiko.ssh_exception import NoValidConnectionsError
from ncclient.operations.errors import TimeoutExpiredError
from ncclient.transport.errors import SessionCloseError
import STARTUP,Config

pdf_log = STARTUP.PDF_CAP()


class TOO_BIG():
    
    def __init__(self) -> None:
        try:
            self.port = 830
            self.USER_N = Config.details['SUDO_USER']
            self.PSWRD = Config.details['SUDO_PASS']
            self.du_password = Config.details['DU_PASS']
            self.session = manager.call_home(host = '', port=4334, hostkey_verify=False,username = self.USER_N, password = self.PSWRD ,allow_agent = False , look_for_keys = False)
            li = self.session._session._transport.sock.getpeername()
            sid = self.session.session_id
            self.host = li[0]
            data = STARTUP.demo(self.session)
            self.users, self.slots, self.macs = data[0], data[1], data[2]
            
        except Exception as e:
            STARTUP.STORE_DATA('{}'.format(e), Format = True,PDF=pdf_log)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format = False,PDF=pdf_log)
            return '{}'.format(e)



    def session_login(self):
            try:
                STARTUP.STORE_DATA('********** Connect to the NETCONF Server ***********',Format='TEST_STEP',PDF=pdf_log)
                STATUS = STARTUP.STATUS(self.host,self.USER_N,self.session.session_id,self.port)
                STARTUP.STORE_DATA(STATUS,Format=False,PDF=pdf_log)

                for i in self.session.server_capabilities:
                    STARTUP.STORE_DATA('{}'.format(i),Format=False,PDF=pdf_log)


                ################ Create Subscription ###############                   
                cap = self.session.create_subscription()
                STARTUP.STORE_DATA('********** Create Subscription ***********',Format=True,PDF=pdf_log)
                STARTUP.STORE_DATA('>subscribe',Format=True,PDF=pdf_log)
                dict_data = xmltodict.parse(str(cap))
                if dict_data['nc:rpc-reply']['nc:ok']== None:
                    STARTUP.STORE_DATA('\nOk\n',Format=False,PDF=pdf_log)




                pdf_log.add_page()
                STARTUP.STORE_DATA("###########Step 1 The TER NETCONF Client periodically tests O-RU’s sync-status until the LOCKED state is reached.#####################",Format='TEST_STEP',PDF=pdf_log)
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
                        STARTUP.STORE_DATA(xml_pretty_str,Format=True,PDF=pdf_log)
                        break
        

                
                STARTUP.STORE_DATA('\t\t********** User_mgmt GET FILTER***********',Format=True,PDF=pdf_log)
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





                xml_data = open("xml/M_FTC_ID_054.xml").read()
                u1 =f'''
                    <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                    {xml_data}
                    </config>'''
                STARTUP.STORE_DATA('\t\t*******  Create NEW USER ********',Format='TEST_STEP',PDF=pdf_log)
                STARTUP.STORE_DATA('> edit-config --target running --config --defop merge',Format=True,PDF=pdf_log)
                STARTUP.STORE_DATA('\t\t*******  Replace with XMl ********',Format=True,PDF=pdf_log)
                STARTUP.STORE_DATA(xml_data,Format=True,PDF=pdf_log)
                d = self.session.edit_config(target='running',config=u1)
                STARTUP.STORE_DATA(d,Format=True,PDF=pdf_log)
                dict_data = xmltodict.parse(str(d))
                '''d = m.dispatch(to_ele(xml_data))
                STARTUP.STORE_DATA(d,Format=True,PDF=pdf_log)
                dict_data = xmltodict(str(d))
                if dict_data ['nc:rpc-reply']['nc:reject-reason']== ' [too-big/too-small] Username not valid, The request or response (that would be generated) istoo big/small for the implementation to handle.!!':
                    pass
                else :
                    return ['nc:rpc-reply']['nc:reject-reason']
                    
                '''
                return 'Configuration are pushed...'

            except RPCError as e:
                if e.message[0:20] == '[too-big/too-small]':
                    STARTUP.STORE_DATA("###########  Rpc Reply ####################",Format=True,PDF=pdf_log)
                    STARTUP.STORE_DATA('ERROR',Format=False,PDF=pdf_log)
                    STARTUP.STORE_DATA(f"\t{'type' : <20}{':' : ^10}{e.type: ^10}\n",Format=False,PDF=pdf_log)
                    STARTUP.STORE_DATA(f"\t{'tag' : <20}{':' : ^10}{e.tag: ^10}\n",Format=False,PDF=pdf_log)
                    STARTUP.STORE_DATA(f"\t{'severity' : <20}{':' : ^10}{e.severity: ^10}\n",Format=False,PDF=pdf_log)
                    STARTUP.STORE_DATA(f"\t{'message' : <20}{':' : ^10}{e.message: ^10}\n",Format=False,PDF=pdf_log)
                else:
                    return [e.type, e.tag, e.severity, e,e.message]



    def Error_Tag(self,filename,Test_Case_ID):
    #give the input configuration in xml file format
    #xml_1 = open('o-ran-hardware.xml').read()
    #give the input in the format hostname, port, username, password 
        try:
            del self.slots['swRecoverySlot']
            
            for key, val in self.slots.items():
                if val[0] == 'true' and val[1] == 'true':
                    ############################### Test Description #############################
                    Test_Desc = '''Test Description : Test to verify whether from the NETCONF Error List with tag too-big.'''
                    CONFIDENTIAL = STARTUP.ADD_CONFIDENTIAL(Test_Case_ID,SW_R = val[2]) 
                    STARTUP.STORE_DATA(CONFIDENTIAL,Format='CONF',PDF= pdf_log)
                    STARTUP.STORE_DATA(Test_Desc,Format='DESC',PDF= pdf_log)
                    pdf_log.add_page()
                    pass


            
            
            time.sleep(5)
            result = self.session_login()

            STARTUP.GET_SYSTEM_LOGS(self.host,self.USER_N,self.PSWRD,pdf_log)
                         
            Exp_Result = '''Expected Result : The request or response (that would be generated) is too large for the implementation to handle.

error-tag:      too-big
error-type:     transport, rpc, protocol, application
error-severity: error
error-info:     none
Description: The request or response (that would be generated) is too large for the implementation to handle.
'''
            STARTUP.STORE_DATA(Exp_Result,Format='DESC',PDF= pdf_log)

            STARTUP.STORE_DATA('\t\t{}'.format('****************** Actual Result ******************'),Format=True,PDF= pdf_log)

            if result:                
                time.sleep(5)
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
                STARTUP.ACT_RES(f"{'Error_Tag[too-big]' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf_log,COL=(255,0,0))
                return result
                
            else:
                time.sleep(5)
                STARTUP.ACT_RES(f"{'Error_Tag[too-big]' : <50}{'=' : ^20}{'PASS' : ^20}",PDF= pdf_log,COL=(105, 224, 113))
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

        except errors.SSHError as e:
            Error = '{} : SSH Socket connection lost....'.format(e)
            STARTUP.STORE_DATA(Error, Format=True,PDF=pdf_log)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf_log)
            return Error
            # raise errors.SSHError('{}: SSH Socket connection lost....'.format(e)) from None

        except errors.AuthenticationError as e:
            Error = "{} : Invalid username/password........".format(e)
            STARTUP.STORE_DATA(Error, Format=True,PDF=pdf_log)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf_log)
            return Error
            # raise f'{e} : Invalid username/password........'

        except NoValidConnectionsError as e:
            Error = '{} : ...'.format(e)
            STARTUP.STORE_DATA(Error, Format=True,PDF=pdf_log)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf_log)
            return Error
            # raise e

        except TimeoutError as e:
            Error = '{} : Call Home is not initiated, Timout Expired....'.format(e)
            STARTUP.STORE_DATA(Error, Format=True,PDF=pdf_log)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf_log)
            return Error
            # raise f'{e} : Call Home is not initiated, Timout Expired....'

        except SessionCloseError as e:
            Error = "{} : Unexpected_Session_Closed....".format(e)
            STARTUP.STORE_DATA(Error, Format=True,PDF=pdf_log)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf_log)
            return Error
            # raise f'{e},Unexpected_Session_Closed....'

        except TimeoutExpiredError as e:
            Error = "{} : TimeoutExpiredError....".format(e)
            STARTUP.STORE_DATA(Error, Format=True,PDF=pdf_log)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf_log)
            return Error
            # raise e

        except OSError as e:
            Error = '{} : Call Home is not initiated, Please wait for sometime........'.format(
                e)
            STARTUP.STORE_DATA(Error, Format=True,PDF=pdf_log)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf_log)
            return Error
            # raise Exception('{} : Please wait for sometime........'.format(e)) from None

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

                
                
    
if __name__ == '__main__':
    try:
        obj = TOO_BIG()
        filename = sys.argv[0].split('.')
        Result = obj.Error_Tag(filename[0],sys.argv[1])
    except Exception as e:
        STARTUP.STORE_DATA('{}'.format(e), Format = True,PDF=pdf_log)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(
            f"Error occured in line number {exc_tb.tb_lineno}", Format = False,PDF=pdf_log)
        print('Usage: python Too_Big.py <Test_Case_ID>')
    
    