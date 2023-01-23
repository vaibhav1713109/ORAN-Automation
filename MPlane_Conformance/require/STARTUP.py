import os, sys, xmltodict
from ncclient import manager
import paramiko
from datetime import datetime
from tabulate import tabulate
from fpdf import FPDF
from pathlib import Path
from configparser import ConfigParser
import time,socket
import logging
from warnings import warn
from binascii import hexlify

logger = logging.getLogger('ncclient.manager')

###############################################################################
## Directory Path
###############################################################################
dir_name = os.path.dirname(os.path.abspath(__file__))
parent = os.path.dirname(dir_name)
# print(parent)
# print(dir_name)
sys.path.append(parent)

########################################################################
## For reading data from .ini file
########################################################################
configur = ConfigParser()
configur.read('{}/Conformance/inputs.ini'.format(parent))

###############################################################################
## Related Imports
###############################################################################
from require.Vlan_Creation import *
from require import Config




class PDF(FPDF):

    def header(self):
        self.image('{}/vvdn_logo.png'.format(dir_name), 10, 8, 33)
        self.set_text_color(44, 112, 232)
        self.set_font('Arial', 'B', 15)
        self.set_x(-45)
        self.set_font('Times', 'B', 12)
        self.cell(10,10, 'M Plane Conformance', 0, 0, 'C')
        self.set_text_color(0,0,0)
        self.ln(20)


    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(0,0,0)
        self.cell(0, 10, 'Page %s' % self.page_no(), 0, 0, 'L')
        self.set_text_color(44, 112, 232)
        self.set_font('Arial', 'B', 8)
        self.cell(0, 10, 'Copyright (c) 2016 - 2022 VVDN Technologies Pvt Ltd', 0, 0, 'R')
        self.cell(0,10)
        self.set_text_color(0,0,0)


def call_home(*args, **kwds):
    host = kwds["host"]
    port = kwds.get("port",4334)
    timeout = kwds["timeout"]
    srv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv_socket.bind((host, port))
    srv_socket.settimeout(timeout)
    srv_socket.listen()

    sock, remote_host = srv_socket.accept()
    logger.info('Callhome connection initiated from remote host {0}'.format(remote_host))
    kwds['sock'] = sock
    srv_socket.close()
    return manager.connect_ssh(*args, **kwds)

###############################################################################
## Check Ping and DHCP Status
###############################################################################
def ping_status(ip_address):
    response = os.system("ping -c 5 " + ip_address)
    # self.ping = subprocess.getoutput(f'ping {ip_address} -c 5')
    if response == 0:
        return True
    else:
        return False


###############################################################################
## SFP Link Detection
###############################################################################
def sfp_Linked():
    ## Check Point 1
    Check1 = True
    interface_name = vlan_Creation().linked_detected()
    if interface_name:
        pass
    else:
        Check1 = False
    return Check1



def colonify(fp):
    fp = fp.decode('UTF-8')
    finga = fp[:2]
    for idx in range(2, len(fp), 2):
        finga += ":" + fp[idx:idx+2]
    return finga

###############################################################################
## Collecting required infromation
###############################################################################
def demo(session,host, port):
    
        # Fetching all the users
        u_name = '''
        <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            <users xmlns="urn:o-ran:user-mgmt:1.0">	
            </users>
        </filter>'''


        get_u = session.get(u_name).data_xml
        dict_u = xmltodict.parse(str(get_u))
        u = {}
        try:
            users = dict_u['data']['users']['user']
            for i in users:
                name = i['name']                
                pswrd = i['password']
                if name:
                    u[name] = u.get(pswrd,0)
                
        except:
            pass

        sw_inv = '''<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            <software-inventory xmlns="urn:o-ran:software-management:1.0">
            </software-inventory>
            </filter>'''
        s = {}
        slot_names = session.get(sw_inv).data_xml
        dict_slot = xmltodict.parse(str(slot_names))
        try:
            slots = dict_slot['data']['software-inventory']['software-slot']
            for k in slots:
                active_s = k['active']
                running_s = k['running']
                slot_name = k['name']
                sw_build = k['build-version']
                slot_status = k['status']
                s[slot_name] = [active_s,running_s,sw_build,slot_status]

        except:
            print("User doesn't have SUDO permission")


        # Fetching all the interface and MAC
        v_name1 = '''
                <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
                </interfaces>
                </filter>
        '''

        interface_name = session.get_config('running', v_name1).data_xml
        dict_interface = xmltodict.parse(str(interface_name))
        Interfaces = dict_interface['data']['interfaces']['interface']
        #STORE_DATA(Interfaces,OUTPUT_LIST)
        d = {}
        ma = {}

        
        for i in Interfaces:
            name = i['name']
            mac = i['mac-address']['#text']
            try:
                IP_ADD = i['ipv4']['address']['ip']
                if name:
                    d[name] = IP_ADD
                    ma[name] = mac
            except:
                pass
        return [u, s, ma, d]
        # return [u, s, ma, d]

###############################################################################
## Sesssion Login
###############################################################################
def session_login(host = '0.0.0.0',USER_N = '',PSWRD = ''):
    try:
        session = call_home(host = '0.0.0.0', port=4334, hostkey_verify=False,username = USER_N, password = PSWRD,timeout = 60,allow_agent = False , look_for_keys = False)
        hostname, call_home_port = session._session._transport.sock.getpeername()   #['ip_address', 'TCP_Port']
        server_key_obj = session._session._transport.get_remote_server_key()
        fingerprint = colonify(hexlify(server_key_obj.get_fingerprint()))
        login_info = f'''> listen --ssh --login {USER_N}
                Waiting 60s for an SSH Call Home connection on port 4334...
                The authenticity of the host '::ffff:{hostname}' cannot be established.
                ssh-rsa key fingerprint is {fingerprint}
                Interactive SSH Authentication done.'''.strip()
        
    except Exception as e:
        warn('Call Home is not initiated!!!!!! So it will try with connect command!!!!')
        session = manager.connect(host = host, port=830, hostkey_verify=False,username = USER_N, password = PSWRD,timeout = 60,allow_agent = False , look_for_keys = False)
        server_key_obj = session._session._transport.get_remote_server_key()
        fingerprint = colonify(hexlify(server_key_obj.get_fingerprint()))
        login_info = f'''> connect --ssh --host {host} --port 830 --login {USER_N}
                ssh-rsa key fingerprint is {fingerprint}
                Interactive SSH Authentication done. 
                        '''
    return session, login_info


def delete_system_log(host):
    for _ in range(5):
        try:
            host = host
            port = 22
            username = configur.get('INFO','super_user')
            password = configur.get('INFO','super_pass')
            command = "rm -rf {};".format(configur.get('INFO','syslog_path'))
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(host, port, username, password)

            stdin, stdout, stderr = ssh.exec_command(command)
            lines = stdout.readlines()
            return True
        except Exception as e:
            print(e)
            pass
    else:
        print('Can\'t connect to the RU.., Logs are not captured.')

###############################################################################
## Collecting the system logs
###############################################################################
def GET_SYSTEM_LOGS(host,user, pswrd,PDF):
    for _ in range(5):
        try:
            host = host
            port = 22
            username = user
            password = pswrd
            PDF.add_page()
            STORE_DATA('\t\t\t\t############ SYSTEM LOGS ##############',Format=True,PDF=PDF)
            command = "cat {};".format(configur.get('INFO','syslog_path'))
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(host, port, username, password)

            stdin, stdout, stderr = ssh.exec_command(command)
            lines = stdout.readlines()
            for i in lines:
                STORE_DATA("{}".format(i),Format=False,PDF=PDF)
            PDF.add_page()
            return True
        except Exception as e:
            print(e)
            pass
    else:
        print('Can\'t connect to the RU.., Logs are not captured.')


###############################################################################
## Filename genration
###############################################################################
def GET_LOGS_NAME(TC_Name):
    s = datetime.now()
    return f"{TC_Name}_{s.hour}_{s.minute}_{s.second}_{s.day}_{s.month}_{s.year}"

###############################################################################
## for storing data into pdf as well as shown to the console
###############################################################################
def STORE_DATA(*datas,Format,PDF):
    for data in datas:
        if Format == True:
            print('='*100)
            print(data)
            print('='*100)
            HEADING(PDF,data)

        elif Format == 'XML':
            print(data)
            XML_FORMAT(PDF,data)

        elif Format == 'CONF':
            print('='*100)
            print(data)
            print('='*100)
            CONFDENTIAL(PDF,data)
        
        elif Format == 'DESC':
            print('='*100)
            print(data)
            print('='*100)
            Test_desc(PDF,data)

        elif Format == 'TEST_STEP':
            print('='*100)
            print(data)
            print('='*100)
            Test_Step(PDF,data)

        else:
            print(data)
            PDF.write(h=5,txt=data)


###############################################################################
## Creating pdf into 'LOGS' directory
###############################################################################
def CREATE_LOGS(File_name,PDF):
    pdf = PDF_CAP()
    LOG_NAME = GET_LOGS_NAME(File_name)
    file1 = f"{parent}/LOGS/{configur.get('INFO','ru_name_rev')}/{LOG_NAME}.pdf"
    PDF.output(file1)


###############################################################################
## Add Confidential for Radio Unit
###############################################################################
def ADD_CONFIDENTIAL(TC,SW_R):

    CONF = '''    

     @ FILE NAME:    M_CTC_ID_0{0}.txt \n                                                           
     @ TEST SCOPE:    M PLANE O-RAN CONFORMANCE \n
     @ Software Release for {1}: \t v{2}                          
     '''.format(TC,configur.get('INFO','ru_name_rev'),SW_R,'*'*70)
    return CONF


###############################################################################
## Style sheet for test description
###############################################################################
def Test_desc(PDF,data):
     PDF.set_font("Times",style = 'B', size=13)
     PDF.set_text_color(17, 64, 37)
     PDF.multi_cell(w =180,h = 10,txt='{}'.format(data),border=1,align='L')
     PDF.set_font("Times",style = '',size = 9)
     PDF.set_text_color(0, 0, 0)
     pass



###############################################################################
## Status of Netopeer-cli
###############################################################################
def STATUS(host,user,session_id,port):
    STATUS = f'''
            > status
            Current NETCONF session:
            ID          : {session_id}
            Host        : {host}
            Port        : {port}
            Transport   : SSH
            Capabilities:
            '''
    return STATUS



###############################################################################
## Initialize PDF
###############################################################################
def PDF_CAP():
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Times", size=9)
    y = int(pdf.epw)
    pdf.image(name='{}/Front_Page.png'.format(dir_name), x = None, y = None, w = y, h = 0, type = '', link = '')
    pdf.ln(10)
    return pdf


###############################################################################
## Stylesheet for heading
###############################################################################
def HEADING(PDF,data,*args):
    PDF.set_font("Times",style = 'B', size=11)
    PDF.write(5, '\n{}\n'.format('='*75))
    PDF.write(5,data)
    PDF.write(5, '\n{}\n'.format('='*75))
    PDF.set_font("Times",style = '',size = 9)



###############################################################################
## Stylesheet for XML
###############################################################################
def XML_FORMAT(PDF,data):
    PDF.set_text_color(199, 48, 83)
    PDF.write(5,data)
    PDF.set_text_color(0, 0, 0)


###############################################################################
## Stylesheet for Confidential
###############################################################################
def CONFDENTIAL(PDF,data):
     PDF.set_font("Times",style = 'B', size=15)
     PDF.set_text_color(10, 32, 71)
     PDF.multi_cell(w =180,txt=data,border=1,align='L')
     PDF.set_font("Times",style = '',size = 9)
     PDF.set_text_color(0, 0, 0)
     PDF.ln(30)
     pass

###############################################################################
## Stylesheet for test setps
###############################################################################
def Test_Step(PDF,data):
    PDF.set_font("Times",style = 'B', size=12)
    PDF.set_text_color(125, 93, 65)
    PDF.write(5, '\n{}\n'.format('='*75))
    PDF.write(5,txt=data)
    PDF.write(5, '\n{}\n'.format('='*75))
    PDF.set_font("Times",style = '',size = 9)
    PDF.set_text_color(0,0,0)


###############################################################################
## Stylesheet for dhcp server
###############################################################################
def DHCP_Status(PDF,data):
    data = data.split('writable')
    #print(data)
    abs_path = os.path.join('{}/dejavu-fonts-ttf-2.37/ttf/'.format(parent),'DejaVuSans.ttf')
    PDF.add_font('DejaVu', '', abs_path, uni=True)
    PDF.set_font("DejaVu",'', size=9)
    STORE_DATA("\t DHCP Status",Format=True,PDF = PDF)
    if len(data) == 2:
        datas = data[1][2:350]+data[1][362:]
    else:
        datas = data[0][2:350]+data[0][362:]
    print(datas)
    PDF.write(5,datas)
    PDF.set_font("Times",style = '',size = 9)

###############################################################################
## Stylesheet for actual result
###############################################################################
def ACT_RES(data,PDF,COL):
    print('='*100)
    print(data)
    print('='*100)
    PDF.set_font("Times",style = 'B', size=12)
    PDF.set_fill_color(COL[0],COL[1],COL[2])
    PDF.write(5, '\n{}\n'.format('='*75))
    PDF.multi_cell(w =PDF.epw,txt=data,border=1,align='L',fill=True)
    PDF.write(5, '\n{}\n'.format('='*75))
    PDF.set_font("Times",style = '',size = 9)
    PDF.set_fill_color(255,255,255)


###############################################################################
## Stylesheet for table
###############################################################################
def TABLE(Header,Data,PDF):
    ACT_RES = tabulate(Data,Header,tablefmt='fancy_grid')
    print(ACT_RES)
    render_header(PDF,Header)
    render_table_data(PDF,Data)

def render_header(PDF,TABLE_Header):
    line_height=10
    col_width=45
    PDF.set_font("Times",style="B")  # enabling bold text
    for col_name in TABLE_Header:
        PDF.cell(col_width, line_height, col_name, border=1,align='C')
    PDF.ln(line_height)
    PDF.set_font(style="")  # disabling bold text

def render_table_data(PDF,TABLE_DATA):  # repeat data rows
    line_height=10
    col_width=45
    for row in TABLE_DATA:
        for datum in row:
            PDF.multi_cell(col_width, line_height, datum, border=1,
                new_x="RIGHT", new_y="TOP", max_line_height=PDF.font_size,align='C')
        PDF.ln(line_height)




if __name__ == "__main__":
    delete_system_log('192.168.149.37')

