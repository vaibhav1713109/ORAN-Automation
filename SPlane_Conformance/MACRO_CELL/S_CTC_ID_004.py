from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys ,os
import socket
import json
from ncclient import manager
import xmltodict
import xml.dom.minidom
import time
import paramiko
import STARTUP
from scp import SCPException
from paramiko import SSHClient
from scp import SCPClient
from calnexRest import calnexInit,calnexSet
pdf = STARTUP.PDF_CAP(TC = "04")
d1 = os.path.dirname(os.path.realpath(__file__))

def kill_ssn(host, port, user, password,sid):
     with manager.connect(host=host, port=port, username=user, hostkey_verify=False, password=password) as m:
         m.kill_session(sid)
        
def session_login(host, port, user, password):
    try:
        with manager.connect(host=host, port=port, username=user, hostkey_verify=False, password=password) as m:

            
            STARTUP.STORE_DATA('********** Connect to the NETCONF Server ***********',Format = True,PDF = pdf)
        
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
            rpc=m.create_subscription()
        
            STARTUP.STORE_DATA('>subscribe',Format = True,PDF = pdf)
        
            dict_data = xmltodict.parse(str(rpc))
            if dict_data['nc:rpc-reply']['nc:ok']== None:
                STARTUP.STORE_DATA('ok',Format = False,PDF = pdf)
        
            STARTUP.STORE_DATA("Initial configuratin of O-RU",Format = True,PDF = pdf)
        
        
            SYNC = '''<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            <sync xmlns="urn:o-ran:sync:1.0">
            </sync>
            </filter>
            '''
            data1  = m.get(SYNC).data_xml
            x = xml.dom.minidom.parseString(data1)
            xml_pretty_str = x.toprettyxml()
            STARTUP.STORE_DATA(xml_pretty_str,Format = "XML",PDF = pdf)
            calnexSet("app/mse/master/Master1/start")
            time.sleep(10)
            driver = webdriver.Chrome('/home/vvdn/Downloads/chromedriver_linux641/chromedriver')
            driver.get("http://" + f"{data['Paragon_IP']}")
            driver.minimize_window()
            # # driver.maximize_window()
            time.sleep(10)

            pdf.add_page()
            element = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='trackContainerTracksNode']/track-master-slave-emulation/div/div[2]/div[2]/div/div[1]/div/div[1]/div[3]/div/div[4]/div[3]/div/div[1]/div"))).get_attribute("class")
            if element == "detected":
                
                pdf.add_page()
                STARTUP.STORE_DATA('Enable ptp and syncE for nomainal ptp and nominal syncE',Format = True,PDF = pdf)

                STARTUP.Open_window()
                STARTUP.clock_class_6()
                pdf.image(name=f'{d1}'+'/PTP_ON.png', x = None, y = None, w = 180, h = 70, type = '', link = '')
                pdf.ln(5)
                pdf.image(name=f'{d1}'+'/clock_class_6.png', x = None, y = None, w = 180, h = 70, type = '', link = '')
                pdf.ln(5)
                time.sleep(2)
                 # calnexSet("app/generation/synce/esmc/Port1/start")
                 # time.sleep(10)
                STARTUP.SYNCE_PRC()
                time.sleep(2)
                pdf.image(name=f'{d1}'+'/SYNCE_PRC.png', x = None, y = None, w = 180, h = 70, type = '', link = '')
                pdf.ln(5)
                
                pdf.add_page()
                STARTUP.STORE_DATA('capturing notifications for ptp , synce and ru-sync states',Format = True,PDF = pdf)

                while True:
                         n = m.take_notification()
                         notify=n.notification_xml
                         dict_notify = xmltodict.parse(str(notify))
                         input_dict =  dict_notify
                         output_dict = json.loads(json.dumps(input_dict)) 
                         def recursive_items(dictionary):
                             for key, value in dictionary.items():
                                 if type(value) is dict:
                                     yield from recursive_items(value)
                                 else:
                                     yield (key, value)
                         for key, value in recursive_items(output_dict):
                             NF1 = key
                         if NF1=='synce-state':
                             s = xml.dom.minidom.parseString(notify)
                             xml_pretty_str = s.toprettyxml()
                             STARTUP.STORE_DATA(xml_pretty_str,Format = "XML",PDF = pdf)
                             break
                STARTUP.STORE_DATA("-"*50,Format=False, PDF = pdf)        
                
                while True:
                     n = m.take_notification()
                     notify=n.notification_xml
                     dict_notify = xmltodict.parse(str(notify))
                     input_dict =  dict_notify
                     output_dict = json.loads(json.dumps(input_dict)) 
                     def recursive_items(dictionary):
                         for key, value in dictionary.items():
                             if type(value) is dict:
                                 yield from recursive_items(value)
                             else:
                                 yield (key, value)
                     for key, value in recursive_items(output_dict):
                         NF1 = key
                    
                     if NF1=='sync-state':
                         s = xml.dom.minidom.parseString(notify)
                         xml_pretty_str = s.toprettyxml()
                         STARTUP.STORE_DATA(xml_pretty_str,Format = "XML",PDF = pdf)
                         break
                STARTUP.STORE_DATA("-"*50,Format=False, PDF = pdf) 
                while True:
                     n = m.take_notification()
                     notify=n.notification_xml
                     dict_notify = xmltodict.parse(str(notify))
                     input_dict =  dict_notify
                     output_dict = json.loads(json.dumps(input_dict))  
                     def recursive_items(dictionary):
                         for key, value in dictionary.items():
                             if type(value) is dict:
                                 yield from recursive_items(value)
                             else:
                                 yield (key, value)
                     for key, value in recursive_items(output_dict):
                         NF1 = key
                     if NF1=='ptp-state':
                         s = xml.dom.minidom.parseString(notify)
                         xml_pretty_str = s.toprettyxml()
                         STARTUP.STORE_DATA(xml_pretty_str,Format = "XML",PDF = pdf)
                         break

                pdf.add_page() 
                STARTUP.STORE_DATA('Retriving the nominal Clock class and nominal ssm code',Format = True,PDF = pdf)  
                
                SYNC = '''<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                 <sync xmlns="urn:o-ran:sync:1.0">
                 </sync>
                 </filter>
                 '''
                data1  = m.get(SYNC).data_xml
                x = xml.dom.minidom.parseString(data1)
                xml_pretty_str = x.toprettyxml()
                STARTUP.STORE_DATA(xml_pretty_str,Format = "XML",PDF = pdf)
                                
                pdf.add_page()  
                #give clock class 140 from paragon
                STARTUP.STORE_DATA("configure clock class 140 from Master",Format = True,PDF = pdf)
                # calnexSet("app/mse/master/Master2/clockclass", "ClockClass", 140)
                # calnexSet("app/mse/applypending")
                        # STARTUP.clock_class_140()
                pdf.image(name=f'{d1}'+'/clock_class_140.png', x = None, y = None, w = 180, h = 70, type = '', link = '')
                pdf.ln(5)
                time.sleep(15)
                    
                SYNC = '''<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <sync xmlns="urn:o-ran:sync:1.0">
                </sync>
                </filter>
                '''
                        
                data1  = m.get(SYNC).data_xml
                x = xml.dom.minidom.parseString(data1)
                xml_pretty_str = x.toprettyxml()
                STARTUP.STORE_DATA(xml_pretty_str,Format = "XML",PDF = pdf)
                        
                pdf.add_page()
                #give clock class 150 from paragon
                STARTUP.STORE_DATA("configure clock class 150 from Master",Format = True,PDF = pdf)
                # calnexSet("app/mse/master/Master2/clockclass", "ClockClass", 150)
                # calnexSet("app/mse/applypending")
                        # STARTUP.clock_class_150()
                pdf.image(name=f'{d1}'+'/clock_class_150.png', x = None, y = None, w = 180, h = 70, type = '', link = '')
                pdf.ln(5)
                time.sleep(15)
                

                SYNC = '''<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <sync xmlns="urn:o-ran:sync:1.0">
                </sync>
                </filter>
                '''
                data1  = m.get(SYNC).data_xml
                x = xml.dom.minidom.parseString(data1)
                xml_pretty_str = x.toprettyxml()
                STARTUP.STORE_DATA(xml_pretty_str,Format = "XML",PDF = pdf)
                        
                pdf.add_page()
                #give clock class 160 from paragon
                        # STARTUP.STORE_DATA("configure clock class 160 from Master",Format = True,PDF = pdf)
                # calnexSet("app/mse/master/Master2/clockclass", "ClockClass", 160)
                # calnexSet("app/mse/applypending")
                        #   STARTUP.clock_class_160()
                time.sleep(2)
                pdf.image(name=f'{d1}'+'/clock_class_160.png', x = None, y = None, w = 180, h = 70, type = '', link = '')
                pdf.ln(5)
                time.sleep(15)
                
                
                SYNC = '''<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <sync xmlns="urn:o-ran:sync:1.0">
                </sync>
                </filter>
                '''
                data1  = m.get(SYNC).data_xml
                x = xml.dom.minidom.parseString(data1)
                xml_pretty_str = x.toprettyxml()
                STARTUP.STORE_DATA(xml_pretty_str,Format = "XML",PDF = pdf)
                        
                pdf.add_page()
                #changing the Domain number 
                STARTUP.STORE_DATA('changing the Domain number to 25',Format = True,PDF = pdf)
                # calnexSet("app/mse/master/Master2/domain", "Domain", 25)
                # calnexSet("app/mse/applypending")
                STARTUP.domain()
                pdf.image(name=f'{d1}'+'/domain.png', x = None, y = None, w = 180, h = 70, type = '', link = '')
                pdf.ln(5)
                time.sleep(2)
                STARTUP.STORE_DATA('Holdover Notification',Format = True,PDF = pdf)
                while True:
                    n = m.take_notification()
                    notify=n.notification_xml
                    dict_notify = xmltodict.parse(str(notify))
                    input_dict =  dict_notify
                    output_dict = json.loads(json.dumps(input_dict))  
                    def recursive_items(dictionary):
                        for key, value in dictionary.items():
                            if type(value) is dict:
                                yield from recursive_items(value)
                            else:
                                yield (key, value)
                    for key, value in recursive_items(output_dict):
                        NF1 = key
                    if NF1=='sync-state':
                        s = xml.dom.minidom.parseString(notify)
                        xml_pretty_str = s.toprettyxml()
                        STARTUP.STORE_DATA(xml_pretty_str,Format = "XML",PDF = pdf)
                        break
                        
                STARTUP.STORE_DATA('Retrieving the holdover state of RU',Format = True,PDF = pdf)
                        
                        
                SYNC = '''<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <sync xmlns="urn:o-ran:sync:1.0">
                </sync>
                </filter>
                '''
                data1  = m.get(SYNC).data_xml
                x = xml.dom.minidom.parseString(data1)
                xml_pretty_str = x.toprettyxml()
                STARTUP.STORE_DATA(xml_pretty_str,Format = "XML",PDF = pdf)
                global dict_Sync1
                dict_Sync1 = xmltodict.parse(str(data1))
                # STARTUP.STORE_DATA('FREERUN NOTIFICATION',Format = True,PDF = pdf)
                time.sleep(900)

                pdf.add_page()
                STARTUP.STORE_DATA('FREERUN NOTIFICATION',Format = True,PDF = pdf)

                while True:
                    n = m.take_notification()
                    notify=n.notification_xml
                    dict_notify = xmltodict.parse(str(notify))
                    input_dict =  dict_notify
                    output_dict = json.loads(json.dumps(input_dict))  
                    def recursive_items(dictionary):
                        for key, value in dictionary.items():
                            if type(value) is dict:
                                yield from recursive_items(value)
                            else:
                                yield (key, value)
                    for key, value in recursive_items(output_dict):
                        NF1 = key
                    if NF1=='sync-state':
                        s = xml.dom.minidom.parseString(notify)
                        xml_pretty_str = s.toprettyxml()
                        STARTUP.STORE_DATA(xml_pretty_str,Format = "XML",PDF = pdf)
                        break
                STARTUP.STORE_DATA('Retrieving the Freerun state of RU',Format = True,PDF = pdf)

                        
                SYNC = '''<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <sync xmlns="urn:o-ran:sync:1.0">
                </sync>
                </filter>
                '''
                        
                data1  = m.get(SYNC).data_xml
                x = xml.dom.minidom.parseString(data1)
                xml_pretty_str = x.toprettyxml()
                STARTUP.STORE_DATA(xml_pretty_str,Format = "XML",PDF = pdf)
                    
            else:
                STARTUP.STORE_DATA("Device not detected",Format = False,PDF = pdf)
    except Exception as e:
        STARTUP.STORE_DATA(e,Format = False,PDF = pdf)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA('Error Line Number:',{exc_tb.tb_lineno},Format = False,PDF = pdf)
        

def Result_Decleration(host, port, user, password):
    try:
        with manager.connect(host=host, port=port, username=user, hostkey_verify=False, password=password) as m:
            STARTUP.STORE_DATA('RESULTS',Format = True,PDF = pdf)
            SYNC = '''
                <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <sync xmlns="urn:o-ran:sync:1.0">
                </sync>
                </filter>
            '''

            value_SYNC = m.get(SYNC).data_xml

            dict_Sync = xmltodict.parse(str(value_SYNC))
            Sync_state=dict_Sync1['data']['sync']['sync-status']['sync-state']
                    
            STARTUP.STORE_DATA(f"{'Sync_state STATUS' : <50}{'=' : ^20}{'PASS' : ^20}" if Sync_state == "HOLDOVER" else f"{'Sync_state STATUS' : <50}{'=' : ^20}{'FAIL' : ^20}",Format = False,PDF = pdf)
                    
            Ptp_lock_state=dict_Sync1['data']['sync']['ptp-status']['lock-state']
            STARTUP.STORE_DATA(f"{'Ptp_lock_state STATUS' : <50}{'=' : ^20}{'PASS' : ^20}" if Ptp_lock_state == "LOCKED" or "UNLOCKED" else f"{'Ptp_lock_state STATUS' : <50}{'=' : ^20}{'FAIL' : ^20}",Format = False,PDF = pdf)
                    
            Ptp_state=dict_Sync1['data']['sync']['ptp-status']['sources']['state']
            STARTUP.STORE_DATA(f"{'Ptp_state STATUS' : <50}{'=' : ^20}{'PASS' : ^20}" if Ptp_state == "NOK" else f"{'Ptp_state STATUS' : <50}{'=' : ^20}{'FAIL' : ^20}",Format = False,PDF = pdf)
                    
            SyncE_lock_state=dict_Sync['data']['sync']['synce-status']['lock-state']
            STARTUP.STORE_DATA(f"{'SyncE_lock_state STATUS' : <50}{'=' : ^20}{'PASS' : ^20}" if SyncE_lock_state == "LOCKED" else f"{'SyncE_lock_state STATUS' : <50}{'=' : ^20}{'FAIL' : ^20}",Format = False,PDF = pdf)

            SyncE_state=dict_Sync['data']['sync']['synce-status']['sources']['state']
            STARTUP.STORE_DATA(f"{'SyncE_State STATUS' : <50}{'=' : ^20}{'PASS' : ^20}" if SyncE_state == "PARENT" else f"{'SyncE_state STATUS' : <50}{'=' : ^20}{'FAIL' : ^20}",Format = False,PDF = pdf)
    except Exception as e:
        STARTUP.STORE_DATA(e,Format = False,PDF = pdf)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA('Error Line Number:',{exc_tb.tb_lineno},Format = False,PDF = pdf)


def CREATE_LOGS(PDF,name):
     name1 = str(path) + "/" +str(name) + ".pdf"
     PDF.output(name1)

if __name__ == '__main__':
    calnexInit("172.17.80.4")
    try:
        f = open(f'{d1}/details.json')
        data = json.load(f)

  # str1 = curr_place.split('-')
  # f"{data['Username']}" = str1[0]
  # f"{data['password']}" = str1[1]
  # m = manager.call_home(host = '', port=4334, hostkey_verify=False,username =f"{data['Username']}", password =f"{data['password']}")

  # li = m._session._transport.sock.getpeername()
  # sid = m.session_id
  # kill_ssn("192.168.1.10",830,f"{data['Username']}",f"{data['password']}",sid)
        
  # res = session_login("192.168.1.10",830,f"{data['Username']}",f"{data['password']}")
    
        res = session_login("192.168.1.10",830,f"{data['Username']}",f"{data['password']}")
        pdf.add_page()
        STARTUP.STORE_DATA('SYSTEM LOGS',Format = True,PDF = pdf)
                
                
        command = f"cd /media/sd-mmcblk0p4; cat {data['Log_file_name']} | grep SYNCMNGR;"
        command1 = f"cd /media/sd-mmcblk0p4; rm -rf {data['Log_file_name']};"
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname="192.168.1.10",username=data["root_Username"],password=data["root_password"])
        stdin, stdout, stderr = ssh_client.exec_command(command)
        lines = stdout.readlines()
        for i in lines:
            STARTUP.STORE_DATA(i,Format = "XML",PDF = pdf)
        stdin, stdout, stderr = ssh_client.exec_command(command1)
        Result_Decleration("192.168.1.10",830,f"{data['Username']}",f"{data['password']}")
        # path = input('Enter the path to save SI LAB logs =')
        path = data['File_path']
        Remote_path= path + "/TC4.log"
        ssh_ob = SSHClient()
        ssh_ob.load_system_host_keys()
        ssh_ob.connect(hostname="192.168.1.10",username=f"{data['Username']}",password=f"{data['password']}")
        scp = SCPClient(ssh_ob.get_transport())
        scp.get('/var/log/slabtimingptp2.log',Remote_path)
        scp.close()
        CREATE_LOGS(pdf,name = "S_CTC_ID_004")
            # stdin, stdout, stderr = ssh_client.exec_command(command2)
            # time.sleep(150)
    except SCPException as e:
        STARTUP.STORE_DATA("File Not found in RU",Format = False,PDF = pdf)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA('Error Line Number:',{exc_tb.tb_lineno},Format = False,PDF = pdf)
    except UnicodeError as e:
        STARTUP.STORE_DATA(e,"Please give correct Ip address",Format = False,PDF = pdf)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA('Error Line Number:',{exc_tb.tb_lineno},Format = False,PDF = pdf)

    except paramiko.ssh_exception.AuthenticationException as e:
        STARTUP.STORE_DATA(e,"Please give correct username or password",Format = False,PDF = pdf)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA('Error Line Number:',{exc_tb.tb_lineno},Format = False,PDF = pdf)

    except socket.timeout as e:
        STARTUP.STORE_DATA(e,"Call Home could not complete",Format = False,PDF = pdf)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA('Error Line Number:',{exc_tb.tb_lineno},Format = False,PDF = pdf)
    
    except Exception as e:
        STARTUP.STORE_DATA(e,Format = True,PDF = pdf)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA('Error Line Number:',{exc_tb.tb_lineno},Format = False,PDF = pdf)

    calnexSet("app/mse/master/Master1/clockclass", "ClockClass", 6)
    calnexSet("app/mse/applypending")
    calnexSet("app/generation/synce/esmc/Port1/ssm", "SsmValue", 'QL-PRC')
    calnexSet("app/mse/master/Master1/stop")
    calnexSet("app/generation/synce/esmc/Port1/stop")
    calnexSet("app/mse/master/Master1/domain", "Domain", 24)
    calnexSet("app/mse/applypending")
