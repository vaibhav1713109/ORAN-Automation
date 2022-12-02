###############################################################################
##@ FILE NAME:      Bandwidth Switch
##@ TEST SCOPE:     M PLANE O-RAN Functional
##@ Version:        V_1.0.0
##@ Support:        @Ramiyer, @VaibhavDhiman, @PriyaSharma
###############################################################################

###############################################################################
## Package Imports 
###############################################################################

import sys, os, time, xmltodict, xml.dom.minidom, lxml.etree, ifcfg
from ncclient import manager
import warnings
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

class bandwidth_switch(vlan_Creation):

    def __init__(self) -> None:
        super().__init__()
        try:
            self.FH_interface = sys.argv[2]
            self.element = sys.argv[3]
            self.bandwidths = sys.argv[4]
            self.bandwidths = self.bandwidths[1:-1].split(',')
            # print(self.bandwidths)
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
            pass
        
        except socket.timeout as e:
            warnings.warn('Call Home is not initiated.')
            try:
                self.session = manager.connect(host = self.hostname, port=830, hostkey_verify=False,username = self.USER_N, password = self.PSWRD , timeout = 60)       
            except Exception as e:
                print(e)      

        except OSError as e:
            warnings.warn('Call Home is not initiated.')
            try:
                self.session = manager.connect(host = self.hostname, port=830, hostkey_verify=False,username = self.USER_N, password = self.PSWRD , timeout = 60)       
            except Exception as e:
                print(e)  

        except Exception as e:  
            STARTUP.STORE_DATA('{}'.format(e), Format = True,PDF=pdf_log)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format = False,PDF=pdf_log)
            return '{}'.format(e)

        finally:
            try:
                data = STARTUP.demo(self.session)
                self.users, self.slots, self.macs = data[0], data[1], data[2]
                self.du_mac = ifcfg.interfaces()[self.interface]['ether']
                self.ru_mac = self.macs[self.FH_interface]
            except Exception as e:
                print(e)

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
            ## Configure Interface yang module
            ###############################################################################                
            xml_data = open('xml/interface.xml').read()
            xml_data = xml_data.format(interface_name= self.FH_interface,mac = self.ru_mac, number= self.FH_interface[3])
            u1 =f'''
                    <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                    {xml_data}
                    </config>'''
            try:
                Data = self.session.edit_config(u1, target='running')
            except RPCError as e:            
                STARTUP.STORE_DATA('{0} RPCError {0}'.format('*'*30),Format=True,PDF=pdf_log)
                STARTUP.STORE_DATA("Not able to push interface xml \n{}".format(e),Format=False,PDF=pdf_log)
                return '{}'.format(e)

            ###############################################################################
            ## Configure processing yang module
            ###############################################################################
            xml_data1 = open('xml/processing.xml').read()
            xml_data1 = xml_data1.format(int_name= self.FH_interface,ru_mac = self.ru_mac,du_mac = self.du_mac, element_name= self.element)
            u2 =f'''
                    <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                    {xml_data1}
                    </config>'''
            try:
                Data = self.session.edit_config(u2, target='running',default_operation = 'replace')
            except RPCError as e:
                STARTUP.STORE_DATA('{0} RPCError {0}'.format('*'*30),Format=True,PDF=pdf_log)
                STARTUP.STORE_DATA("Not able to push processing xml \n{}".format(e),Format=False,PDF=pdf_log)
                return '{}'.format(e)

            STARTUP.STORE_DATA('################# Pre get filter #################',Format='TEST_STEP',PDF=pdf_log)
            STARTUP.STORE_DATA('>get --filter-xpath /o-ran-uplane-conf:user-plane-configuration',Format=True,PDF=pdf_log)
                
            up ='''
                <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <user-plane-configuration xmlns="urn:o-ran:uplane-conf:1.0">
                </user-plane-configuration>
                </filter>
                '''
            Cap = self.session.get(up).data_xml
            x = xml.dom.minidom.parseString(Cap)
            xml_pretty_str = x.toprettyxml()
            STARTUP.STORE_DATA(xml_pretty_str,Format='XML',PDF=pdf_log)


            ######### Configure U Plane with different Channel Bandwidth #########
            txarfcn= configur.get('INFO', 'tx_arfcn')
            rxarfcn= configur.get('INFO', 'rx_arfcn')
            tx_center_freq= configur.get('INFO', 'tx_center_freq')
            rx_center_freq= configur.get('INFO', 'rx_center_freq')
            for bw in self.bandwidths:
                STARTUP.STORE_DATA("######### Configure U Plane with different Channel Bandwidth #########",Format='TEST_STEP',PDF=pdf_log)     
                STARTUP.STORE_DATA('> edit-config  --target running --config --defop replace',Format=True,PDF=pdf_log)
                STARTUP.STORE_DATA('******* Replace with below xml ********',Format=True,PDF=pdf_log)
                
                
                xml_1 = open('xml/uplane.xml').read()
                xml_1 = xml_1.format(element_name= self.element,ch_bandwidth = int(float(bw)*(10**6)),tx_arfcn=txarfcn, rx_arfcn = rxarfcn,
                        tx_center_freq= int(float(tx_center_freq)*(10**9)), rx_center_freq= int(float(rx_center_freq)*(10**9)))
                snippet = f"""
                            <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                            {xml_1}
                            </config>"""
                
                STARTUP.STORE_DATA(snippet,Format='XML',PDF=pdf_log)
                STARTUP.STORE_DATA("#########  The O-RU NETCONF Sever responds with the <rpc-reply> .#########",Format=True,PDF=pdf_log)
                data1 = self.session.edit_config(target="running", config=snippet, default_operation = 'replace')
                dict_data1 = xmltodict.parse(str(data1))
                if dict_data1['nc:rpc-reply']['nc:ok']== None:
                    STARTUP.STORE_DATA('Ok',Format=True,PDF=pdf_log)
                    



                STARTUP.STORE_DATA('################# Post get filter #################',Format=True,PDF=pdf_log)
                STARTUP.STORE_DATA('>get --filter-xpath /o-ran-uplane-conf:user-plane-configuration',Format=True,PDF=pdf_log)
                    
                up ='''
                    <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                    <user-plane-configuration xmlns="urn:o-ran:uplane-conf:1.0">
                    </user-plane-configuration>
                    </filter>
                    '''
                Cap = self.session.get(up).data_xml
                x = xml.dom.minidom.parseString(Cap)
                xml_pretty_str = x.toprettyxml()
                STARTUP.STORE_DATA(xml_pretty_str,Format='XML',PDF=pdf_log)


                return True


        ###############################################################################
        ## Corresponding error tag will come
        ###############################################################################                
        except RPCError as e:
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
                    Test_Desc = '''Test Description : 1. O-RU is successfully synchronised with CUS emulator (ORS In lab Env)
                            2. Using U Plane Yang model configure TX/RX Array carrier or Using WEB-GUI configure the Channel Bandwidth. 
                            3. NETCONF Client triggers <rpc><ge-config --source running> towards NETCONF Server'''
                    CONFIDENTIAL = STARTUP.ADD_CONFIDENTIAL(filename,SW_R = val[2]) 
                    STARTUP.STORE_DATA(CONFIDENTIAL,Format='CONF',PDF= pdf_log)
                    STARTUP.STORE_DATA(Test_Desc,Format='DESC',PDF= pdf_log)
                    pdf_log.add_page()
                    pass


            
            
            time.sleep(5)
            result = self.session_login()

            STARTUP.GET_SYSTEM_LOGS(self.host,self.USER_N,self.PSWRD,pdf_log)
                         
            Exp_Result = '''Expected Result : 1. O-RU is in Sync lock state.
            2. O-RU controller able to modify the parameters in O-RU's running configurations
            3. Verify the O-RU reply with <rpc> <reply> <OK> 
                '''
            STARTUP.STORE_DATA(Exp_Result,Format='DESC',PDF= pdf_log)
            STARTUP.STORE_DATA('\t\t{}'.format('****************** Actual Result ******************'),Format=True,PDF= pdf_log)

            if result != True:
                if type(result) == list:
                    STARTUP.STORE_DATA(f"ERROR",Format=True,PDF= pdf_log)
                    STARTUP.STORE_DATA(f"{'error-type' : <20}{':' : ^10}{result[0]: ^10}",Format=False,PDF=pdf_log)
                    STARTUP.STORE_DATA(f"{'error-tag' : <20}{':' : ^10}{result[1]: ^10}",Format=False,PDF=pdf_log)
                    STARTUP.STORE_DATA(f"{'error-severity' : <20}{':' : ^10}{result[2]: ^10}",Format=False,PDF=pdf_log)
                    STARTUP.STORE_DATA(f"{'error-path' : <20}{':' : ^10}{result[3]: ^10}",Format=False,PDF=pdf_log)
                    STARTUP.STORE_DATA(f"{'Description' : <20}{':' : ^10}{result[4]: ^10}",Format=False,PDF=pdf_log)
                    return result[5]
                else:
                    STARTUP.STORE_DATA(f"{'Fail-Reason' : <15}{'=' : ^20}{result : ^20}",Format=False,PDF=pdf_log)
                STARTUP.ACT_RES(f"{'Bandwidth Switch' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf_log,COL=(255,0,0))
                return result
                
            else:
                STARTUP.ACT_RES(f"{'Bandwidth Switch' : <50}{'=' : ^20}{'PASS' : ^20}",PDF= pdf_log,COL=(105, 224, 113))
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
        obj = bandwidth_switch()
        filename = sys.argv[1]
        Result = obj.test_main()
    except Exception as e:
        STARTUP.STORE_DATA('{}'.format(e), Format = True,PDF=pdf_log)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(
            f"Error occured in line number {exc_tb.tb_lineno}", Format = False,PDF=pdf_log)
    print('Usage: python Bandwidth_Switch.py <Test_Case_ID> <Fronthaul Interface Eg. eth0/eth1> <element name eg. element0/element1> <bandwidths Eg. [10,15,20]>')
    

