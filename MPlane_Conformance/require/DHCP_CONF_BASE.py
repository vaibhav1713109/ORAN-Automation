from pytest import ExitCode
import subprocess
import random, ifcfg, os, time
import ISC_DHCP_SERVER as ISC_DHCP_SERVER
import LINK_DETECTED as LINK_DETECTED

class test_DHCP_CONF():
    def __init__(self) -> None:
        self.IPADDR = ''
        self.SUBNET_M = ''
        self.FLAG = False
        self.INTERFACE_NAME = ''
        self.interfaces_name = ''
        self.STATIC_IP = ''
        pass

    

    ############################################ Read dhcp configuration and add data in dhcp configurration file. ############################################
    def test_read(self): 
        while True:   
            self.INTERFACE_NAME, self.interfaces_name= LINK_DETECTED.Link_Detect().test_linked_detected()
            if self.INTERFACE_NAME:                                  # Call the linkdetected func
                print('Link Detected')
                break
        # print(self.interfaces_name)
        self.STATIC_IP = self.interfaces_name[self.INTERFACE_NAME]['inet'].split('.')            # Store ip data in list (e.g. 192.168.4.25 >> ['192','168','4','20'])
        # print(self.STATIC_IP)
        self.SUBNET_M = '{}.{}.{}.0'.format(self.STATIC_IP[0],self.STATIC_IP[1],self.STATIC_IP[2])         # Make subnet of ip (e.g. 192.168.3.0)
        hex_ip = '{:02X}:{:02X}:{:02X}:{:02X}'.format(*map(int,self.STATIC_IP))                  # Convert ip into hex (e.g. 192.168.3.20 >> C0:A8:03:10)
        # print(hex_ip)
        directory_path = os.path.dirname(__file__)
        # print(directory_path)
        file = open(os.path.join(directory_path,'../DATA','DHCPD_CONF.txt'), 'r')
        data = file.readlines()
        self.IPADDR = '{}.{}.{}.{}'.format(*map(int,self.STATIC_IP)) 
        ############################################ Chnage ip address for vlan scanning ############################################
        for i in data:
            print(i)
            if 'domain-name-servers' in i:
                index_of_domain = data.index(i)
                new_domain = 'option domain-name-servers {}.{}.{}.{};\n'.format(*map(str,self.STATIC_IP))
                data[index_of_domain] = new_domain

            if 'vendor-encapsulated-options 81:' in i:
                index_of_81 = i.index('81')
                # print(index_of_81)
                if self.IPADDR not in i:
                    s = i.rstrip()
                    new_i = f'\toption vendor-encapsulated-options 81:04:{hex_ip};\n'
                    index_of_i = data.index(i)
                    data[index_of_i] = new_i
                    # print(i)
            if 'subnet' in i:
                if self.SUBNET_M  in i:
                    flag = True
                    break
                else: 
                    flag = False
            

        ############################################ ADD Subnet for reterive ip details ############################################
        if flag == False:
            new_subnet = '''[subnet {0}.0 netmask 255.255.255.0 {{
            pool {{
                    allow members of "o-ran-ru";
                    allow members of "o-ran-ru2";
                    range {0}.37 {0}.67 ;

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
    }}]'''

            new_sub = new_subnet.format(self.SUBNET_M[:len(self.SUBNET_M)-2],self.IPADDR)
            new_s = new_sub[1:len(new_sub)-1]
            data.append(new_s)
        file.close()
        # for i in data:
        #     print(i)
        file1 = open('/etc/dhcp/dhcpd.conf', 'w+')
        file1.writelines(data)
        file1.close()
        ISC_DHCP_SERVER.test_DHCP_CONF().test_read(self.INTERFACE_NAME,0)
        d = os.system('sudo /etc/init.d/isc-dhcp-server restart')
        st = subprocess.getoutput('sudo /etc/init.d/isc-dhcp-server status')
    

def test_call():
    obj = test_DHCP_CONF()

    obj.test_read()


if __name__ == "__main__":
    test_call()
