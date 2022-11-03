import socket
import sys, os
import time
from tkinter.messagebox import NO
from ncclient import manager
import subprocess
from ncclient.transport import errors
from paramiko.ssh_exception import NoValidConnectionsError
from ncclient.operations.errors import TimeoutExpiredError
from ncclient.transport.errors import SessionCloseError
import STARTUP, ifcfg, random, Config
import DHCP_CONF.ISC_DHCP_SERVER as ISC_DHCP_SERVER
import DHCP_CONF.DHCP_CONF_VLAN as DHCP_CONF_VLAN
from tabulate import tabulate


pdf = STARTUP.PDF_CAP()

class M_CTC_id_001():

    def __init__(self,host, port, user, pswrd):
        self.host = host
        self.port = port
        self.user = user
        self.pswrd = pswrd
         

    # Call Home initialization----
    def Call_Home(self):
        Test_Step1 = '\tThe O-RU NETCONF Serve  establishes TCP connection and performs a Call Home procedure towards the NETCONF Client and establishes a SSH.'
        STARTUP.STORE_DATA('{}'.format(Test_Step1),Format='TEST_STEP',PDF = pdf)
        m1 = manager.call_home(host='', port=4334, username=self.user , hostkey_verify=False, password=self.pswrd, timeout = 60,allow_agent = False , look_for_keys = False)
        li = m1._session._transport.sock.getpeername()   #['ip_address', 'TCP_Port']
        LISTEN = f'''> listen --ssh --login {self.user }\nWaiting 60s for an SSH Call Home connection on port 4334...'''
        STARTUP.STORE_DATA(LISTEN,Format=False,PDF = pdf)
        try:
            if m1:
                query = 'yes'
                str_out = f'''The authenticity of the host '::ffff:{li[0]}' cannot be established.
                ssh-rsa key fingerprint is 59:9e:90:48:f1:d7:6e:35:e8:d1:f6:1e:90:aa:a3:83:a0:6b:98:5a.
                Are you sure you want to continue connecting (yes/no)? yes'''
                STARTUP.STORE_DATA(str_out,Format=False,PDF = pdf)
                if query == 'yes':
                    STARTUP.STORE_DATA(f'''\n{self.user }@::ffff:{li[0]} password: \n''',Format=False,PDF = pdf)
                    Test_Step2 = "\tTER NETCONF Client and O-RU NETCONF Server exchange capabilities through the NETCONF <hello> messages"
                    STARTUP.STORE_DATA('{}'.format(Test_Step2),Format='TEST_STEP',PDF = pdf)
                    STARTUP.STORE_DATA(f'''> status\nCurrent NETCONF session:\nID\t: {m1.session_id}\nHost\t: :ffff:{li[0]}\nPort\t: {li[1]}\nTransport\t: SSH\nCapabilities:''',Format=False,PDF = pdf)
                    for i in m1.server_capabilities:
                        STARTUP.STORE_DATA(i,Format=False,PDF = pdf)
                    return [m1.session_id, li]
            else:
                m1.close()
        
            
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA("\t\t{}".format(e),Format=False,PDF = pdf)
            return  f"{e} \nError occured in line number {exc_tb.tb_lineno}"

       
    

############################# Create Random Vlan for VLAN Scanning ############################
def create_vlan(name,v_id):
        time.sleep(10)
        obj = ISC_DHCP_SERVER.test_DHCP_CONF()
        obj.test_read(name,v_id)
        obj1 = DHCP_CONF_VLAN.test_DHCP_CONF()
        IPADDR = obj1.test_read()
        VLAN_NAME = '{}.{}'.format(name,v_id)
        d = os.system(f'sudo ip link add link {name} name {name}.{v_id} type vlan id {v_id}')
        d = os.system(f'sudo ifconfig {name}.{v_id} {IPADDR} up')
        d = os.system('sudo /etc/init.d/isc-dhcp-server restart')
        st = subprocess.getoutput('sudo /etc/init.d/isc-dhcp-server status')
        li_of_interfaces = list(ifcfg.interfaces().keys())
        if VLAN_NAME in li_of_interfaces:
            return True,IPADDR
        else:
            return False,IPADDR
        
        

########################## Check Which interface is Linked ##################################
def ethtool_linked(interface):
                # STARTUP.STORE_DATA(interface,OUTPUT_LIST=OUTPUT_LIST)
    cmd = "sudo ethtool " + interface
    # STARTUP.STORE_DATA(cmd,OUTPUT_LIST=OUTPUT_LIST)
    gp = os.popen(cmd)
    fat=gp.read().split('\n')
    for line in fat:
        # STARTUP.STORE_DATA(line,OUTPUT_LIST=OUTPUT_LIST)
        if "Speed" in line and ('25000' in line or '10000' in line):
            return interface



########################### Check Link is detected or not ####################################
def linked_detected():
    while True:
        inter = ifcfg.interfaces()
        Interface = list(inter.keys())
        for i in Interface:
            if '.' not in i:
                if ethtool_linked(i):
                    s = ethtool_linked(i)
                    if s !=None:
                        return s



def PINGING(hostname):
    STARTUP.STORE_DATA("\t ########### Pinging ###########",Format=True,PDF = pdf)
    response = os.system("ping -c 5 " + hostname)
    #and then check the response...
    if response == 0:
        return True
    else:
        return False


########################### Check DHCP status ############################
def DHCP_STATUS(IPADDRES):
    li_st = IPADDRES.split('.')
    subnet = '{0}.{1}.{2}'.format(li_st[0],li_st[1],li_st[2])
    while True:
        st = subprocess.getoutput('sudo /etc/init.d/isc-dhcp-server status')
        st = st.split('\n')
        for i in st:
            if 'DHCPREQUEST' in i:
                # print(i)
                if subnet in i:
                    return True




########################### Main Function ############################
def test_MAIN_FUNC_001():
    vlan_id = random.randint(20,22)
    ################################### Check Point 1 {Link Detected} #####################################
    interface_name = linked_detected()
    if interface_name:
        Res1 = True

    
    ################################### Check Point 2 {VLAN Created} #####################################
    Res2 = create_vlan(interface_name,vlan_id)

    ################################### Check Subnet in Dhcp Status ##########################################
    Res = DHCP_STATUS(Res2[1])
    time.sleep(5)
    j = 20
    if vlan_id> j:
        j = vlan_id
    USER_N = Config.details['SUDO_USER'] 
    PSWRD = Config.details['SUDO_PASS'] 


    try:
        ############################## Perform call home to get ip_details #################################

        m = manager.call_home(host = '', port=4334, hostkey_verify=False,username = USER_N, password = PSWRD,timeout = 60,allow_agent = False , look_for_keys = False)
        li = m._session._transport.sock.getpeername()   #['ip_address', 'TCP_Port']
        sid = m.session_id
        
        if m:
            
            obj = M_CTC_id_001(li[0],830,USER_N,PSWRD)
            STARTUP.kill_ssn(li[0], 830, USER_N, PSWRD,sid)
            time.sleep(10)
            RU_Details = STARTUP.demo(li[0], 830, USER_N, PSWRD)
            
            for key, val in RU_Details[1].items():
                    if val[0] == 'true' and val[1] == 'true':
                        

                        ############################### Test Description #############################
                        Test_Desc = '''This scenario validates that the O-RU properly executes the session establishment procedure \nwith VLANs and a DHCPv4 server. This test is applicable to IPv4 environments.'''
                        CONFIDENTIAL = STARTUP.ADD_CONFIDENTIAL('01',SW_R = val[2]) 
                        STARTUP.STORE_DATA(CONFIDENTIAL,Format='CONF',PDF= pdf)
                        STARTUP.STORE_DATA(Test_Desc,Format='DESC',PDF= pdf)
                        pdf.add_page()



            ############################## VLAN of Test PC ######################################
            STARTUP.STORE_DATA("\t Interfaces Present in DU Side",Format=True,PDF= pdf)
            ip_config = subprocess.getoutput('ifconfig')
            STARTUP.STORE_DATA(ip_config,Format='XML',PDF= pdf)



            pdf.add_page()
            ############################### DHCP Status #############################
            STARTUP.STORE_DATA("\t DHCP Status",Format=True,PDF = pdf)
            st = subprocess.getoutput('sudo /etc/init.d/isc-dhcp-server status')
            STARTUP.DHCP_Status(data=st,PDF = pdf)




            ############################### Check Ping of VLAN IP ################################
            # For pinging vlan ip and perform call home feature
            st = subprocess.getoutput(f'ping {li[0]} -c 5')
            Res3 = PINGING(li[0])
            STARTUP.STORE_DATA(st,Format=False,PDF = pdf)



            
            pdf.add_page()
            time.sleep(10)
            res = obj.Call_Home()
            time.sleep(10)

            # For Capturing the logs
            ############################### Expected/Actual Result ####################################################
            STARTUP.GET_SYSTEM_LOGS(li[0],USER_N,PSWRD,pdf)
            Exp_Result = 'Expected Result : The TER NETCONF Client and O-RU NETCONF Server exchange capabilities through NETCONF <hello> messages.'
            STARTUP.STORE_DATA(Exp_Result,Format='DESC',PDF= pdf)

            STARTUP.STORE_DATA('\t\t{}'.format('****************** Actual Result ******************'),Format=True,PDF= pdf)
        
            if type(res) == str:
                STARTUP.STORE_DATA('{0} FAIL_REASON {0}'.format('*'*20),Format=True,PDF= pdf)
                Error_Info = '''\terror-tag \t: \t{}\n\terror-type \t: \t{}\n\terror-severity \t: \t{}\n\tDescription' \t: \t{}'''.format(*map(str,res))
                STARTUP.STORE_DATA(Error_Info,Format=False,PDF= pdf)
                STARTUP.ACT_RES(f"{'Perform_Call_Home' : <50}{'=' : ^20}{'FAIL' : ^20}",PDF= pdf,COL=(235, 52, 52))
                return Error_Info
                # raise '\t\tFAIL-REASON\t\n{}'.format(Error_Info)
            else:
                # For Capturing the logs
                STARTUP.kill_ssn(li[0], 830, USER_N, PSWRD,res[0])

                STARTUP.ACT_RES(f"{'Perform_Call_Home' : <50}{'=' : ^20}{'SUCCESS' : ^20}",PDF= pdf,COL=(105, 224, 113))
                # Table = ['Check Points', 'Result']
                # Result = [['Linked Detected','PASS' if Res1 else 'FAIL'],['VLAN Created','PASS' if Res2 else 'FAIL'],['PINGING','PASS' if Res3 else 'FAIL','PASS'],['Call Home','PASS' if res else 'FAIL']]
                # STARTUP.TABLE(Table,Result,PDF=pdf)
                return True
            
    
    ############################### Known Exceptions ####################################################
    except socket.timeout as e:
        Error = '{} : Call Home is not initiated, SSH Socket connection lost....'.format(
            e)
        STARTUP.STORE_DATA(Error, Format=True,PDF=pdf)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(
            f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
        return Error
        # raise socket.timeout('{}: SSH Socket connection lost....'.format(e)) from None

    except errors.SSHError as e:
        Error = '{} : SSH Socket connection lost....'.format(e)
        STARTUP.STORE_DATA(Error, Format=True,PDF=pdf)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(
            f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
        return Error
        # raise errors.SSHError('{}: SSH Socket connection lost....'.format(e)) from None

    except errors.AuthenticationError as e:
        Error = "{} : Invalid username/password........".format(e)
        STARTUP.STORE_DATA(Error, Format=True,PDF=pdf)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(
            f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
        return Error
        # raise f'{e} : Invalid username/password........'

    except NoValidConnectionsError as e:
        Error = '{} : ...'.format(e)
        STARTUP.STORE_DATA(Error, Format=True,PDF=pdf)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(
            f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
        return Error
        # raise e

    except TimeoutError as e:
        Error = '{} : Call Home is not initiated, Timout Expired....'.format(e)
        STARTUP.STORE_DATA(Error, Format=True,PDF=pdf)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(
            f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
        return Error
        # raise f'{e} : Call Home is not initiated, Timout Expired....'

    except SessionCloseError as e:
        Error = "{} : Unexpected_Session_Closed....".format(e)
        STARTUP.STORE_DATA(Error, Format=True,PDF=pdf)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(
            f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
        return Error
        # raise f'{e},Unexpected_Session_Closed....'

    except TimeoutExpiredError as e:
        Error = "{} : TimeoutExpiredError....".format(e)
        STARTUP.STORE_DATA(Error, Format=True,PDF=pdf)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(
            f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
        return Error
        # raise e

    except OSError as e:
        Error = '{} : Call Home is not initiated, Please wait for sometime........'.format(
            e)
        STARTUP.STORE_DATA(Error, Format=True,PDF=pdf)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(
            f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
        return Error
        # raise Exception('{} : Please wait for sometime........'.format(e)) from None

    except Exception as e:
        STARTUP.STORE_DATA('{}'.format(e), Format=True,PDF=pdf)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(
            f"Error occured in line number {exc_tb.tb_lineno}", Format=False,PDF=pdf)
        return e
        # raise Exception('{}'.format(e)) from None


    ############################### MAKE PDF File ####################################################
    finally:
        time.sleep(80)
        STARTUP.CREATE_LOGS('M_CTC_ID_001',PDF=pdf)

        
        
        # except:
        #         time.sleep(20)
        #         pass

if __name__ == '__main__':
    if test_MAIN_FUNC_001() == True:
        pass
    else:
        pass
