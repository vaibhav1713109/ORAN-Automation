import socket , os
import STARTUP
import json
import sys
from ncclient import manager
import xmltodict
import xml.dom.minidom
import time
import paramiko
from scp import SCPException
from paramiko import SSHClient
from scp import SCPClient
from calnexRest import calnexInit

pdf = STARTUP.PDF_CAP(TC = "1")
d1 = os.path.dirname(os.path.realpath(__file__))
print(d1)
def kill_ssn(host, port, user, password,sid):
    with manager.connect(host=host, port=port, username=user, hostkey_verify=False, password=password) as m:
        m.kill_session(sid)

def session_login(host, port, user, password):
    try:
        with manager.connect(host=host, port=port, username=user, hostkey_verify=False, password=password) as m:
            STARTUP.STORE_DATA('Step 1 Connect to the NETCONF Server',Format = True,PDF = pdf)
            STARTUP.STORE_DATA(f'''> connect --ssh --host {host} --port 830 --login {user}
                    Interactive SSH Authentication
                    Type your password:
                    Password: 
                    > status
                    Current NETCONF session:
                    ID          : {m.session_id}
                    Host        : {host}
                    Port        : {port}
                    Transport   : SSH
                    Capabilities:
                    ''',Format = False,PDF = pdf)
            for i in m.server_capabilities:
                STARTUP.STORE_DATA(i,Format = False,PDF = pdf)

            cap = m.create_subscription()
            pdf.add_page()
            STARTUP.STORE_DATA('>subscribe',Format = True,PDF = pdf)
            dict_data = xmltodict.parse(str(cap))
            if dict_data['nc:rpc-reply']['nc:ok']== None:
                STARTUP.STORE_DATA('Ok',Format = False,PDF = pdf)
            pdf.ln(5)

            STARTUP.STORE_DATA('Step 1 PTP and syncE both are in Passive state',Format = True,PDF = pdf)
            STARTUP.PTP_OFF()
            pdf.image(name = f"{d1}"+'/PTP_OFF.png', x = None, y = None, w = 180, h = 70, type = '', link = '')
            pdf.ln(5)
            time.sleep(2)

            STARTUP.SYNCE_NONE()
            pdf.image(name=f"{d1}"+'/SYNCE_NONE.png', x = None, y = None, w = 180, h = 70, type = '', link = '')
            pdf.ln(8)
            STARTUP.STORE_DATA('Step 2 Freerun State of O-RU in Startup Condition',Format = True,PDF = pdf)
            SYNC = '''<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            <sync xmlns="urn:o-ran:sync:1.0">
            </sync>
            </filter>
            '''
        
            data1  = m.get(SYNC).data_xml
            x = xml.dom.minidom.parseString(data1)
            

            xml_pretty_str = x.toprettyxml()
            # STARTUP.STORE_DATA('Expected Result',Format = True,PDF = pdf)
            STARTUP.STORE_DATA(xml_pretty_str,Format = "XML",PDF= pdf)
    
    except Exception as e:
        STARTUP.STORE_DATA(f"{e}",Format = "TEST_STEP",PDF = pdf)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA('Error Line Number:',f'{exc_tb.tb_lineno}',Format = "TEST_STEP",PDF = pdf)

def Result_Decleration(host, port, user, password):
    try:
        with manager.connect(host=host, port=port, username=user, hostkey_verify=False, password=password) as m:
            pdf.add_page()
            STARTUP.STORE_DATA('RESULTS',Format =True,PDF = pdf)
            SYNC = '''
                <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <sync xmlns="urn:o-ran:sync:1.0">
                </sync>
                </filter>
                '''
       
            value_SYNC = m.get(SYNC).data_xml
 
            dict_Sync = xmltodict.parse(str(value_SYNC))
            Sync_state=dict_Sync['data']['sync']['sync-status']['sync-state']

            STARTUP.STORE_DATA(f"{'Sync_state STATUS' : <50}{'=' : ^20}{'PASS' : ^20}" if Sync_state == "FREERUN" else f"{'Sync_state STATUS' : <50}{'=' : ^20}{'FAIL' : ^20}",Format = False,PDF = pdf)
            
            Ptp_lock_state=dict_Sync['data']['sync']['ptp-status']['lock-state']
            STARTUP.STORE_DATA(f"{'Ptp_lock_state STATUS' : <50}{'=' : ^20}{'PASS' : ^20}" if Ptp_lock_state == "UNLOCKED" else f"{'Ptp_lock_state STATUS' : <50}{'=' : ^20}{'FAIL' : ^20}",Format = False,PDF = pdf)
            
            Ptp_state=dict_Sync['data']['sync']['ptp-status']['sources']['state']
            STARTUP.STORE_DATA(f"{'Ptp_state STATUS' : <50}{'=' : ^20}{'PASS' : ^20}" if Ptp_state == "DISABLED" else f"{'Ptp_state STATUS' : <50}{'=' : ^20}{'FAIL' : ^20}",Format = False,PDF = pdf)
            
            SyncE_lock_state=dict_Sync['data']['sync']['synce-status']['lock-state']
            STARTUP.STORE_DATA(f"{'SyncE_lock_state STATUS' : <50}{'=' : ^20}{'PASS' : ^20}" if SyncE_lock_state == "UNLOCKED" else f"{'SyncE_lock_state STATUS' : <50}{'=' : ^20}{'FAIL' : ^20}",Format = False,PDF = pdf)

            SyncE_state=dict_Sync['data']['sync']['synce-status']['sources']['state']
            STARTUP.STORE_DATA(f"{'SyncE_State STATUS' : <50}{'=' : ^20}{'PASS' : ^20}" if SyncE_state == "DISABLED" else f"{'SyncE_state STATUS' : <50}{'=' : ^20}{'FAIL' : ^20}",Format = False,PDF = pdf)
    except Exception as e:
        STARTUP.STORE_DATA(f"{e}",Format = "TEST_STEP",PDF = pdf)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA('Error Line Number:',f'{exc_tb.tb_lineno}',Format = False,PDF = pdf)

def CREATE_LOGS(PDF,name):
    name1 = str(path) + "/" +str(name) + ".pdf"
    PDF.output(name1)

if __name__ == '__main__':
    calnexInit("172.17.80.4")
    try:
        f = open(f'{d1}/details.json')
        data = json.load(f)
        m = manager.call_home(host = '', port=4334, hostkey_verify=False,username =f"{data['Username']}", password =f"{data['password']}")
        li = m._session._transport.sock.getpeername()
        sid = m.session_id
        kill_ssn(li,830,f"{data['Username']}",f"{data['password']}",sid)
        res = session_login(li[0],830,f"{data['Username']}",f"{data['password']}")   
        pdf.add_page()
        STARTUP.STORE_DATA('SYSTEM LOGS',Format = True,PDF = pdf)
        command = f"cd /media/sd-mmcblk0p4; cat {data['Log_file_name']} | grep SYNCMNGR;"
        command1 = f"cd /media/sd-mmcblk0p4; rm -rf {data['Log_file_name']};"
        # command2 = "rureset"
        pdf.add_page()
        # STARTUP.STORE_DATA("Result Decleration",Format =True,PDF = pdf)
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=li[0],username=f"{data['Username']}",password=f"{data['password']}")

        stdin, stdout, stderr = ssh_client.exec_command(command)
        lines = stdout.readlines()
        for i in lines:
            STARTUP.STORE_DATA(i,Format ="XML",PDF = pdf)
        stdin, stdout, stderr = ssh_client.exec_command(command1)
        

        Result_Decleration(li[0],830,f"{data['Username']}",f"{data['password']}")
        path = data['File_path']
        Remote_path= path + "/TC1.log"
        ssh_ob = SSHClient()
        ssh_ob.load_system_host_keys()
        ssh_ob.connect(hostname=li[0],username=data["root_Username"],password=data["root_password"])
        scp = SCPClient(ssh_ob.get_transport())
        scp.get('/var/log/slabtimingptp2.log',Remote_path)
        scp.close()
        CREATE_LOGS(pdf,name = "S_CTC_ID_001")
        # stdin, stdout, stderr = ssh_client.exec_command(command2)
        # time.sleep(150)
   
    except SCPException as e:
        STARTUP.STORE_DATA("File Not found in RU",Format = False,PDF = pdf)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA('Error Line Number:',f'{exc_tb.tb_lineno}',Format =False,PDF = pdf)     

    except UnicodeError as e:
        STARTUP.STORE_DATA(f"{e}","Please give correct Ip address",Format =False,PDF = pdf)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA('Error Line Number:',f'{exc_tb.tb_lineno}',Format = False,PDF = pdf)

    except paramiko.ssh_exception.AuthenticationException as e:
        STARTUP.STORE_DATA(f"{e}","Please give correct username or password",Format =False,PDF = pdf)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA('Error Line Number:',f'{exc_tb.tb_lineno}',Format = False,PDF = pdf)

    except socket.timeout as e:
        STARTUP.STORE_DATA(f'{e}',Format = False,PDF = pdf)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA('Error Line Number:',f'{exc_tb.tb_lineno}',Format = False,PDF = pdf)
    
    except Exception as e:
        STARTUP.STORE_DATA(f'{e}',Format = "TEST_STEP",PDF = pdf)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA('Error Line Number:',f'{exc_tb.tb_lineno}',Format = False,PDF = pdf)