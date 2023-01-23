###############################################################################
##@ FILE NAME:      M_CTC_ID_011
##@ TEST SCOPE:     M PLANE O-RAN CONFORMANCE
##@ Version:        V_1.0.0
##@ Support:        @Ramiyer, @VaibhavDhiman, @PriyaSharma
###############################################################################

###############################################################################
## Package Imports 
###############################################################################

import socket, sys, os, warnings, time, xmltodict, xml.dom.minidom, paramiko, lxml.etree
from ncclient import manager
from ncclient.operations.rpc import RPC, RPCError
from ncclient.transport import errors
from paramiko.ssh_exception import NoValidConnectionsError
from ncclient.operations.errors import TimeoutExpiredError
from ncclient.transport.errors import SessionCloseError
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
from Conformance.Notification import *
from require.Vlan_Creation import *
from require import STARTUP, Config



###############################################################################
## Initiate PDF
###############################################################################
pdf = STARTUP.PDF_CAP()

class M_CTC_ID_011(vlan_Creation):
   
    # init method or constructor 
    def __init__(self):
        super().__init__()
        self.hostname, self.call_home_port = '',''
        self.USER_N = ''
        self.PSWRD = ''
        self.session = ''

    

    ###############################################################################
    ## Test Procedure
    ###############################################################################
    def test_procedure(self):
    
        STARTUP.STORE_DATA('\n\n\t\t********** Connect to the NETCONF Server ***********\n\n',Format='TEST_STEP',PDF = pdf)
        STARTUP.STORE_DATA(self.login_info,Format=False,PDF = pdf)
        STATUS = STARTUP.STATUS(self.hostname,self.USER_N,self.session.session_id,830)
        STARTUP.STORE_DATA(STATUS,Format=False,PDF = pdf)
        notification('Netconf Session Established!!')


        ###############################################################################
        ## Server Capabilities
        ###############################################################################
        for cap in self.session.server_capabilities:
            STARTUP.STORE_DATA("\t{}".format(cap),Format=False,PDF = pdf)
        notification('Hello Capabilities Exchanged!!')
            
        ###############################################################################
        ## Create_subscription
        ###############################################################################
        filter = """<filter type="xpath" xmlns="urn:ietf:params:xml:ns:netconf:notification:1.0" xmlns:notf_c="urn:ietf:params:xml:ns:yang:ietf-netconf-notifications" select="/notf_c:*"/>"""
        cap=self.session.create_subscription(filter=filter)
        STARTUP.STORE_DATA('> subscribe --filter-xpath /ietf-netconf-notifications:*', Format=True, PDF=pdf)
        dict_data = xmltodict.parse(str(cap))
        if dict_data['nc:rpc-reply']['nc:ok'] == None:
            STARTUP.STORE_DATA('\nOk\n', Format=False, PDF=pdf)
        notification('Subscription with netconf-config filter performed!!')
           

        pdf.add_page()
        ###############################################################################
        ## Test Procedure 1
        ###############################################################################
        Test_Step1 = '\t\t***********step 1 and 2 Retrival of ru information with filter **********'
        STARTUP.STORE_DATA('{}'.format(Test_Step1),Format='TEST_STEP',PDF = pdf)
        STARTUP.STORE_DATA("get --filter-xpath /o-ran-usermgmt:users/user",Format=True,PDF = pdf)
        u_name = '''
                <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <users xmlns="urn:o-ran:user-mgmt:1.0">	
                    <user>                                                        
                        
                    </user>
                </users>
                </filter>
        '''
        
        ###############################################################################
        ## Get the RU details with filter
        ###############################################################################
        user_name = self.session.get_config('running', u_name).data_xml
        x = xml.dom.minidom.parseString(user_name)
        xml_pretty_str = x.toprettyxml()
        STARTUP.STORE_DATA(xml_pretty_str,Format='XML',PDF = pdf)
        notification('Performed Get Operation with filter!!')
        return True   

                
    ###############################################################################
    ## Main Function
    ###############################################################################
    def test_Main_011(self):
        notification("Test Case M_CTC_ID_011 is under process...")
        Check1 = self.linked_detected()
        
        # print(self.hostname)
        ###############################################################################
        ## Read User Name and password from Config.INI of Config.py
        ###############################################################################
        self.USER_N = configur.get('INFO','sudo_user')
        self.PSWRD = configur.get('INFO','sudo_pass')
        if Check1 == False or Check1 == None:
            return Check1
        pkt = sniff(iface = self.interface, stop_filter = self.check_tcp_ip, timeout = 100)
        # return False
        try:
            STARTUP.delete_system_log(host = self.hostname)
            time.sleep(2)
            ###############################################################################
            ## Perform call home to get ip_details
            ###############################################################################
            self.session, self.login_info = STARTUP.session_login(host = self.hostname,USER_N = self.USER_N,PSWRD = self.PSWRD)

            
            if self.session:
                RU_Details = STARTUP.demo(session = self.session,host= self.hostname, port= 830)
            
                for key, val in RU_Details[1].items():
                    if val[0] == 'true' and val[1] == 'true':
                        
                        ###############################################################################
                        ## Test Description
                        ###############################################################################
                        Test_Desc = 'Test Description : This scenario validates that the O-RU NETCONF Server properly executes a get command with a filter applied.'
                        CONFIDENTIAL = STARTUP.ADD_CONFIDENTIAL('11',SW_R = val[2]) 
                        STARTUP.STORE_DATA(CONFIDENTIAL,Format='CONF',PDF= pdf)
                        STARTUP.STORE_DATA(Test_Desc,Format='DESC',PDF= pdf)
                        pdf.add_page()
                time.sleep(5)
                result = self.test_procedure()
                print(result)

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
            

                     
    
def test_m_ctc_id_011():
    tc011_obj = M_CTC_ID_011()
    Check = tc011_obj.test_Main_011()
    if Check == False:
        STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
        STARTUP.STORE_DATA('{}'.format('SFP link Not Detected...'),Format=False,PDF= pdf)
        STARTUP.ACT_RES(f"{'Retrieval with filter applied' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(255,0,0))
        notification('FAIL_REASON :SFP link not detected...')
        notification(f"{'Retrieval with filter applied' : <50}{'=' : ^20}{'FAIL' : ^20}")
        return False
    
    ###############################################################################
    ## Expected/Actual Result
    ###############################################################################
    STARTUP.GET_SYSTEM_LOGS(tc011_obj.hostname,tc011_obj.USER_N,tc011_obj.PSWRD,pdf)
    Exp_Result = 'Expected Result : The O-RU NETCONF Server responds with <rpc-reply><data> where <data> contains details for objects as conforming to the <filter>.'
    STARTUP.STORE_DATA(Exp_Result,Format='DESC',PDF= pdf)

    STARTUP.STORE_DATA('\t\t{}'.format('****************** Actual Result ******************'),Format=True,PDF= pdf)
    try:
        if Check == True:
            STARTUP.ACT_RES(f"{'Retrieval with filter applied' : <50}{'=' : ^20}{'SUCCESS' : ^20}",PDF= pdf,COL=(0,255,0))
            notification(f"{'Retrieval with filter applied' : <50}{'=' : ^20}{'PASS' : ^20}")
            return True

        elif type(Check) == list:
            STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
            Error_Info = '''ERROR\n\terror-type \t: \t{}\n\terror-tag \t: \t{}\n\terror-severity \t: \t{}\n\tmessage' \t: \t{}'''.format(*map(str,Check))
            STARTUP.STORE_DATA(Error_Info,Format=False,PDF= pdf)
            STARTUP.ACT_RES(f"{'Retrieval with filter applied' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(255,0,0))
            notification("FAIL_REASON : {}".format(Error_Info))
            notification(f"{'Retrieval with filter applied' : <50}{'=' : ^20}{'FAIL' : ^20}")
            return False
        else:
            STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
            STARTUP.STORE_DATA('{}'.format(Check),Format=False,PDF= pdf)
            STARTUP.ACT_RES(f"{'Retrieval with filter applied' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(255,0,0))
            notification("FAIL_REASON : {}".format(Check))
            notification(f"{'Retrieval with filter applied' : <50}{'=' : ^20}{'FAIL' : ^20}")
            return False


    except Exception as e:
            STARTUP.STORE_DATA('{}'.format(e), Format=True,PDF=pdf)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(
                f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
            notification("FAIL_REASON : {}".format(e))
            notification(f"{'Retrieval with filter applied' : <50}{'=' : ^20}{'FAIL' : ^20}")
            return False


    ###############################################################################
    ## For Capturing the logs
    ###############################################################################
    finally:
        STARTUP.CREATE_LOGS('M_CTC_ID_011',PDF=pdf)
        notification("Successfully completed Test Case M_CTC_ID_011. Logs captured !!")



if __name__ == "__main__":
    start_time = time.time()
    test_m_ctc_id_011()
    end_time = time.time()
    print('Execution Time is : {}'.format(int(end_time-start_time)))
    pass

