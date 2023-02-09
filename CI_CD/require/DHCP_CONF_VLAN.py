import random, ifcfg, subprocess,os

class test_DHCP_CONF():
    def __init__(self) -> None:
        self.IPADDR = ''
        self.SUBNET_M = ''
        self.FLAG = False
        self.INTERFACE_NAME = ''
        self.interfaces_name = ''
        self.STATIC_IP = ''
        pass



    ############################################ Genrate random ip for vlan ############################################
    def test_random_ip_genrate(self):
        x = random.randint(1,255)
        y = random.randint(1,255)
        self.IPADDR = '192.168.{}.{}'.format(x,y)



    ############################################ Read dhcp configuration and add data in dhcp configurration file.   ############################################
    def test_read(self):
        self.test_random_ip_genrate()                                                       # Call the random function
        split_ip = self.IPADDR.split('.')                                                   # Store ip data in list (e.g. 192.168.3.20 >> ['192','168','3','20'])
        self.SUBNET_M = '{}.{}.{}.0'.format(split_ip[0],split_ip[1],split_ip[2])            # Make subnet of ip (e.g. 192.168.3.0)
        hex_ip = '{:02X}:{:02X}:{:02X}:{:02X}'.format(*map(int,split_ip))                   # Convert ip into hex (e.g. 192.168.3.20 >> C0:A8:03:10)
        print(hex_ip)
        directory_path = os.path.dirname(__file__)
        # print(directory_path)
        file = open(os.path.join(directory_path,'../DATA','DHCPD_CONF.txt'), 'r')
        data = file.readlines()


        ############################################ Chnage ip address for vlan scanning ############################################
        for i in data:
            if 'domain-name-servers' in i:
                index_of_domain = data.index(i)
                new_domain = 'option domain-name-servers {};\n'.format(self.IPADDR)
                data[index_of_domain] = new_domain
            if 'vendor-encapsulated-options 81:' in i:
                if self.IPADDR not in i:
                    s = i.rstrip()
                    new_i = f'\toption vendor-encapsulated-options 81:04:{hex_ip};\n'
                    index_of_i = data.index(i)
                    data[index_of_i] = new_i
                    # print(i)
            if 'subnet' in i:
                if self.SUBNET_M  in i:
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



        ############################################ Write Data in file ############################################
        # for i in data:
        #     print(i)
        file1 = open('/etc/dhcp/dhcpd.conf', 'w+')
        file1.writelines(data)
        file1.close()
        return self.IPADDR



############################################ Unit Test The function ############################################
def test_call():
    obj = test_DHCP_CONF()
    # print(obj.test_read())
    if obj.test_read():
        return True
    else:
        return False
if __name__ == "__main__":
    test_call()