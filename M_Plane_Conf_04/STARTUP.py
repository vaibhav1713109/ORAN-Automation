import os
from ncclient import manager
import xmltodict,Config
import paramiko
from datetime import datetime
from tabulate import tabulate
from fpdf import FPDF




def kill_ssn(host, port, user, password,sid):
    with manager.connect(host=host, port=port, username=user, hostkey_verify=False, password=password, allow_agent = False , look_for_keys = False) as m:
        m.kill_session(session_id =sid)


def demo(host, port, user, password):
    with manager.connect(host=host, port=port, username=user , hostkey_verify=False, password=password, timeout = 60, allow_agent = False , look_for_keys = False) as m:
        


        # Fetching all the users
        u_name = '''
        <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            <users xmlns="urn:o-ran:user-mgmt:1.0">	
            </users>
        </filter>'''


        get_u = m.get(u_name).data_xml
        dict_u = xmltodict.parse(str(get_u))
        try:
            users = dict_u['data']['users']['user']
            u = {}
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
        slot_names = m.get(sw_inv).data_xml
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

        interface_name = m.get_config('running', v_name1).data_xml
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


        
        host = host
        port = 22
        user1 = Config.details['SUPER_USER']
        pswrd = Config.details['SUPER_USER_PASS']

        command = "cd {}; rm -rf {};".format(Config.details['SYSLOG_PATH'],Config.details['syslog_name'])
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port, user1, pswrd)

        stdin, stdout, stderr = ssh.exec_command(command)
        return [u, s, ma, d]


def GET_SYSTEM_LOGS(host,user, pswrd,PDF):
    host = host
    port = 22
    username = user
    password = pswrd
    PDF.add_page()
    STORE_DATA('\t\t\t\t############ SYSTEM LOGS ##############',Format=True,PDF=PDF)
    command = "cd {}; cat {};".format(Config.details['SYSLOG_PATH'],Config.details['syslog_name'])
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, port, username, password)

    stdin, stdout, stderr = ssh.exec_command(command)
    lines = stdout.readlines()
    for i in lines:
        STORE_DATA("{}".format(i),Format=False,PDF=PDF)
    PDF.add_page()


def GET_LOGS_NAME(TC_Name):
    s = datetime.now()
    return f"{TC_Name}_{s.hour}_{s.minute}_{s.second}_{s.day}_{s.month}_{s.year}"

######################## Use This when more then 2 args in STORE_DATA functio,OUTPUT_LISTn
def STORE_DATA(*datas,Format,PDF):
    for data in datas:
    # OUTPUT_LIST.append(*data)
    # print(''.join([*data]))
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


def CREATE_LOGS(File_name,PDF):
    pdf = PDF_CAP()
    LOG_NAME = GET_LOGS_NAME(File_name)
    local_DIR = os.path.dirname(__file__)
    ABS_Path = os.path.join(local_DIR,'LOGS')
    file1 = f"{ABS_Path}/{LOG_NAME}.pdf"
    # STORE_DATA(OUTPUT_LIST,OUTPUT_LIST)
    PDF.output(file1)


def ADD_CONFIDENTIAL(TC,SW_R):

    CONF = '''    

     @ FILE NAME:    M_CTC_ID_0{0}_.txt \n                                                           
     @ TEST SCOPE:    M PLANE O-RAN CONFORMANCE \n
     @ Software Release for Garuda_RevD: \t v{1}                          
     '''.format(TC,SW_R,'*'*70)
    return CONF


def Test_desc(PDF,data):
     PDF.set_font("Times",style = 'B', size=13)
     PDF.set_text_color(17, 64, 37)
     PDF.multi_cell(w =180,h = 10,txt='{}'.format(data),border=1,align='L')
     PDF.set_font("Times",style = '',size = 9)
     PDF.set_text_color(0, 0, 0)
    #  PDF.ln(80)
     pass



def STATUS(host,user,session_id,port):
    STATUS = f'''> connect --ssh --host {host} --port 830 --login {user}
                        Interactive SSH Authentication
                        Type your password:
                        Password: 
                        > status
                        Current NETCONF session:
                        ID          : {session_id}
                        Host        : {host}
                        Port        : {port}
                        Transport   : SSH
                        Capabilities:
                        '''
    return STATUS



def PDF_CAP():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Times", size=9)
    y = int(pdf.epw)
    pdf.image(name='Front_Page.png', x = None, y = None, w = y, h = 0, type = '', link = '')
    pdf.ln(10)
    return pdf



def HEADING(PDF,data,*args):
    PDF.set_font("Times",style = 'B', size=11)
    PDF.write(5, '\n{}\n'.format('='*75))
    PDF.write(5,data)
    PDF.write(5, '\n{}\n'.format('='*75))
    PDF.set_font("Times",style = '',size = 9)



def XML_FORMAT(PDF,data):
    PDF.set_text_color(199, 48, 83)
    PDF.write(5,data)
    PDF.set_text_color(0, 0, 0)


def CONFDENTIAL(PDF,data):
     PDF.set_font("Times",style = 'B', size=15)
     PDF.set_text_color(10, 32, 71)
     PDF.multi_cell(w =180,txt=data,border=1,align='L')
     PDF.set_font("Times",style = '',size = 9)
     PDF.set_text_color(0, 0, 0)
     PDF.ln(30)
     pass

def Test_Step(PDF,data):
    PDF.set_font("Times",style = 'B', size=12)
    PDF.set_text_color(125, 93, 65)
    PDF.write(5, '\n{}\n'.format('='*75))
    PDF.write(5,txt=data)
    PDF.write(5, '\n{}\n'.format('='*75))
    PDF.set_font("Times",style = '',size = 9)
    PDF.set_text_color(0,0,0)


def DHCP_Status(PDF,data):
    print(data)
    abs_path = os.path.join('dejavu-fonts-ttf-2.37/ttf/','DejaVuSansCondensed.ttf')
    PDF.add_font('DejaVu', '', abs_path, uni=True)
    PDF.set_font("DejaVu",'', size=9)
    PDF.write(5,data)
    PDF.set_font("Times",style = '',size = 9)

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
