###############################################################################
##@ FILE NAME:      Using the NETCONF client transfer the generated counter files from O-RAN/PM/ folder  in O-RU
##@ TEST SCOPE:     M PLANE O-RAN Functional
##@ Version:        V_1.0.0
##@ Support:        @Ramiyer, @VaibhavDhiman, @PriyaSharma
###############################################################################

###############################################################################
## Package Imports 
###############################################################################

import sys, os, time, xmltodict, xml.dom.minidom, paramiko
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

class create_subscribe(performance_activation):

    def __init__(self) -> None:
        super().__init__()
        self.rx_measurement_interval, self.transceiver_measurement_interval, self.notification_measurement_interval, self.file_measurement_interval = 120, 60, 240, 120
        


    def session_login(self):
        try:
            ###############################################################################
            ## Capture The notification in loop
            ###############################################################################
            self.session_login_activate()
            pdf_log.add_page()
            Test_Step2 = '\t\tO-RU NETCONF Server sends <notification><download-event> with status COMPLETED to TER NETCONF Client'
            STARTUP.STORE_DATA('{}'.format(Test_Step2),Format='TEST_STEP',PDF=pdf_log)
            # t = time.time() + self.rx_measurement_interval + self.transceiver_measurement_interval + self.notification_measurement_interval + self.file_measurement_interval
            t = time.time() + 240
            while t> time.time():
                n = self.session.take_notification(timeout = t)
                if n == None:
                    break
                notify = n.notification_xml
                dict_n = xmltodict.parse(str(notify))
                try:
                    notf = dict_n['notification']['netconf-config-change']
                except:
                    x = xml.dom.minidom.parseString(notify)
                    xml_pretty_str = x.toprettyxml()
                    STARTUP.STORE_DATA(xml_pretty_str, Format='XML',PDF=pdf_log)
                    pass
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
           
    def verify_csv_file(self):
        try:
            host = self.hostname
            port = 22
            username = configur.get('INFO','super_user')
            print(username)
            password = configur.get('INFO','super_pass')
            print(password)
            command = "ls /media/sd-mmcblk0p4/O-RAN/PM/"
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(host, port, username, password)

            stdin, stdout, stderr = ssh.exec_command(command)
            lines = stdout.readlines()

        except Exception as e:
            print(e)
            print('Can\'t connect to RU..')
        pass


    def test_main(self):
        try:
            del self.slots['swRecoverySlot']
            
            for key, val in self.slots.items():
                if val[0] == 'true' and val[1] == 'true':
                    ############################### Test Description #############################
                    Test_Desc = '''Test Description : 1. Open the NETCONF client.
2. Send the rpc <edit-config> with below parameters
2.a SFTP-upload as TRUE, 
2.b file-upload-interval 
2.c remote-SFTP-upload-path
2.d SFTP credentials 
3. Wait for the rpc reply message for successful configurations.
4. Open the uploaded counter files on SFTP server. '''
                    CONFIDENTIAL = STARTUP.ADD_CONFIDENTIAL(filename,SW_R = val[2]) 
                    STARTUP.STORE_DATA(CONFIDENTIAL,Format='CONF',PDF= pdf_log)
                    STARTUP.STORE_DATA(Test_Desc,Format='DESC',PDF= pdf_log)
                    pdf_log.add_page()
                    pass


            
            
            time.sleep(5)
            result = self.session_login()

            STARTUP.GET_SYSTEM_LOGS(self.host,self.USER_N,self.PSWRD,pdf_log,number=500)
                         
            Exp_Result = '''Expected Result : 1. Verify the NETCONF client is opened successfully.
2. Verify the <edit-config> is configures succesfully with any error messages.
3. Verify the files are uploaded in the SFTP server file path.  
4. Verify the .csv file name of the performance management as below format: 
Eg: C201805181300+0900_201805181330+0900_ABC0123456.csv.
5. Verify the measurement results in each lines are below format. 
Eg:1, RX_ON_TIME, 2018-05-18T13:00:00+09:00, 2018-05-18T13:30:00+09:00, 0, 123, AAAA, 1, 123, BBBB, 2, 123, CCCC, 3, 123,
DDDD
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
                STARTUP.ACT_RES(f"{'Using the NETCONF client transfer the generated counter files from O-RAN/PM/ folder  in O-RU' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf_log,COL=(255,0,0))
                return result
                
            else:
                STARTUP.ACT_RES(f"{'Using the NETCONF client transfer the generated counter files from O-RAN/PM/ folder  in O-RU' : <50}{'=' : ^20}{'PASS' : ^20}",PDF= pdf_log,COL=(105, 224, 113))
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
        obj = create_subscribe()
        filename = sys.argv[1]
        Result = obj.test_main()
    except Exception as e:
        STARTUP.STORE_DATA('{}'.format(e), Format = True,PDF=pdf_log)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(
            f"Error occured in line number {exc_tb.tb_lineno}", Format = False,PDF=pdf_log)
        print('Usage: python create_subscribe.py <Test_Case_ID> <Fronthaul Interface Eg. eth0/eth1> <element name eg. element0/element1> <bandwidths Eg. 10> <remote_path eg. sftp://vvdn@192.168.4.15:22/home/vvdn>')
    
    