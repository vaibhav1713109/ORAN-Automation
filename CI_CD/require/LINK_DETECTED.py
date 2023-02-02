import subprocess, ifcfg, time
from scapy.all import *

class Link_Detect():
    def __init__(self) -> None:
        self.interfaces_name = ifcfg.interfaces()
        self.INTERFACE_NAME = ''
        self.hostname = ''
        self.du_hostname = ''
        pass




    ############################################ Return the interface which is detected ############################################
    def test_ethtool_linked(self,interface):
        cmd = "sudo ethtool " + interface
        Output = subprocess.getoutput(cmd).split('\n')
        for line in Output:
            # print(line)
            if "Speed" in line and ('10000' in line or '25000' in line):   
                # print(self.INTERFACE_NAME)
                return interface


    ############################################  Test whether link is detected. ############################################
    def test_linked_detected(self):
        Interfaces = list(self.interfaces_name.keys())
        # print(Interface)
        for i in Interfaces:
            # print(self.test_ethtool_linked(i))
            if '.' not in i:
                if self.test_ethtool_linked(i):
                    self.INTERFACE_NAME = self.test_ethtool_linked(i)
        return self.INTERFACE_NAME,self.interfaces_name

    def check_tcp_ip(self,pkt):
        summary = pkt.summary()
        try:
            if 'TCP' in summary:
                # pkt.show()
                interfaces = ifcfg.interfaces()
                mac_adrs = interfaces[self.INTERFACE_NAME]['ether']
                if pkt['TCP'].sport == 4334 or pkt['TCP'].sport == 830 or mac_adrs == pkt.src or pkt['TCP'].flags == 'RA':
                    print('Got ip to the Fronthaul Interface...')
                    print('Fronthaul Interface IP is : {}'.format(pkt['IP'].dst))
                    self.hostname = pkt['IP'].dst
                    self.du_hostname = pkt['IP'].src
                    # print(self.hostname)
                    time.sleep(5)
                    return True
                else:
                    print('Got ip to the Fronthaul Interface...')
                    print('Fronthaul Interface IP is : {}'.format(pkt['IP'].src))
                    self.hostname = pkt['IP'].src
                    self.du_hostname = pkt['IP'].dst
                    # print(self.hostname)
                    time.sleep(5)
                    return True
        except Exception as e:
            # print(e)
            return False
        pass

    ###############################################################################
    ## Check Ping and DHCP Status
    ###############################################################################
    def ping_status(self):
        sniff(iface = self.INTERFACE_NAME, stop_filter = self.check_tcp_ip, timeout = 100)
        self.dhcpp_st = subprocess.getoutput('sudo /etc/init.d/isc-dhcp-server status')
        ## Check3 : Ping of VLAN IP
        check3 = True
        response = os.system("ping -c 5 {}".format(self.hostname))
        self.ping = subprocess.getoutput('ping -c 5 {}'.format(self.hostname))
        if response == 0:
            print('{0}\nDHCP IP is Pinging...\n{0}'.format('='*100))
        else:
            print('{0}\nDHCP IP not Pinging...\n{0}'.format('='*100))
            check3 = False
        return check3

def test_call():
    obj = Link_Detect()
    t = time.time()+100
    while t > time.time():
        obj.test_linked_detected()
        if obj.INTERFACE_NAME:
            print('Link Detected!!', obj.INTERFACE_NAME)
            break
    obj.ping_status()

if __name__ == "__main__":
    # i = 0
    # while i<10:
    #     print(i)
    #     i+=1
        test_call()