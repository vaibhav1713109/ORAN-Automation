###############################################################################
##@ FILE NAME:      Performance Measurement Deactivation using the single NETCONF client for all mesurement groups
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
from .performance_activation import *



###############################################################################
## Initiate PDF
###############################################################################
pdf_log = STARTUP.PDF_CAP()

class performance_Deactivation(performance_activation):

    def __init__(self) -> None:
        super().__init__()
        


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

            self.config_interface_processing_iplane()

            # ###############################################################################
            # ## Create Subscription
            # ###############################################################################                
            # cap = self.session.create_subscription()
            # STARTUP.STORE_DATA('********** Create Subscription ***********',Format=True,PDF=pdf_log)
            # STARTUP.STORE_DATA('>subscribe',Format=True,PDF=pdf_log)
            # dict_data = xmltodict.parse(str(cap))
            # if dict_data['nc:rpc-reply']['nc:ok']== None:
            #     STARTUP.STORE_DATA('\nOk\n',Format=False,PDF=pdf_log)
            

            ###############################################################################
            ## Pre Get Filter
            ############################################################################### 
            STARTUP.STORE_DATA('################# Pre get filter #################',Format=True,PDF=pdf_log)
            STARTUP.STORE_DATA('>get --filter-xpath /o-ran-performance-management:performance-measurement-objects',Format=True,PDF=pdf_log)
                
            get_filter ='''
                <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <performance-measurement-objects xmlns="urn:o-ran:performance-management:1.0">
                </performance-measurement-objects>
                </filter>
                '''
            Cap = self.session.get(get_filter).data_xml
            x = xml.dom.minidom.parseString(Cap)
            xml_pretty_str = x.toprettyxml()
            STARTUP.STORE_DATA(xml_pretty_str,Format='XML',PDF=pdf_log)

            ###############################################################################
            ## Fetch Public Key of Linux PC
            ###############################################################################
            pub_k = subprocess.getoutput('cat /etc/ssh/ssh_host_rsa_key.pub')
            pk = pub_k.split()
            pub_key = pk[1]

            ###############################################################################
            ## Test step 1 configure performance Deactivation
            ###############################################################################  
            xml_data = open("{}/Performance_Management/xml/deactivate_performance.xml".format(parent)).read()
            measurement_interval = 10
            xml_data = xml_data.format(
                rmt_path=self.rmt, password=self.du_password, public_key=pub_key, measurement_interval = measurement_interval)              
            STARTUP.STORE_DATA('\t\t ******* TER NETCONF Client triggers Performance Deactivation RPC *******',Format='TEST_STEP',PDF=pdf_log)
            STARTUP.STORE_DATA('> edit-config  --target running --config --defop replace',Format=True, PDF=pdf_log)
            STARTUP.STORE_DATA('******* Replace with below xml ********',Format=True, PDF=pdf_log)
            STARTUP.STORE_DATA(xml_data,Format='XML',PDF=pdf_log)

            snippet = f"""
                        <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                        {xml_data}
                        </config>"""

            data1 = self.session.edit_config(target="running", config=snippet, default_operation = 'replace')
            STARTUP.STORE_DATA('RPC Reply',Format=True,PDF=pdf_log)
            STARTUP.STORE_DATA(data1,Format=False,PDF=pdf_log)


            ###############################################################################
            ## Post Get Filter
            ############################################################################### 
            STARTUP.STORE_DATA('################# Post get filter #################',Format=True,PDF=pdf_log)
            STARTUP.STORE_DATA('>get --filter-xpath /o-ran-performance-management:performance-measurement-objects',Format=True,PDF=pdf_log)
                
            get_filter ='''
                <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <performance-measurement-objects xmlns="urn:o-ran:performance-management:1.0">
                </performance-measurement-objects>
                </filter>
                '''
            Cap = self.session.get(get_filter).data_xml
            x = xml.dom.minidom.parseString(Cap)
            xml_pretty_str = x.toprettyxml()
            STARTUP.STORE_DATA(xml_pretty_str,Format='XML',PDF=pdf_log)
            return True
            
            

        ###############################################################################
        ## Corresponding error tag will come
        ###############################################################################                
        except RPCError as e:
            STARTUP.STORE_DATA("###########  Rpc Reply ####################",Format=True,PDF=pdf_log)
            STARTUP.STORE_DATA('ERROR\n',Format=False,PDF=pdf_log)
            STARTUP.STORE_DATA(f"\t{'type' : <20}{':' : ^10}{e.type: ^10}\n",Format=False,PDF=pdf_log)
            STARTUP.STORE_DATA(f"\t{'tag' : <20}{':' : ^10}{e.tag: ^10}\n",Format=False,PDF=pdf_log)
            STARTUP.STORE_DATA(f"\t{'severity' : <20}{':' : ^10}{e.severity: ^10}\n",Format=False,PDF=pdf_log)
            STARTUP.STORE_DATA(f"\t{'path' : <20}{':' : ^10}{e.path: ^10}\n",Format=False,PDF=pdf_log)
            STARTUP.STORE_DATA(f"\t{'message' : <20}{':' : ^10}{e.message: ^10}\n",Format=False,PDF=pdf_log)
            return [e.type, e.tag, e.severity, e.path, e.message]
           


    def test_main(self):
        try:
            del self.slots['swRecoverySlot']
            
            for key, val in self.slots.items():
                if val[0] == 'true' and val[1] == 'true':
                    ############################### Test Description #############################
                    Test_Desc = '''Test Description : 1. Open the NETCONF client.
2. Edit the XML file for transceiver stats measurement group with below details:
            2.a measurement-interval (Min | Max value )
            2.b measurement-object (ALL)
            2.c active:FALSE 
            2.d start-time and end-time
            2.e  object-unit
            2.f report-info
3. Save the XML file on local PC.
4 Deactivate the performance measurement via NETCONF client  using rpc <edit-config> to O-RU from O-RU controller.'''
                    CONFIDENTIAL = STARTUP.ADD_CONFIDENTIAL(filename,SW_R = val[2]) 
                    STARTUP.STORE_DATA(CONFIDENTIAL,Format='CONF',PDF= pdf_log)
                    STARTUP.STORE_DATA(Test_Desc,Format='DESC',PDF= pdf_log)
                    pdf_log.add_page()
                    pass


            
            
            time.sleep(5)
            result = self.session_login()

            STARTUP.GET_SYSTEM_LOGS(self.host,self.USER_N,self.PSWRD,pdf_log,number=500)
                         
            Exp_Result = '''Expected Result : 1. Verify the NETCONF client is opened successfully.
2. Verify the modified  parameters are saved in the XML file. 
3. Verify the O-RU successfully deactivated the configured measurement groups via XML file 
                '''
            STARTUP.STORE_DATA(Exp_Result,Format='DESC',PDF= pdf_log)
            STARTUP.STORE_DATA('\t\t{}'.format('****************** Actual Result ******************'),Format=True,PDF= pdf_log)

            if result:
                if type(result) == list:
                    STARTUP.STORE_DATA(f"ERROR",Format=True,PDF= pdf_log)
                    STARTUP.STORE_DATA(f"{'error-type' : <20}{':' : ^10}{result[0]: ^10}",Format=False,PDF=pdf_log)
                    STARTUP.STORE_DATA(f"{'error-tag' : <20}{':' : ^10}{result[1]: ^10}",Format=False,PDF=pdf_log)
                    STARTUP.STORE_DATA(f"{'error-severity' : <20}{':' : ^10}{result[2]: ^10}",Format=False,PDF=pdf_log)
                    STARTUP.STORE_DATA(f"{'error-path' : <20}{':' : ^10}{result[3]: ^10}",Format=False,PDF=pdf_log)
                    STARTUP.STORE_DATA(f"{'Description' : <20}{':' : ^10}{result[4]: ^10}",Format=False,PDF=pdf_log)
                    return result
                else:
                    STARTUP.STORE_DATA(f"{'Error_Tag_Mismatch' : <15}{'=' : ^20}{result : ^20}",Format=False,PDF=pdf_log)
                STARTUP.ACT_RES(f"{'Performance Measurement Deactivation using the single NETCONF client for all mesurement groups' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf_log,COL=(255,0,0))
                return result
                
            else:
                STARTUP.ACT_RES(f"{'Performance Measurement Deactivation using the single NETCONF client for all mesurement groups' : <50}{'=' : ^20}{'PASS' : ^20}",PDF= pdf_log,COL=(105, 224, 113))
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
        obj = performance_Deactivation()
        filename = sys.argv[1]
        Result = obj.test_main()
    except Exception as e:
        STARTUP.STORE_DATA('{}'.format(e), Format = True,PDF=pdf_log)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(
            f"Error occured in line number {exc_tb.tb_lineno}", Format = False,PDF=pdf_log)
        print('Usage: python performance_deactivation.py <Test_Case_ID> <Fronthaul Interface Eg. eth0/eth1> <element name eg. element0/element1> <bandwidths Eg. 10> <remote_path eg. sftp://vvdn@192.168.4.15:22/home/vvdn>')
    
    