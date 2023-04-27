###############################################################################
##@ FILE NAME:      M_CTC_ID_026
##@ TEST SCOPE:     M PLANE O-RAN CONFORMANCE
##@ Version:        V_1.0.0
##@ Support:        @Ramiyer, @VaibhavDhiman, @PriyaSharma
###############################################################################

###############################################################################
## Package Imports 
###############################################################################

import sys, os, time, xmltodict, xml.dom.minidom, re, ifcfg, subprocess
from lxml import etree
from warnings import warn
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
# print(parent)
root_dir = parent.rsplit('/',1)[0]
sys.path.append(parent)

########################################################################
## For reading data from .ini file
########################################################################
configur = ConfigParser()
configur.read('{}/inputs.ini'.format(dir_name))

###############################################################################
## Related Imports
###############################################################################
# from require.Notification import *
# from require.Configuration import *
# from require.Genrate_User_Pass import *



class M_CTC_ID_026():
    # init method or constructor 
    def __init__(self):
        self.hostname = configur.get('INFO','ru_ip')
        self.username = configur.get('INFO','ru_username')
        self.password = configur.get('INFO','ru_password')
        self.ru_mac = configur.get('INFO','ru_mac')
        self.du_mac = configur.get('INFO','du_mac')
        self.timeout = 60
        self.tx_arfcn = configur.get('INFO','tx_arfcn')
        self.rx_arfcn = configur.get('INFO','rx_arfcn')
        self.bandwidth = configur.get('INFO','bandwidth')
        self.tx_center_freq = configur.get('INFO','tx_center_frequency')
        self.rx_center_freq = configur.get('INFO','rx_center_frequency')
        self.duplex_scheme = configur.get('INFO','duplex_scheme')
        self.scs_val = configur.get('INFO','scs_value')
        self.element_name = configur.get('INFO','element_name')
        self.interface_ru = configur.get('INFO','fh_interface')
        print(self.interface_ru)
        self.uplane_filter = '''
                <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <user-plane-configuration xmlns="urn:o-ran:uplane-conf:1.0">
                </user-plane-configuration>
                </filter>
                '''

    def check_ping_status(self):
        response = subprocess.Popen(f"ping -c 5 {self.hostname}", shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = response.communicate()
        Response = stdout.decode()
        pattern = '[1-5] received'
        ans  = re.search(pattern,Response)
        if ans:
            return True
        else:
            return False

    def session_login(self):
        try:
            self.session = manager.call_home(host = '0.0.0.0', port=4334, hostkey_verify=False,username = self.username, password = self.password,timeout = self.timeout,allow_agent = False , look_for_keys = False)
            self.hostname, call_home_port = self.session._session._transport.sock.getpeername()   #['self.hostname', 'TCP_Port']
            self.login_info = f'''> listen --ssh --login {self.username}
                    Waiting 60s for an SSH Call Home connection on port 4334...
                    The authenticity of the host '::ffff:{self.hostname}' cannot be established.
                    Interactive SSH Authentication done.'''.strip()
            
        except Exception as e:
            print(f'session_login call_home Error : {e}')
            warn('Call Home is not initiated. Hence as an alternative "connect" initialisation will be performed.')
            self.session = manager.connect(host = self.hostname, port=830, hostkey_verify=False,username = self.username, password = self.password,timeout = self.timeout,allow_agent = False , look_for_keys = False)
            self.login_info = f'''> connect --ssh --host {self.hostname} --port 830 --login {self.username}
                    Interactive SSH Authentication done. 
                  '''
        return self.session, self.login_info


    ###############################################################################
    ## Login with sudo user for getting user details
    ###############################################################################
    def fetch_mac_of_ru(self):
        try:
            v_name1 = '''
                    <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                    <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
                    </interfaces>
                    </filter>
            '''
            interface_name = self.session.get(filter= v_name1).data_xml
            dict_interface = xmltodict.parse(str(interface_name))
            Interfaces = dict_interface['data']['interfaces']['interface']
            d = {}
            macs = {}
            for i in Interfaces:
                name = i['name']
                mac = i['mac-address']['#text']
                try:
                    IP_ADD = i['ipv4']['address']['ip']
                    if name:
                        d[name] = IP_ADD
                        macs[name] = mac
                except:
                    pass
            self.ru_mac = macs[self.interface_ru]
            print(self.ru_mac)
            return True
        except RPCError as e:
            return e
        
    def configure_interface(self):
        try:
            n = self.interface_ru[3]
            xml_data = open('{}/interface.xml'.format(dir_name)).read()
            xml_data = xml_data.format(interface_name= self.interface_ru,mac = self.ru_mac, number= n)
            interface_xml =f'''
                    <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                    {xml_data}
                    </config>'''
            print('{0}\n#{1}#\n{0}'.format('*'*100,'Interface_Yang'.center(98)))
            print(xml_data)
            print('-'*100)
            rpc_reply = self.session.edit_config(target="running", config=interface_xml,default_operation='merge')
            print(rpc_reply)
            if 'Ok' not in str(rpc_reply) or 'ok' not in str(rpc_reply):
                print("Merging interface xml || Successful")
                return True
            else:
                print("Merging interface xml || Fail")
                return rpc_reply
        except RPCError as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(f"Error occured in line number {exc_tb.tb_lineno}")
            rpc_error_element = etree.ElementTree(e.xml)
            rpc_error = etree.tostring(rpc_error_element).decode()
            rpc_error = xml.dom.minidom.parseString(rpc_error).toprettyxml()
            print(rpc_error)
            return rpc_error
        
        except Exception as e:
            print('{}'.format(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(f"Error occured in line number {exc_tb.tb_lineno}")
            return e

    def configure_processing(self):
        try:
            xml_data = open('{}/processing.xml'.format(dir_name)).read()
            xml_data = xml_data.format(int_name= self.interface_ru,ru_mac = self.ru_mac, du_mac = self.du_mac, element_name= self.element_name)
            processing_xml =f'''
                    <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                    {xml_data}
                    </config>'''
            print('{0}\n#{1}#\n{0}'.format('*'*100,'Processing_Yang'.center(98)))
            print(xml_data)
            print('-'*100)
            rpc_reply = self.session.edit_config(target="running", config=processing_xml,default_operation='merge')
            if 'Ok' not in str(rpc_reply) or 'ok' not in str(rpc_reply):
                print("Merging processing xml || Successful")
                return True
            else:
                print("Merging processing xml || Fail")
                print('-'*100)
                return rpc_reply
        except RPCError as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(f"Error occured in line number {exc_tb.tb_lineno}")
            rpc_error_element = etree.ElementTree(e.xml)
            rpc_error = etree.tostring(rpc_error_element).decode()
            rpc_error = xml.dom.minidom.parseString(rpc_error).toprettyxml()
            print(rpc_error)
            return rpc_error
        
        except Exception as e:
            print('{}'.format(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(f"Error occured in line number {exc_tb.tb_lineno}")
            return e

    def configure_uplane(self):
        try:
            n = self.interface_ru[3]
            xml_data = open('{}/uplane_xml.xml'.format(dir_name)).read()
            xml_data = xml_data.format(tx_arfcn = self.tx_arfcn, rx_arfcn = self.rx_arfcn, bandwidth = int(float(self.bandwidth)*(10**6)), tx_center_freq = int(float(self.tx_center_freq)*(10**9)), 
                        rx_center_freq = int(float(self.rx_center_freq)*(10**9)), duplex_scheme = self.duplex_scheme,element_name= self.element_name, scs_val = self.scs_val)
            user_plane_xml = f"""
                        <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                        {xml_data}
                        </config>"""
            print('{0}\n#{1}#\n{0}'.format('*'*100,'Uplane_Yang'.center(98)))
            print(xml_data)
            print('-'*100)
            rpc_reply = self.session.edit_config(target="running", config=user_plane_xml,default_operation='merge')
            if 'Ok' not in str(rpc_reply) or 'ok' not in str(rpc_reply):
                print("Merging uplane_xml xml || Successful")
            else:
                print("Merging uplane_xml xml || Fail")
                return rpc_reply
            print('-'*100)
            get_ouput = self.session.get(filter=self.uplane_filter).data_xml
            dict_data = xmltodict.parse(str(get_ouput))
            print(dict_data)
            ARFCN_RX1 = dict_data['data']['user-plane-configuration']['rx-array-carriers']['absolute-frequency-center']
            ARFCN_TX1 = dict_data['data']['user-plane-configuration']['tx-array-carriers']['absolute-frequency-center']

            ################# Check the ARFCN #################
            if (ARFCN_RX1 == self.rx_arfcn) and (ARFCN_TX1 == self.tx_arfcn):
                print(self,"o-ran-user-plane yang configured || Success")
                return True
            else:
                return "o-ran-uplane configuration didn't configure in O-RU"
        except RPCError as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(f"Error occured in line number {exc_tb.tb_lineno}")
            rpc_error_element = etree.ElementTree(e.xml)
            rpc_error = etree.tostring(rpc_error_element).decode()
            rpc_error = xml.dom.minidom.parseString(rpc_error).toprettyxml()
            print(rpc_error)
            return rpc_error
        
        except Exception as e:
            print('{}'.format(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(f"Error occured in line number {exc_tb.tb_lineno}")
            return e      

    ###############################################################################
    ## Main Function
    ###############################################################################
    def Main_Function(self):
        ping_status = self.check_ping_status()
        if ping_status:
            try:
                time.sleep(10)
                self.session, self.session_info = self.session_login()
                if self.session:
                    self.fetch_mac_of_ru()
                    interface_status = self.configure_interface()
                    if interface_status!=True:
                        return interface_status
                    processing_status = self.configure_processing()
                    if processing_status!=True:
                        return processing_status
                    uplane_status = self.configure_uplane()
                    if uplane_status!=True:
                        return uplane_status
                    return True
            ###############################################################################
            ## Exception
            ###############################################################################
            except Exception as e:
                print('{}'.format(e))
                exc_type, exc_obj, exc_tb = sys.exc_info()
                print(f"Error occured in line number {exc_tb.tb_lineno}", Format=False)
                return e
        else:
            print('RU is not pinging...')
        

if __name__ == "__main__":
    obj = M_CTC_ID_026()
    obj.Main_Function()

