###############################################################################
##@ FILE NAME:      Get Without Filter
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
configur.read('{}/require/inputs.ini'.format(parent))

###############################################################################
## Related Imports
###############################################################################
from require import STARTUP
# from require.Vlan_Creation import *
from require.Notification import *
from require.LINK_DETECTED import *


###############################################################################
## Initiate PDF
###############################################################################
pdf = STARTUP.PDF_CAP()
summary = []


class get_without_filter(Link_Detect):

    # init method or constructor
    def __init__(self) -> None:
        super().__init__()
        self.interface_name = ''
        self.hostname, self.call_home_port = '',''
        self.USER_N = ''
        self.PSWRD = ''
        self.session = ''

    ###############################################################################
    ## Test Execution and Procedure
    ###############################################################################
    def Test_Execcution(self):
        STARTUP.STORE_DATA('\n\n\t\t********** Connect to the NETCONF Server ***********\n\n',Format='TEST_STEP',PDF = pdf)
        STARTUP.STORE_DATA(self.login_info,Format=False,PDF = pdf)
        STATUS = STARTUP.STATUS(self.hostname,self.USER_N,self.session.session_id,830)
        STARTUP.STORE_DATA(STATUS,Format=False,PDF = pdf)

        ###############################################################################
        ## Server Capabilities
        ###############################################################################
        for cap in self.session.server_capabilities:
            STARTUP.STORE_DATA("\t{}".format(cap),Format=False,PDF = pdf)
        summary.append('Hello Capabilities Exchanged || Successful')
        print('-'*100)
        print(summary[-1])
            
        ###############################################################################
        ## Create_subscription
        ###############################################################################
        filter = """<filter type="xpath" xmlns="urn:ietf:params:xml:ns:netconf:notification:1.0" xmlns:notf_c="urn:ietf:params:xml:ns:yang:ietf-netconf-notifications" select="/notf_c:*"/>"""
        cap=self.session.create_subscription(filter=filter)
        STARTUP.STORE_DATA('> subscribe --filter-xpath /ietf-netconf-notifications:*', Format=True, PDF=pdf)
        dict_data = xmltodict.parse(str(cap))
        if dict_data['nc:rpc-reply']['nc:ok'] == None:
            STARTUP.STORE_DATA('\nOk\n', Format=False, PDF=pdf)
        summary.append('Subscription with netconf-config filter || Successful')
        print('-'*100)
        print(summary[-1])  

        pdf.add_page()
        ###############################################################################
        ## Test Procedure 1
        ###############################################################################
        Test_Step1 = '\t\t Step 1 The TER NETCONF Client triggers <rpc><get> towards the O-RU NETCONF Server.'
        STARTUP.STORE_DATA('{}'.format(Test_Step1),Format = 'TEST_STEP',PDF=pdf)
        STARTUP.STORE_DATA('{}'.format('> get'), Format = True,PDF=pdf)
        
        ###############################################################################
        ## Test Procedure 2
        ###############################################################################
        Test_Step2 = '\t\t Step 2 The O-RU NETCONF Server responds with <rpc-reply><data> where <data> contains all information elements that the O-RU NETCONF Server is able to expose'
        STARTUP.STORE_DATA(
            '{}'.format(Test_Step2), Format = 'TEST_STEP',PDF=pdf)


        ###############################################################################
        ## Get the RU details without filter
        ###############################################################################
        Data = self.session.get(filter=None, with_defaults=None).data_xml
        x = xml.dom.minidom.parseString(Data)
        xml_pretty_str = x.toprettyxml()
        STARTUP.STORE_DATA(xml_pretty_str, Format = 'XML',PDF=pdf)
        summary.append('Get Operation without filter || Successful')
        print('-'*100)
        print(summary[-1])
        return True



    ###############################################################################
    ## Main Function
    ###############################################################################
    def Main_Function(self):
        print(f'{"-"*100}\nCheck the Link Detection')
        Check1 = self.link_detected()
        Result = STARTUP.check_link_and_ping_dhcp_either_static(Check1,pdf,self.INTERFACE_NAME,summary)
        if not Result[-1]:
            return Result[0]
        self.hostname = Result[0]

        ###############################################################################
        ## Read User Name and password from Config.INI of Config.py
        ###############################################################################
        self.USER_N = configur.get('INFO','sudo_user')
        self.PSWRD = configur.get('INFO','sudo_pass')


        try:
            time.sleep(5)
            STARTUP.delete_system_log(host= self.hostname)
            ###############################################################################
            ## Perform call home to get ip_details
            ###############################################################################
            self.session, self.login_info = STARTUP.session_login(host = self.hostname,USER_N = self.USER_N,PSWRD = self.PSWRD)
            # self.hostname, self.call_home_port = self.session._session._transport.sock.getpeername()   #['ip_address', 'TCP_Port'] +
            
            if self.session:
                summary.append('Netopeer Connection || Successful')
                print('-'*100)
                print(summary[-1])
                self.RU_Details = STARTUP.Software_detail(session = self.session)

                for key, val in self.RU_Details.items():
                    if val[0] == 'true' and val[1] == 'true':

                        ###############################################################################
                        ## Test Description
                        ###############################################################################
                        Test_Desc = 'Test Description : This scenario validates that the O-RU NETCONF Server properly executes a general get command.'
                        CONFIDENTIAL = STARTUP.ADD_CONFIDENTIAL('Get Without Filter', SW_R=val[2])
                        STARTUP.STORE_DATA(CONFIDENTIAL, Format = 'CONF',PDF=pdf)
                        STARTUP.STORE_DATA(Test_Desc,Format = 'DESC',PDF= pdf)
                        pdf.add_page()

                STARTUP.STORE_DATA('{}'.format(Result[1][0]).center(100),Format=True,PDF=pdf)
                STARTUP.STORE_DATA(Result[1][1],Format=False,PDF=pdf)
                STARTUP.STORE_DATA('{}'.format("ping -c 5 {}".format(self.hostname)).center(100),Format=True,PDF=pdf)
                STARTUP.STORE_DATA(Result[1][2],Format=False,PDF=pdf)
                result = self.Test_Execcution()
                if result == True:
                    return True
                else:
                    return result


        ###############################################################################
        ## Exception
        ###############################################################################
        except socket.timeout as e:
            Error = '{} : Call Home is not initiated, SSH Socket connection lost....'.format(e)
            STARTUP.STORE_DATA(Error, Format=True,PDF=pdf)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
            return Error

        except RPCError as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
            return [e.type, e.tag, e.severity, e.path, e.message, exc_tb.tb_lineno]

        except Exception as e:
            STARTUP.STORE_DATA('{}'.format(e), Format=True,PDF=pdf)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
            return e
            
        finally:
            try:
                self.session.close_session()
            except Exception as e:
                print(e)

        

    

def Result_Declartion():
    tc010_obj = get_without_filter()
    Check = tc010_obj.Main_Function()
    if Check == False:
        STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
        STARTUP.STORE_DATA('{}'.format('SFP Link not detected..'),Format=False,PDF= pdf)
        STARTUP.ACT_RES(f"{'Get without Filter' : <50}{'||' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(235, 52, 52))
        summary.append('FAIL_REASON || SFP link not detected')
        print('-'*100)
        print(summary[-1])
        summary.append(f"{'Get without Filter' : <50}{'||' : ^20}{'FAIL' : ^20}")
        print('-'*100)
        print(summary[-1])
        return False

    ###############################################################################
    ## Expected/Actual Result and System Logs
    ###############################################################################
    STARTUP.GET_SYSTEM_LOGS(tc010_obj.hostname,tc010_obj.USER_N,tc010_obj.PSWRD,pdf)
    Exp_Result = 'Expected Result : The O-RU NETCONF Server responds with <rpc-reply><data> where <data> contains all information elements that the O-RU NETCONF Server is able to expose'
    STARTUP.STORE_DATA(Exp_Result,Format = 'DESC',PDF= pdf)

    STARTUP.STORE_DATA('\t\t{}'.format('****************** Actual Result ******************'),Format = True,PDF= pdf)
    try:
        if Check == True:
            STARTUP.ACT_RES(f"{'Get without Filter' : <50}{'||' : ^20}{'SUCCESS' : ^20}",PDF= pdf,COL=(105, 224, 113))
            summary.append(f"{'Get without Filter' : <50}{'||' : ^20}{'PASS' : ^20}")
            print('-'*100)
            print(summary[-1])
            return True
            
        elif type(Check) == list:
            STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
            Error_Info = '''\terror-tag \t: \t{}\n\terror-type \t: \t{}\n\terror-severity \t: \t{}\n\tDescription' \t: \t{}'''.format(*map(str,Check))
            STARTUP.STORE_DATA(Error_Info,Format=False,PDF= pdf)
            STARTUP.ACT_RES(f"{'Get without Filter' : <50}{'||' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(235, 52, 52))
            summary.append("FAIL_REASON || {}".format(Error_Info))
            print('-'*100)
            print(summary[-1])
            summary.append(f"{'Get without Filter' : <50}{'||' : ^20}{'FAIL' : ^20}")
            print('-'*100)
            print(summary[-1])
            return False
        else:
            STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
            STARTUP.STORE_DATA('{}'.format(Check),Format=False,PDF= pdf)
            STARTUP.ACT_RES(f"{'Get without Filter' : <50}{'||' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(235, 52, 52))
            summary.append("FAIL_REASON || {}".format(Check))
            print('-'*100)
            print(summary[-1])
            summary.append(f"{'Get without Filter' : <50}{'||' : ^20}{'FAIL' : ^20}")
            print('-'*100)
            print(summary[-1])
            return False


    except Exception as e:
            STARTUP.STORE_DATA('{}'.format(e), Format=True,PDF=pdf)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
            summary.append("FAIL_REASON || {}".format(e))
            print('-'*100)
            print(summary[-1])
            summary.append(f"{'Get without Filter' : <50}{'||' : ^20}{'FAIL' : ^20}")
            print('-'*100)
            print(summary[-1])
            return False


    ###############################################################################
    ## For Capturing the logs
    ###############################################################################
    finally:
        STARTUP.HEADING(PDF=pdf,data='{0} Summary {0}'.format('*'*30))
        STARTUP.render_table_data(pdf,STARTUP.append_data(summary)) 
        STARTUP.CREATE_LOGS('Get_Without_Filter',PDF=pdf) 

if __name__ == "__main__":
    start_time = datetime.fromtimestamp(int(time.time()))
    Test_procedure = [f"{'='*100}\nTest case *Get Without Filter* Started!! Status: Running\n{'='*100}",'** Test Coverage **'.center(50),'Static IP Ping',
                'Netopeer Connection','Capability exchange','Create-subscription','Apply Get with out filter', 'Start Time : {}'.format(start_time),'='*100]
    notification('\n'.join(Test_procedure))
    Result = Result_Declartion()
    end_time = datetime.fromtimestamp(int(time.time()))
    st_time = 'Start Time : {}'.format(start_time)
    en_time = 'End Time : {}'.format(end_time)
    execution_time = 'Execution Time is : {}'.format(end_time-start_time)
    print('-'*100)
    print(f'{st_time}\n{en_time}\n{execution_time}')
    summary.insert(0,'******* Result *******'.center(50))
    summary.insert(0,'='*100)
    notification('\n'.join(summary[:-1]))
    notification(f'{st_time}\n{en_time}\n{execution_time}')
    notification(f"{'='*100}\n{summary[-1]}\n{'='*100}")
    if Result != True:
        sys.exit(1)
