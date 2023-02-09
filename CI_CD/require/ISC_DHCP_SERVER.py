import random, ifcfg, subprocess, os

class test_DHCP_CONF():
    def __init__(self) -> None:
        self.IPADDR = ''
        self.SUBNET_M = ''
        self.FLAG = False
        self.INTERFACE_NAME = ''
        self.interfaces_name = ''
        self.STATIC_IP = ''
        pass

    ############################################ Return the interface which is detected ############################################
    def test_ethtool_linked(self,interface):
        cmd = "sudo ethtool " + interface
        Output = subprocess.getoutput(cmd).split('\n')
        for line in Output:
            if "Speed" in line and '1000' in line:
                self.INTERFACE_NAME = interface
                return self.INTERFACE_NAME

    ############################################  Test whether link is detected. ############################################
    def test_linked_detected(self):
        self.interfaces_name = ifcfg.interfaces()
        Interface = list(self.interfaces_name.keys())
        # print(Interface)
        for i in Interface:
            if self.test_ethtool_linked(i):
                s = self.test_ethtool_linked(i)


    # Genrate random ip for vlan
    def test_random_ip_genrate(self):
        x = random.randint(1,255)
        y = random.randint(1,255)
        self.IPADDR = '192.168.{}.{}'.format(x,y)

    # Read dhcp configuration and add data in dhcp configurration file.
    def test_read(self,interface,v_id):
        directory_path = os.path.dirname(__file__)
        # print(directory_path)
        file = open(os.path.join(directory_path,'../DATA','ISC_DHCP_SERVER.txt'), 'r+')
        data = file.readlines()
        # Chnage ip address for vlan scanning
        for i in data:
            if 'INTERFACES' in i:
                s = i.rstrip()
                if v_id:
                    new_i = f'INTERFACES="{interface}.{v_id}"\n'
                else:
                    new_i = f'INTERFACES="{interface}"\n'
                index_of_i = data.index(i)
                data[index_of_i] = new_i
                    # print(i)
            
        # for i in data:
        #     print(i)
        file1 = open('/etc/default/isc-dhcp-server', 'w+')
        file1.writelines(data)
        file1.close()

if __name__ == "__main__":
    obj = test_DHCP_CONF()
    v_id = random.randint(10,30)
    obj.test_read('eth0',v_id)
    