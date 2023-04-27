import os, sys, xmltodict,ifcfg, subprocess, time,re,xml.dom.minidom
from ncclient import manager
from lxml import etree
from ncclient.operations.rpc import RPC, RPCError
from ncclient.xml_ import to_ele
import paramiko
from scapy.all import *
from datetime import datetime
from tabulate import tabulate
from fpdf import FPDF
from fpdf.enums import XPos, YPos
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
root_dir = parent.rsplit('/',1)[0]
# print(parent)
# print(dir_name)

########################################################################
## For reading data from .ini file
########################################################################
configur = ConfigParser()
configur.read('{}/require/inputs.ini'.format(parent))


class PowerCycleError(Exception):
    def __init__(self, message):
        super().__init__(message)
    # def __init__(self, message, error_code):
    #     super().__init__(message)
    #     self.error_code = error_code


class PDF(FPDF):
    

    def header(self):
        self.image('{}/require/vvdn_logo.png'.format(parent), 10, 8, 33)
        self.set_text_color(44, 112, 232)
        self.set_font('Times', 'B', 15)
        self.set_x(-45)
        self.set_font('Times', 'B', 12)
        self.cell(0,10,'M Plane Conformance', XPos.RIGHT, new_y= YPos.NEXT, align='R')
        self.set_text_color(0,0,0)
        self.ln(20)


    def footer(self):
        self.set_y(-15)
        self.set_font('Times', 'I', 8)
        self.set_text_color(0,0,0)
        self.cell(0, 10, 'Page %s' % self.page_no(), XPos.RIGHT, new_y= YPos.NEXT, align='C')
        self.set_text_color(44, 112, 232)
        self.set_font('Times', 'B', 8)
        self.cell(0, -10, 'Copyright (c) 2016 - 2022 VVDN Technologies Pvt Ltd', XPos.RIGHT, new_y= YPos.NEXT, align='R')
        self.cell(0,10)
        self.set_text_color(0,0,0)

    ###############################################################################
    ## for storing data into pdf as well as shown to the console
    ###############################################################################
    def STORE_DATA(self,*datas,Format):
        for data in datas:
            if Format == True:
                # print('='*100)
                # print(data)
                # print('='*100)
                self.HEADING(data)

            elif Format == 'XML':
                # print(data)
                self.XML_FORMAT(data)

            elif Format == 'CONF':
                # print('='*100)
                # print(data)
                # print('='*100)
                self.CONFDENTIAL(data)
            
            elif Format == 'DESC':
                # print('='*100)
                # print(data)
                # print('='*100)
                self.Test_desc(data)

            elif Format == 'TEST_STEP':
                # print('='*100)
                # print(data)
                # print('='*100)
                self.Test_Step(data)

            else:
                # print(data)
                self.write(h=5,txt=data)

    ###############################################################################
    ## Add Confidential for Radio Unit
    ###############################################################################
    def ADD_CONFIDENTIAL(self,TC,SW_R):

        CONF = '''    

        @ FILE NAME:    {0}.txt \n                                                           
        @ TEST SCOPE:    M PLANE O-RAN CONFORMANCE \n
        @ Software Release for {1}: \t v{2}                          
        '''.format(TC,configur.get('INFO','ru_name_rev'),SW_R,'*'*70)
        return CONF


    ###############################################################################
    ## Style sheet for test description
    ###############################################################################
    def Test_desc(self,data):
        self.set_font("Times",style = 'B', size=13)
        self.set_text_color(17, 64, 37)
        self.multi_cell(w =180,h = 10,txt='{}'.format(data),border=1,align='L')
        self.set_font("Times",style = '',size = 9)
        self.set_text_color(0, 0, 0)
        pass



    ###############################################################################
    ## Status of Netopeer-cli
    ###############################################################################
    def STATUS(self,host,session_id,port):
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
    def PDF_CAP(self):
        self.add_page()
        self.set_font("Times", size=9)
        y = int(self.epw)
        self.image(name='{}/require/Front_Page.png'.format(parent), x = None, y = None, w = y, h = 0, type = '', link = '')
        self.ln(10)


    ###############################################################################
    ## Stylesheet for heading
    ###############################################################################
    def HEADING(self,data,*args):
        self.set_font("Times",style = 'B', size=11)
        self.write(5, '\n{}\n'.format('='*75))
        self.write(5,data)
        self.write(5, '\n{}\n'.format('='*75))
        self.set_font("Times",style = '',size = 9)



    ###############################################################################
    ## Stylesheet for XML
    ###############################################################################
    def XML_FORMAT(self,data):
        self.set_text_color(199, 48, 83)
        self.write(5,data)
        self.set_text_color(0, 0, 0)


    ###############################################################################
    ## Stylesheet for Confidential
    ###############################################################################
    def CONFDENTIAL(self,data):
        self.set_font("Times",style = 'B', size=15)
        self.set_text_color(10, 32, 71)
        self.multi_cell(w =180,txt=data,border=1,align='L')
        self.set_font("Times",style = '',size = 9)
        self.set_text_color(0, 0, 0)
        self.ln(30)
        pass

    ###############################################################################
    ## Stylesheet for test setps
    ###############################################################################
    def Test_Step(self,data):
        self.set_font("Times",style = 'B', size=12)
        self.set_text_color(125, 93, 65)
        self.write(5, '\n{}\n'.format('='*75))
        self.write(5,txt=data)
        self.write(5, '\n{}\n'.format('='*75))
        self.set_font("Times",style = '',size = 9)
        self.set_text_color(0,0,0)


    ###############################################################################
    ## Stylesheet for dhcp server
    ###############################################################################
    def DHCP_Status(self,data):
        data = data.split('writable')
        #print(data)
        #abs_path = os.path.join('{}/dejavu-fonts-ttf-2.37/ttf/'.format(parent),'DejaVuSans.ttf')
        #self.add_font('DejaVu', '', abs_path, uni=True)
        #self.set_font("DejaVu",'', size=9)
        self.STORE_DATA("\t DHCP Status",Format=True)
        if len(data) == 2:
            datas = data[1][2:350]+data[1][362:]
        else:
            datas = data[0][2:350]+data[0][362:]
        print(datas)
        self.write(5,datas)
        self.set_font("Times",style = '',size = 9)

    ###############################################################################
    ## Stylesheet for actual result
    ###############################################################################
    def ACT_RES(self,data,COL):
        # print('='*100)
        # print(data)
        # print('='*100)
        self.set_font("Times",style = 'B', size=12)
        self.set_fill_color(COL[0],COL[1],COL[2])
        self.write(5, '\n{}\n'.format('='*75))
        self.multi_cell(w =self.epw,txt=data,border=1,align='L',fill=True)
        self.write(5, '\n{}\n'.format('='*75))
        self.set_font("Times",style = '',size = 9)
        self.set_fill_color(255,255,255)


    ###############################################################################
    ## Stylesheet for table
    ###############################################################################
    def TABLE(self,Header,Data,PDF):
        ACT_RES = tabulate(Data,Header,tablefmt='fancy_grid')
        print(ACT_RES)
        self.render_header(Header)
        self.render_table_data(Data)

    def render_header(self,TABLE_Header):
        line_height=10
        col_width=45
        self.set_font("Times",style="B")  # enabling bold text
        for col_name in TABLE_Header:
            self.cell(col_width, line_height, col_name, border=1,align='C')
        self.ln(line_height)
        self.set_font(style="")  # disabling bold text

    def render_table_data(self,TABLE_DATA):  # repeat data rows
        line_height=10
        col_width=self.epw/len(TABLE_DATA[0])
        for row in TABLE_DATA:
            for datum in row:
                self.multi_cell(col_width, line_height, datum, border=1,
                    new_x="RIGHT", new_y="TOP", max_line_height=self.font_size,align='L')
            self.ln(line_height)

    ###############################################################################
    ## Collecting the system logs
    ###############################################################################
    def GET_SYSTEM_LOGS(self,host,user, pswrd):
        for _ in range(5):
            try:
                host = host
                port = 22
                username = user
                password = pswrd
                self.add_page()
                self.STORE_DATA('\t\t\t\t############ SYSTEM LOGS ##############',Format=True)
                command = "cat {};".format(configur.get('INFO','syslog_path'))
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(host, port, username, password)

                stdin, stdout, stderr = ssh.exec_command(command)
                lines = stdout.readlines()
                for i in lines:
                    self.STORE_DATA("{}".format(i),Format=False)
                self.add_page()
                return True
            except Exception as e:
                PDF.STORE_DATA(self,f'GET_SYSTEM_LOGS Error : {e}',Format=True)
                pass
        else:
            Configuration.append_data_and_print(self,'Can\'t connect to the RU || Logs are not captured.')
            return False





class Configuration():
    def __init__(self) -> None:
        self.interfaces_name = list(ifcfg.interfaces().keys())
        self.INTERFACE_NAME = ''
        pass

    ###############################################################################
    ## Identify the 10/25G Interface
    ###############################################################################
    def identify_10G_interface(self):
        for interface in self.interfaces_name:
            if '.' not in interface:
                cmd = f"sudo ethtool {interface} | grep 'Speed:\|Link detected'"
                p = subprocess.Popen(cmd, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = p.communicate()
                if 'sudo: /etc/sudoers.d/README is world writable' not in stderr.decode() and stderr:
                    print(stderr)
                    return False
                else:
                    output = stdout.decode().split('\n')
                    if '10000' in  output[0] or '25000' in  output[0]:
                        return interface

    ###############################################################################
    ## Test whether link is detected.
    ###############################################################################
    def check_link_detection(self):
        wait_time = configur.getint('INFO','wait_time')
        timeout = time.time()+wait_time
        while timeout > time.time():
            self.INTERFACE_NAME = self.identify_10G_interface()
            if self.INTERFACE_NAME:
                print('SFP Link detected!!')
                return self.INTERFACE_NAME,self.interfaces_name
        else:
            print('\n ********** SFP is not Connected!!! ********** \n')
            self.INTERFACE_NAME = ''
            return False

    ###############################################################################
    ## Check wether dhcp is running
    ###############################################################################
    def is_DHCP_server_running(self):
        cmd = "sudo systemctl status isc-dhcp-server.service"
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if "Active: active (running)" in out.decode():
            # logging.info("DHCP server is running.")
            return True
        else:
            # logging.warning("DHCP server is not running. Restarting...")
            self.restart_dhcp_server()
            return self.is_DHCP_server_running()
    
    ###############################################################################
    ## Restart DHCP Server
    ###############################################################################
    def restart_dhcp_server(self):
        cmd = "sudo systemctl restart isc-dhcp-server.service"
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        if stderr:
            raise PowerCycleError(f"Failed to restart DHCP server: {stderr.decode()}")
        time.sleep(1)
        if not self.is_DHCP_server_running():
            raise PowerCycleError("Failed to start DHCP server.")
        pass

    ###############################################################################
    ## Check Ping
    ###############################################################################
    def check_ping_status(self, ip_address):
        response = subprocess.Popen(f"ping -c 5 {ip_address}", shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = response.communicate()
        Response = stdout.decode()
        pattern = '[1-5] received'
        ans  = re.search(pattern,Response)
        if ans:
            return True
        else:
            return False
    ############################################ Genrate random ip for vlan ############################################
    def test_random_ip_genrate(self):
        x = random.randint(1,255)
        y = random.randint(1,255)
        self.IPADDR = '192.168.{}.{}'.format(x,y)

    ############################################ Read dhcp configuration and add data in dhcp configurration file.   ############################################
    def test_configure_dhcpd_conf(self):
        # Call the random ip genrator function
        self.test_random_ip_genrate()
        # Store ip data in list (e.g. 192.168.3.20 >> ['192','168','3','20'])
        split_ip = self.IPADDR.split('.')
        # Make subnet of ip (e.g. 192.168.3.0)
        self.SUBNET_M = '{}.{}.{}.0'.format(split_ip[0],split_ip[1],split_ip[2])
        # Convert ip into hex (e.g. 192.168.3.20 >> C0:A8:03:10)
        hex_ip = '{:02X}:{:02X}:{:02X}:{:02X}'.format(*map(int,split_ip))                   
        # print(hex_ip)
        directory_path = os.path.dirname(os.path.dirname(__file__))
        dhcp_conf_file_path = f'{directory_path}/DATA/DHCPD_CONF.txt'
        # print(directory_path)
        file = open(dhcp_conf_file_path, 'r')
        data = file.readlines()


        ############################################ Chnage ip address for vlan scanning ############################################
        for line in data:
            if 'domain-name-servers' in line:
                index_of_domain = data.index(line)
                new_domain = 'option domain-name-servers {};\n'.format(self.IPADDR)
                data[index_of_domain] = new_domain
            elif 'vendor-encapsulated-options 81:' in line:
                if self.IPADDR not in line:
                    s = line.rstrip()
                    new_i = f'\toption vendor-encapsulated-options 81:04:{hex_ip};\n'
                    index_of_i = data.index(line)
                    data[index_of_i] = new_i
            elif 'subnet' in line:
                if self.SUBNET_M  in line:
                    self.FLAG = True
                    break
                else: 
                    self.FLAG = False



        ############################################ ADD Subnet for reterive ip details ############################################
        if self.FLAG == False:
            new_subnet = '''subnet {0}.0 netmask 255.255.255.0 {{
            pool {{
                    allow members of "o-ran-ru";
                    allow members of "o-ran-ru2";
                    range {0}.37 {0}.200 ;

            }}
            pool {{
                    deny members of "o-ran-ru";
                    deny members of "o-ran-ru2";
                    range {0}.6 {0}.36 ;
            }}
            option routers {1};
            option broadcast-address {0}.255;
            option subnet-mask 255.255.255.0;
            option interface-mtu 1500;
            }}\n'''

            new_sub = new_subnet.format(self.SUBNET_M[:len(self.SUBNET_M)-2],self.IPADDR)
            # new_s = new_sub[1:len(new_sub)-1]
            data.append(new_sub)    
        file.close()

        file1 = open('/etc/dhcp/dhcpd.conf', 'w+')
        file1.writelines(data)
        file1.close()
        return self.IPADDR

    def test_configure_isc_dhcp_server(self,interface,v_id):
        directory_path = os.path.dirname(os.path.dirname(__file__))
        dhcp_conf_file_path = f'{directory_path}/DATA/ISC_DHCP_SERVER.txt'
        # print(directory_path)
        file = open(dhcp_conf_file_path, 'r+')
        data = file.readlines()
        # Chnage ip address for vlan scanning
        for line in data:
            if 'INTERFACES' in line:
                s = line.rstrip()
                if v_id:
                    new_i = f'INTERFACES="{interface}.{v_id}"\n'
                else:
                    new_i = f'INTERFACES="{interface}"\n'
                index_of_i = data.index(line)
                data[index_of_i] = new_i
                    # print(i)
        file.close()
        # for i in data:
        #     print(i)
        file1 = open('/etc/default/isc-dhcp-server', 'w+')
        file1.writelines(data)
        file1.close()
    def reboot_RU(self,hostname):
        for _ in range(5):
            try:
                host = hostname
                port = 22
                username = configur.get('INFO','super_user')
                password = configur.get('INFO','super_pass')
                command = "reboot"
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(host, port, username, password)

                stdin, stdout, stderr = ssh.exec_command(command)
                lines = stdout.readlines()
                print(lines)
                return True
            except Exception as e:
                print(f'Reboot_RU Error : {e}')
                time.sleep(2)
                pass
        else:
            return 'Can\'t connect to the RU.., Reboot not happened.'

    def basic_check_for_vlan_scan(self):
        '''Description:  Check the link detection and the ping of dhcp ip if dhcp ip not ping return False with error string.
                        else it will reboot the RU so that vlan scan should start.'''
        Output = self.Link_detction_and_check_ping()
        if Output[-1]!=True:
            return Output[0]
        hostname = Output[-2]
        Res = self.reboot_RU(hostname)
        interfaces = ifcfg.interfaces().keys()
        for inter in interfaces:
            if f'{self.INTERFACE_NAME}.' in inter:
                os.system(f'sudo ifconfig {inter} down')
        return Res
    
    ###############################################################################
    ## Get IP its return either DHCP or Static
    ###############################################################################
    def get_ip_address(self):
        wait_time = configur.getint('INFO','wait_time')
        timeout = time.time()+wait_time
        static_ip = configur.get('INFO','static_ip')
        Result = subprocess.getoutput('sudo /etc/init.d/isc-dhcp-server status')
        Result = Result.split('\n')
        dhcp_ip = ''
        for line in Result:
            if "DHCPACK on" in line and f"via {self.INTERFACE_NAME}" in line: 
                pattern = '(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
                ans = re.findall(pattern,line)
                dhcp_ip = ans[0]
        print(f"DHCP IP: {dhcp_ip}")
        print(f'{"-"*100}\nCheck the status of DHCP ip {dhcp_ip} ping\n{"-"*100}')
        while time.time()<timeout:
            if self.check_ping_status(dhcp_ip):
                self.append_data_and_print(f"DHCP IP {dhcp_ip} || successful.")
                ping_out = subprocess.getoutput("ping -c 5 {}".format(dhcp_ip))
                # print(ping_out)
                return dhcp_ip, ping_out,True
            time.sleep(5)
        else:
            self.append_data_and_print(f"DHCP IP {dhcp_ip} || fail.")
            ping_out = subprocess.getoutput("ping -c 5 {}".format(dhcp_ip))
            print(ping_out)
            print(f'{"-"*100}\nCheck the status of Static ip {static_ip} ping\n{"-"*100}')
            for _ in range(5):
                if self.check_ping_status(static_ip):
                    self.append_data_and_print(f'Static IP {static_ip} Ping || Successful')
                    ping_out = subprocess.getoutput("ping -c 5 {}".format(static_ip))
                    # print(ping_out)
                    return static_ip, ping_out,True
                time.sleep(5)
            else:
                self.append_data_and_print(f'Static IP {static_ip} Ping || Successful')
                PDF.STORE_DATA(self,'{}'.format("ping -c 5 {}".format(self.hostname)).center(100),Format=True,)
                ping_out = subprocess.getoutput("ping -c 5 {}".format(static_ip))
                PDF.STORE_DATA(self,ping_out,Format=False)
                return f'Static IP {static_ip} Ping || Fail'


    ###############################################################################
    ## Main function of configuration class
    ###############################################################################
    def Link_detction_and_check_ping(self):
        '''
            Description : It will check the link detecion first then get the ip which is pingable either DHCP or Static.
        '''
        print(f'{"-"*100}\nCheck the Link Detection')
        check_link = self.check_link_detection()

        cmd = "ethtool " + self.INTERFACE_NAME
        ethtool_out = subprocess.getoutput(cmd)
        if check_link:
            Result = self.get_ip_address()
            if Result[-1]==True:
                return ethtool_out, Result[1], cmd, Result[0],True
            else:
                PDF.STORE_DATA(self,'{}'.format(cmd).center(100),Format=True)
                PDF.STORE_DATA(self,ethtool_out,Format=False)
                return Result[0],False
        else:
            self.append_data_and_print(f'SFP Link Detection || Fail')
            PDF.STORE_DATA(self,'{}'.format(cmd).center(100),Format=True)
            PDF.STORE_DATA(self,ethtool_out,Format=False)
            return 'SFP Link Detection || Fail', False


    def check_ip_ping(self,ip_address):
        wait_time = configur.getint('INFO','wait_time')
        timeout = time.time()+wait_time
        for _ in range(10):
            dhcp_ip_address = self.check_dhcp_status()
            if self.check_ping_status(dhcp_ip_address):
                return dhcp_ip_address
            time.sleep(2)
        else:
            print(f'DHCP IP {dhcp_ip_address} Pinging Fail')
            timeout = time.time()+wait_time
            while timeout > time.time():
                if self.check_ping_status(ip_address):
                    return ip_address
            else:
                return False

    ###############################################################################
    ## It will append the data and print last appended data
    ###############################################################################
    def append_data_and_print(self,data):
        self.summary.append(data)
        print('-'*100)
        print(data)
        pass
    
    ###############################################################################
    ## Make nested list for storing summary
    ###############################################################################
    def nested_summary_list(self,summary):
        '''summary  =  [test_step3 || status, test_step3 || status, test_step3 || status, ...]
            it will split all test step with "||" and store [test_step and status] in table_data list'''
        table_data = []
        for data in summary:
            d = data.split('||')
            table_data.append([d[0],d[1]])
        return table_data
        pass        
    
    ###############################################################################
    ## Result Declaration for Test Script
    ###############################################################################
    def Result_Declartion(self,Test_case_name,Result,Log_Name):
        Check = Result
        # if Check[-1] == False:
        #     PDF.STORE_DATA(self,'{0} FAIL_REASON {0}'.format('*'*20),Format=True)
        #     PDF.STORE_DATA(self,f'{Check[0]}',Format=False)
        #     PDF.ACT_RES(self,f"{Test_case_name : <50}{'||' : ^20}{'FAIL' : ^20}",COL=(235, 52, 52))
        #     Configuration.append_data_and_print(self,f'FAIL_REASON || {Check[0]}')
        #     Configuration.append_data_and_print(self,f"{Test_case_name : <50}{'||' : ^20}{'FAIL' : ^20}")
        #     return False
        ###############################################################################
        ## Expected/Actual Result
        ###############################################################################
        PDF.GET_SYSTEM_LOGS(self,self.hostname,self.username,self.password)
        Exp_Result = 'Expected Result : The O-RU NETCONF Server responds with <rpc-reply><ok/></rpc-reply> to the TER NETCONF Client.'
        PDF.STORE_DATA(self,Exp_Result,Format='DESC')

        PDF.STORE_DATA(self,'\t\t{}'.format('****************** Actual Result ******************'),Format=True)

        try:
            if Check == True:
                PDF.ACT_RES(self,f"{Test_case_name : <50}{'||' : ^20}{'SUCCESS' : ^20}",COL=(105, 224, 113))
                Configuration.append_data_and_print(self,f"{Test_case_name : <50}{'||' : ^20}{'PASS' : ^20}")
                return True

            elif type(Check) == list:
                PDF.STORE_DATA(self,'{0} FAIL_REASON {0}'.format('*'*20),Format=True)
                Error_Info = '''\terror-tag \t: \t{}\n\terror-type \t: \t{}\n\terror-severity \t: \t{}\n\tDescription' \t: \t{}'''.format(*map(str,Check))
                PDF.STORE_DATA(self,Error_Info,Format=False)
                PDF.ACT_RES(self,f"{Test_case_name : <50}{'||' : ^20}{'FAIL' : ^20}",COL=(235, 52, 52))
                Configuration.append_data_and_print(self,"FAIL_REASON || {}".format(Error_Info))
                Configuration.append_data_and_print(self,f"{Test_case_name : <50}{'||' : ^20}{'FAIL' : ^20}")
                return False
            else:
                PDF.STORE_DATA(self,'{0} FAIL_REASON {0}'.format('*'*20),Format=True)
                PDF.STORE_DATA(self,'{}'.format(Check),Format=False)
                PDF.ACT_RES(self,f"{Test_case_name : <50}{'||' : ^20}{'FAIL' : ^20}",COL=(235, 52, 52))
                Configuration.append_data_and_print(self,'FAIL_REASON || {}'.format(Check))
                Configuration.append_data_and_print(self,f"{Test_case_name : <50}{'||' : ^20}{'FAIL' : ^20}")
                return False

                
        except Exception as e:
                PDF.STORE_DATA(self,'Result_Declartion Error : {}'.format(e), Format=True)
                exc_type, exc_obj, exc_tb = sys.exc_info()
                PDF.STORE_DATA(self,f"Error occured in line number {exc_tb.tb_lineno}", Format=False)
                Configuration.append_data_and_print(self,'FAIL_REASON || {}'.format(e))
                Configuration.append_data_and_print(self,f"{Test_case_name : <50}{'||' : ^20}{'FAIL' : ^20}")
                return False

        ###############################################################################
        ## For Capturing the logs
        ###############################################################################
        finally:
            PDF.HEADING(self,data='{0} Summary {0}'.format('*'*30))
            PDF.render_table_data(self,Configuration.nested_summary_list(self,self.summary))
            genrate_pdf_report.CREATE_LOGS(self,Log_Name)
    
    def test_server_10_interface_ip(self,ip_format):
        interfaces = ifcfg.interfaces()
        for key, val in interfaces.items():
            if val.get('inet') and ip_format in val['inet']:
                return val['inet']

class netopeer_connection():
    def __init__(self) -> None:
        self.username = configur.get('INFO','sudo_user')
        self.password = configur.get('INFO','sudo_pass')
        self.hostname = configur.get('INFO','static_ip')
        self.session = ''
        self.login_info = ''
        print(f'Sudo Credential : {self.username} {self.password}')


    ###############################################################################
    ## Deleting the system log 
    ###############################################################################
    def delete_system_log(self,host):
        timeout = time.time() + 30
        while time.time() < timeout:
        # for _ in range(5):
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
                PDF.STORE_DATA(self,f'Delete_system_log Error : {e}',Format=True)
                time.sleep(5)
                pass
        else:
            print('Can\'t connect to the RU.., old logs are not deleted.')
            return False
    

    ###############################################################################
    ## Call Home
    ###############################################################################
    def call_home(self,*args, **kwds):
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
    ## Decoding fingerprint
    ###############################################################################
    def colonify(self,fp):
        fp = fp.decode('UTF-8')
        finga = fp[:2]
        for idx in range(2, len(fp), 2):
            finga += ":" + fp[idx:idx+2]
        return finga

    ###############################################################################
    ## Establishing netopeer connection  
    ###############################################################################
    def session_login(self,timeout=20,username='',password=''):
        print(f'{"-"*100}\nEstablishing Netopeer Connection')
        try:
            self.session = self.call_home(host = '0.0.0.0', port=4334, hostkey_verify=False,username = username, password = password,timeout = timeout,allow_agent = False , look_for_keys = False)
            self.hostname, call_home_port = self.session._session._transport.sock.getpeername()   #['ip_address', 'TCP_Port']
            server_key_obj = self.session._session._transport.get_remote_server_key()
            fingerprint = self.colonify(hexlify(server_key_obj.get_fingerprint()))
            self.login_info = f'''> listen --ssh --login {username}
                    Waiting 60s for an SSH Call Home connection on port 4334...
                    The authenticity of the host '::ffff:{self.hostname}' cannot be established.
                    ssh-rsa key fingerprint is {fingerprint}
                    Interactive SSH Authentication done.'''.strip()
            
        except Exception as e:
            PDF.STORE_DATA(self,f'session_login call_home Error : {e}',Format=True)
            warn('Call Home is not initiated. Hence as an alternative "connect" initialisation will be performed.')
            # notification('Call Home is not initiated. Hence as an alternative "connect" initialisation will be performed.')
            self.session = manager.connect(host = self.hostname, port=830, hostkey_verify=False,username = username, password = password,timeout = timeout,allow_agent = False , look_for_keys = False)
            server_key_obj = self.session._session._transport.get_remote_server_key()
            fingerprint = self.colonify(hexlify(server_key_obj.get_fingerprint()))
            self.login_info = f'''> connect --ssh --host {self.hostname} --port 830 --login {username}
                    ssh-rsa key fingerprint is {fingerprint}
                    Interactive SSH Authentication done. 
                  '''
        return self.session, self.login_info

    ###############################################################################
    ## add_netopeer_connection_details to PDF
    ###############################################################################
    def add_netopeer_connection_details(self):
        PDF.STORE_DATA(self,'\n\n\t\t********** Connect to the NETCONF Server ***********\n\n',Format='TEST_STEP')
        PDF.STORE_DATA(self,self.login_info,Format=False)
        STATUS = PDF.STATUS(self,self.hostname,self.session.session_id,830)
        PDF.STORE_DATA(self,STATUS,Format=False)
    
    ###############################################################################
    ## Collect Active Software Detail
    ###############################################################################
    def Software_detail(self):
        sw_inv = '''<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            <software-inventory xmlns="urn:o-ran:software-management:1.0">
            </software-inventory>
            </filter>'''
        sw_detail = {}
        slot_names = self.session.get(sw_inv).data_xml
        dict_slot = xmltodict.parse(str(slot_names))
        try:
            slots = dict_slot['data']['software-inventory']['software-slot']
            for k in slots:
                active_s = k['active']
                running_s = k['running']
                slot_name = k['name']
                sw_build = k['build-version']
                slot_status = k['status']
                sw_detail[slot_name] = [active_s,running_s,sw_build,slot_status]

        except:
            print("User doesn't have SUDO permission")
        return sw_detail
    
    ###############################################################################
    ## ADD Test Description
    ###############################################################################
    def add_test_description(self,Test_Description,Test_Case_name):
        try:
            sw_detail = self.Software_detail()
            del sw_detail['swRecoverySlot']
            for key, val in sw_detail.items():
                #print(key,val)
                if (val[0] == 'true' and val[1] == 'true') or (val[0] == 'false' and val[1] == 'true'):
                    Test_Desc = f'Test Description :  {Test_Description}'
                    CONFIDENTIAL = PDF.ADD_CONFIDENTIAL(self,Test_Case_name,SW_R = val[2]) 
                    PDF.STORE_DATA(self,CONFIDENTIAL,Format='CONF')
                    PDF.STORE_DATA(self,Test_Desc,Format='DESC')
                    PDF.add_page(self)
                    self.running_sw = val[2]
                elif (val[0] == 'true' and val[1] == 'false'):
                    Test_Desc = f'Test Description :  {Test_Description}'
                    CONFIDENTIAL = PDF.ADD_CONFIDENTIAL(self,Test_Case_name,SW_R = val[2]) 
                    PDF.STORE_DATA(self,CONFIDENTIAL,Format='CONF')
                    PDF.STORE_DATA(self,Test_Desc,Format='DESC')
                    PDF.add_page(self)
                    self.running_false_sw = val[2]
                    self.inactive_slot = key
                else:
                    self.running_false_sw = val[2]
                    self.inactive_slot = key
            # print(self.running_sw, self.ruinning_false_sw, self.inactive_slot)
            return self.running_sw, self.running_false_sw, self.inactive_slot
        except Exception as e:
            PDF.STORE_DATA(self,f'Add_test_description Error : {e}',Format=True)
            return e
    
    def hello_capability(self):
        for cap in self.session.server_capabilities:
            PDF.STORE_DATA(self,"\t{}".format(cap),Format=False)
        self.summary.append('Capability exchange || Successful')
        print('-'*100)
        print(self.summary[-1])
        return True

    def create_subscription(self,filter=None, cmd = ''):
        PDF.STORE_DATA(self,cmd, Format=True)
        cap = self.session.create_subscription(filter=filter)
        dict_data = xmltodict.parse(str(cap))
        if 'ok' in str(cap) or 'Ok' in str(cap) or 'OK' in str(cap):
            PDF.STORE_DATA(self,'\nOk\n', Format=False)
        Configuration.append_data_and_print(self,'Create-subscription || Successful')
        pass

    def captured_notifications(self,filter):
        timeout= time.time()+60
        while timeout>time.time():
            n = self.session.take_notification(timeout=60)
            if n == None:
                break
            notify = n.notification_xml
            dict_n = xmltodict.parse(str(notify))
            try:
                dict_notfication = dict_n['notification'][filter]
                if dict_notfication:
                    x = xml.dom.minidom.parseString(notify)
                    xml_pretty_str = x.toprettyxml()
                    PDF.STORE_DATA(self,xml_pretty_str, Format='XML')
                    return dict_notfication
            except:
                pass
        else:
            print('No Notification captured..')
            return 'No Notification captured..'

    def get(self,filter=None,cmd = ''):
        if cmd:
            PDF.STORE_DATA(self,cmd, Format=True)
        get_ouput = self.session.get(filter).data_xml
        parsed_data = xml.dom.minidom.parseString(get_ouput)
        xml_pretty_str = parsed_data.toprettyxml()
        dict_data = xmltodict.parse(str(get_ouput))
        return xml_pretty_str,dict_data

    def reboot_RU(self,hostname):
        for _ in range(5):
            try:
                host = host
                port = 22
                username = configur.get('INFO','super_user')
                password = configur.get('INFO','super_pass')
                command = "reboot"
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(host, port, username, password)

                stdin, stdout, stderr = ssh.exec_command(command)
                lines = stdout.readlines()
                return True
            except Exception as e:
                time.sleep(5)
                PDF.STORE_DATA(self,f'Reboot_ru Error : {e}',Format=True)
                pass
        else:
            print('Can\'t connect to the RU.., Not able to reboot RU.')
            return False

    def edit_config(self,xml_data,operation='merge'):
        try:
            PDF.STORE_DATA(self,f'> edit-config  --target running --config --defop {operation}', Format=True)
            PDF.STORE_DATA(self,'******* Replace with below xml ********', Format=True)
            PDF.STORE_DATA(self,xml_data, Format='XML')
            self.session._Manager__set_timeout(80)
            rpc_reply = self.session.edit_config(target="running", config=xml_data,default_operation=operation)
            PDF.STORE_DATA(self,'''######### RPC Reply #########''', Format=True)
            if 'ok' in str(rpc_reply) or 'OK' in str(rpc_reply)  or 'Ok' in str(rpc_reply):
                PDF.STORE_DATA(self,f'\n{str(rpc_reply)}\n', Format=False)
                return True
            else:
                return rpc_reply
        except RPCError as e:
            rpc_error_element = etree.ElementTree(e.xml)
            rpc_error = etree.tostring(rpc_error_element).decode()
            rpc_error = xml.dom.minidom.parseString(rpc_error).toprettyxml()
            print('rpc_error occured edit_config')
            return rpc_error
        except Exception as e:
            PDF.STORE_DATA(self,f'Edit_config Error : {e}',Format=True)
            return e
        pass

    def send_rpc(self,rpc_data):
        try:
            PDF.STORE_DATA(self,'\n> user-rpc\n', Format=True)
            PDF.STORE_DATA(self,'******* Replace with below xml ********', Format=True)
            PDF.STORE_DATA(self,rpc_data, Format='XML')
            PDF.STORE_DATA(self,'******* RPC Reply ********', Format=True)
            rpc_reply = str(self.session.dispatch(to_ele(rpc_data)))
            PDF.STORE_DATA(self,'{}'.format(rpc_reply), Format='XML')
            if 'FAILED' in rpc_reply:
                return rpc_reply
            else:
                return True
        except Exception as e:
            PDF.STORE_DATA(self,f'Send_rpc Error : {e}',Format=True)
            return e

class genrate_pdf_report():
    def __init__(self) -> None:
        pass

    ###############################################################################
    ## Filename genration
    ###############################################################################
    def GET_LOGS_NAME(self,TC_Name):
        s = datetime.now()
        return f"{TC_Name}_{s.hour}_{s.minute}_{s.second}_{s.day}_{s.month}_{s.year}"

    ###############################################################################
    ## Creating pdf into 'LOGS' directory
    ###############################################################################
    def CREATE_LOGS(self,File_name):
        log_NAME = self.GET_LOGS_NAME(File_name)
        # print(f"{root_dir}/{configur.get('INFO','ru_name_rev')}/LOGS/MPLANE/{log_NAME}.pdf")
        file1 = f"{root_dir}/{configur.get('INFO','ru_name_rev')}/LOGS/MPLANE/{log_NAME}.pdf"
        ## Save the pdf file
        PDF.output(self,file1)




if __name__ == "__main__":
    # obj = Configuration()
    # obj.check_link_detection()
    sw_inv = '''<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            <software-inventory xmlns="urn:o-ran:software-management:1.0">
            </software-inventory>
            </filter>'''
    obj2 = genrate_pdf_report()
    filename = obj2.CREATE_LOGS('M_ctc_id_14')
