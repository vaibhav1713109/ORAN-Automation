###############################################################################
##@ FILE NAME:      M_CTC_ID_027
##@ TEST SCOPE:     M PLANE O-RAN CONFORMANCE
##@ Version:        V_1.0.0
##@ Support:        @Ramiyer, @VaibhavDhiman, @PriyaSharma
###############################################################################

###############################################################################
## Package Imports 
###############################################################################

import sys, os, time, xmltodict, xml.dom.minidom, lxml.etree, ifcfg, socket
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
from require import STARTUP, Config
from Conformance.M_CTC_ID_026 import M_CTC_ID_026

###############################################################################
## Initiate PDF
###############################################################################
pdf = STARTUP.PDF_CAP()

class M_CTC_ID_027(M_CTC_ID_026):
    # init method or constructor 
    def __init__(self):
        super().__init__()

    

    ###############################################################################
    ## Test Procedure
    ###############################################################################
    def test_procedure(self):
        try:
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
            ## Configure Interface Yang
            ###############################################################################
            n = self.interface_ru[3]
            xml_data = open('{}/require/Yang_xml/interface.xml'.format(parent)).read()
            xml_data = xml_data.format(interface_name= self.interface_ru,mac = self.ru_mac, number= n)
            u1 =f'''
                    <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                    {xml_data}
                    </config>'''
            Data = self.session.edit_config(u1, target='running')
            
            ###############################################################################
            ## Configure Processing Yang
            ###############################################################################
            xml_data1 = open('{}/require/Yang_xml/processing.xml'.format(parent)).read()
            xml_data1 = xml_data1.format(int_name= self.interface_ru,ru_mac = self.ru_mac, du_mac = self.du_mac, element_name= self.element_name)
            u2 =f'''
                    <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                    {xml_data1}
                    </config>'''
            Data = self.session.edit_config(u2, target='running')
            

            ###############################################################################
            ## Pre get filter
            ###############################################################################
            pdf.add_page()
            STARTUP.STORE_DATA('################# Pre get filter #################',Format=True, PDF=pdf)
            STARTUP.STORE_DATA('> get --filter-xpath /o-ran-uplane-conf:user-plane-configuration',Format=True, PDF=pdf)                    
            up ='''
                <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <user-plane-configuration xmlns="urn:o-ran:uplane-conf:1.0">
                </user-plane-configuration>
                </filter>
                '''
            Cap = self.session.get(up).data_xml
            x = xml.dom.minidom.parseString(Cap)
            xml_pretty_str = x.toprettyxml()
            STARTUP.STORE_DATA(xml_pretty_str,Format='XML', PDF=pdf) 


            ###############################################################################
            ## Test Procedure 1 : Configure Uplane Yang
            ###############################################################################   
            pdf.add_page()          
            Test_Step1 = "STEP 1 The TER NETCONF Client assigns unique eAxC_IDs to low-level-rx-endpoints. The same set of eAxC_IDs is also assigned to low-level-tx-endpoints. The TER NETCONF Client uses <rpc><editconfig>."
            STARTUP.STORE_DATA('{}'.format(Test_Step1),Format='TEST_STEP', PDF=pdf)
            
            STARTUP.STORE_DATA('> edit-config  --target running --config --defop replace',Format=True, PDF=pdf)
            STARTUP.STORE_DATA('******* Replace with below xml ********',Format=True, PDF=pdf)
            
            xml_1 = open('{}/require/Yang_xml/TC_27.xml'.format(parent)).read()
            xml_1 = xml_1.format(tx_arfcn = self.tx_arfcn, rx_arfcn = self.rx_arfcn, bandwidth = int(float(self.bandwidth)*(10**6)), tx_center_freq = int(float(self.tx_center_freq)*(10**9)), rx_center_freq = int(float(self.rx_center_freq)*(10**9)), duplex_scheme = self.duplex_scheme,element_name= self.element_name)
            snippet = f"""
                        <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                        {xml_1}
                        </config>"""
            
            STARTUP.STORE_DATA(snippet,Format='XML', PDF=pdf)

            try:
                data1 = self.session.edit_config(target="running", config=snippet, default_operation = 'replace')
                dict_data1 = xmltodict.parse(str(data1))
                if dict_data1['nc:rpc-reply']['nc:ok']== None:
                    STARTUP.STORE_DATA('\nOk\n',Format=False, PDF=pdf)
                    return f'\t\t******COnfiguration are pushed********\n {data1}'
                    

            except RPCError as e:
                if "[operation-not-supported]Duplicate value '1' found for eaxc-id" in e.message:
                    ###############################################################################
                    ## Test Procedure 2 : Check Access Denied
                    ###############################################################################   
                    pdf.add_page()
                    Test_Step2 = 'STEP 2 The O-RU NETCONF Sever responds with the <rpc-reply> message indicating rejection of the requested procedure.'
                    STARTUP.STORE_DATA('{}'.format(Test_Step2),Format='TEST_STEP', PDF=pdf)
                    STARTUP.STORE_DATA('ERROR\n',Format=False, PDF=pdf)
                    STARTUP.STORE_DATA(f"{'type' :^20}{':' : ^10}{e.type: ^10}\n",Format=False, PDF=pdf)
                    STARTUP.STORE_DATA(f"{'tag' : ^20}{':' : ^10}{e.tag: ^10}\n",Format=False, PDF=pdf)
                    STARTUP.STORE_DATA(f"{'severity' : ^20}{':' : ^10}{e.severity: ^10}\n",Format=False, PDF=pdf)
                    STARTUP.STORE_DATA(f"{'path' : ^20}{':' : ^10}{e.path: ^10}\n",Format=False, PDF=pdf)
                    STARTUP.STORE_DATA(f"{'message' : ^20}{':' : ^10}{e.message: ^10}\n",Format=False, PDF=pdf)
                    return True
                else:
                    return 'Description : {}'.format(e.message)
        ###############################################################################
        ## Exception
        ###############################################################################
        except RPCError as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
            return [e.type, e.tag, e.severity, e.path, e.message, exc_tb.tb_lineno]

        except Exception as e:
            STARTUP.STORE_DATA('{}'.format(e), Format=True,PDF=pdf)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
            return e
        
        


        

    ###############################################################################
    ## Main Function
    ###############################################################################
    def test_Main_027(self):
        Check1 = self.linked_detected()
        
        
        ###############################################################################
        ## Read User Name and password from Config.INI of Config.py
        ############################################################################### 
        self.USER_N = configur.get('INFO','sudo_user')
        self.PSWRD = configur.get('INFO','sudo_pass')
        self.tx_arfcn = configur.get('INFO','tx_arfcn')
        self.rx_arfcn = configur.get('INFO','rx_arfcn')
        self.bandwidth = configur.get('INFO','bandwidth')
        self.tx_center_freq = configur.get('INFO','tx_center_frequency')
        self.rx_center_freq = configur.get('INFO','rx_center_frequency')
        self.duplex_scheme = configur.get('INFO','duplex_scheme')
        self.interface_ru = configur.get('INFO','fh_interface')
        if Check1 == False or Check1 == None:
            return Check1

        sniff(iface = self.interface, stop_filter = self.check_tcp_ip, timeout = 100)
        try:
            STARTUP.delete_system_log(host= self.hostname)
            ###############################################################################
            ## Perform call home to get ip_details
            ###############################################################################
            self.session = STARTUP.call_home(host = '0.0.0.0', port=4334, hostkey_verify=False,username = self.USER_N, password = self.PSWRD,timeout = 60,allow_agent = False , look_for_keys = False)
            self.hostname, self.call_home_port = self.session._session._transport.sock.getpeername()   #['ip_address', 'TCP_Port']
            
            if self.session:
                self.RU_Details = STARTUP.demo(session = self.session,host= self.hostname, port= 830)
                for key, val in self.RU_Details[1].items():
                        if val[0] == 'true' and val[1] == 'true':
                            ###############################################################################
                            ## Test Description
                            ###############################################################################
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
                
                
                ###############################################################################
                ## Fronthoul Interface
                ###############################################################################
                macs = self.FETCH_MAC()
                self.ru_mac = macs[self.interface_ru]
                self.du_mac = ifcfg.interfaces()[self.interface]['ether']
                time.sleep(5)
                result = self.test_procedure()
                # time.sleep(5)
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
            STARTUP.STORE_DATA(
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
                
        
def test_m_ctc_id_027():
    tc027_obj = M_CTC_ID_027()
    Check = tc027_obj.test_Main_027()
    if Check == False:
            STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
            STARTUP.STORE_DATA('SFP link not detected...',Format=False,PDF= pdf)
            STARTUP.ACT_RES(f"{'O-RU Configurability Test (negative case)' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=[255,0,0])
            return False
    ###############################################################################
    ## Expected/Actual Result
    ###############################################################################
    STARTUP.GET_SYSTEM_LOGS(tc027_obj.hostname,tc027_obj.USER_N,tc027_obj.PSWRD,pdf)
    Exp_Result = 'Expected Result : The O-RU NETCONF Sever responds with the <rpc-reply> message indicating rejection of the requested procedure'
    STARTUP.STORE_DATA(Exp_Result, Format='DESC', PDF=pdf)

    STARTUP.STORE_DATA('\t\t{}'.format('****************** Actual Result ******************'), Format=True, PDF=pdf)
    try:
        if Check == True:
            STARTUP.ACT_RES(f"{'O-RU Configurability Test (negative case)' : <50}{'=' : ^20}{'SUCCESS' : ^20}",PDF= pdf,COL=[0,255,0])
            return True

        elif type(Check) == list:
            STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
            Error_Info = '''ERROR\n\terror-type \t: \t{}\n\terror-tag \t: \t{}\n\terror-severity \t: \t{}\n\tpath \t: \t{}\n\tDescription' \t: \t{}'''.format(*map(str,Check))
            STARTUP.STORE_DATA(Error_Info,Format=False,PDF= pdf)
            STARTUP.ACT_RES(f"{'O-RU Configurability Test (negative case)' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=[255,0,0])
            return False
        else:
            STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
            STARTUP.STORE_DATA('{}'.format(Check),Format=False,PDF= pdf)
            STARTUP.ACT_RES(f"{'O-RU Configurability Test (negative case)' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=[255,0,0])
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
        STARTUP.CREATE_LOGS('M_CTC_ID_027',PDF=pdf)


if __name__ == "__main__":
    test_m_ctc_id_027()
    pass
