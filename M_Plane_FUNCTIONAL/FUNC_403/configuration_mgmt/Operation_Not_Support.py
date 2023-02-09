import socket
import sys
from ncclient import manager
from ncclient.operations.rpc import RPCError
import xmltodict
import xml.dom.minidom
import time
from ncclient.transport import errors
import re
from paramiko.ssh_exception import NoValidConnectionsError
from ncclient.operations.errors import TimeoutExpiredError
from ncclient.transport.errors import SessionCloseError
import STARTUP, Config

pdf_log = STARTUP.PDF_CAP()

class Operation_not_Support():
    def __init__(self,filename,element_name,interface_name):
        try:
            self.filename = filename
            self.element_name = element_name
            self.port = 830
            self.USER_N = Config.details['SUDO_USER']
            self.PSWRD = Config.details['SUDO_PASS']
            self.session = manager.call_home(host = '', port=4334, hostkey_verify=False,username = self.USER_N, password = self.PSWRD ,allow_agent = False , look_for_keys = False)
            li = self.session._session._transport.sock.getpeername()
            sid = self.session.session_id
            self.ip_adr = interface_name                        ############################### Frontaul Interface name persent in RU
            self.host = li[0]
            data = STARTUP.demo(self.session)
            self.users, self.slots, self.macs = data[0], data[1], data[2]
            self.mac = self.macs[self.ip_adr]
            self.port_n = self.ip_adr[3]
            self.du_mac = Config.details['DU_MAC']
            val = self.isValidMACAddress(self.du_mac)
            if val == True:
                pass
            else:
                STARTUP.STORE_DATA('Please provide valid mac address :\n',Format=True,PDF=pdf_log)
                return 0
            pass
        except Exception as e:
            STARTUP.STORE_DATA('{}'.format(e), Format = True,PDF=pdf_log)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format = False,PDF=pdf_log)
            return '{}'.format(e)

    def session_login(self):
        try:
            xml_data = open('xml/interface.xml').read()
            xml_data = xml_data.format(interface_name= self.ip_adr,mac = self.mac, number= self.port_n)
            u1 =f'''
                    <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                    {xml_data}
                    </config>'''
            try:
                Data = self.session.edit_config(u1, target='running')
            except RPCError as e:
                STARTUP.STORE_DATA('{0} RPCError {}'.format('*'*30),Format=True,PDF=pdf_log)
                STARTUP.STORE_DATA("\t\t Not able to push interface xml: {}".format(e),Format=False,PDF=pdf_log)
                return '{}'.format(e)


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
        


                

                xml_data = open("xml/M_FTC_ID_062.xml").read()
                xml_data = xml_data.format(int_name= self.ip_adr,ru_mac = self.mac,du_mac = self.du_mac, element_name= self.element_name)
                u1 =f'''
                    <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                    {xml_data}
                    </config>'''


                STARTUP.STORE_DATA('\t\t*******  TER NETCONF Client sends <rpc><Processing> to the O-RU NETCONF Server ********',Format='TEST_STEP',PDF=pdf_log)
                STARTUP.STORE_DATA('> edit-config  --target running --config --defop replace',Format=True,PDF=pdf_log)
                STARTUP.STORE_DATA(xml_data,Format='XML',PDF=pdf_log)
                d = self.session.edit_config(target='running',config=u1)
                STARTUP.STORE_DATA('{}'.format(d))
                dict_data = xmltodict.parse(str(d))
                return 'Configuration are pushed...'
                

            except RPCError as e:
                s = '[operation-not-supported]'
                if s in e.message:
                    STARTUP.STORE_DATA("###########  Rpc Reply ####################",Format=True,PDF=pdf_log)
                    STARTUP.STORE_DATA('ERROR',Format=False,PDF=pdf_log)
                    STARTUP.STORE_DATA(f"\t{'type' : <20}{':' : ^10}{e.type: ^10}\n",Format=False,PDF=pdf_log)
                    STARTUP.STORE_DATA(f"\t{'tag' : <20}{':' : ^10}{e.tag: ^10}\n",Format=False,PDF=pdf_log)
                    STARTUP.STORE_DATA(f"\t{'severity' : <20}{':' : ^10}{e.severity: ^10}\n",Format=False,PDF=pdf_log)
                    STARTUP.STORE_DATA(f"\t{'message' : <20}{':' : ^10}{e.message: ^10}\n",Format=False,PDF=pdf_log)
                else:
                    return [e.type, e.tag, e.severity, e.path ,e.message]
        
        except Exception as e:
            STARTUP.STORE_DATA('{}'.format(e), Format=True,PDF=pdf_log)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf_log)
            return '{}'.format(e)
        
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



    def OPR_not_Support(self,Test_Case_ID):

        try:
                
                
            for key, val in self.slots.items():
                if val[0] == 'true' and val[1] == 'true':
                    ############################### Test Description #############################
                    Test_Desc = '''Test Description : Test to verify whether from the NETCONF Error List with tag operation-not-supported.'''
                    CONFIDENTIAL = STARTUP.ADD_CONFIDENTIAL(Test_Case_ID,SW_R = val[2]) 
                    STARTUP.STORE_DATA(CONFIDENTIAL,Format='CONF',PDF= pdf_log)
                    STARTUP.STORE_DATA(Test_Desc,Format='DESC',PDF= pdf_log)
                    pdf_log.add_page()
            

            time.sleep(5)
            result = self.session_login()
            STARTUP.GET_SYSTEM_LOGS(self.host,self.USER_N,self.PSWRD,pdf_log)
                         
            Exp_Result = '''Expected Result : Request could not be completed because the requested operation is not supported by this implementation.

error-tag:      operation-not-supported
error-type:     protocol, application
error-severity: error
error-info:     none
Description:    Request could not be completed because the requested
                   operation is not supported by this implementation.
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
                STARTUP.ACT_RES(f"{'Error_Tag[Operation-not-supported]' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf_log,COL=(255,0,0))
                return result
                
            else:
                time.sleep(5)
                STARTUP.ACT_RES(f"{'Error_Tag[Operation-not-supported]' : <50}{'=' : ^20}{'PASS' : ^20}",PDF= pdf_log,COL=(105, 224, 113))
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
            STARTUP.CREATE_LOGS(self.filename,PDF=pdf_log)

                
                
    
if __name__ == '__main__':
    try:
        filename = sys.argv[0].split('.')
        obj = Operation_not_Support(filename[0],sys.argv[1],sys.argv[2])
        Result = obj.OPR_not_Support(sys.argv[3])
    except Exception as e:
        STARTUP.STORE_DATA('{}'.format(e), Format = True,PDF=pdf_log)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(
            f"Error occured in line number {exc_tb.tb_lineno}", Format = False,PDF=pdf_log)
        print('Usage: python Operation_Not_Support.py <Element_Name> <Fronthaul_Interface_name_of_RU(Eg: eth0, eth1)> <Test_Case_ID>')
    
    