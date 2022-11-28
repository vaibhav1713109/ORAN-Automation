#######################################################################
## Useful Information for sniffing(capturing packets)
#######################################################################
'''Sniff packets
sniff([count=0,] [prn=None,] [store=1,] [offline=None,] [lfilter=None,] + L2ListenSocket args) -> list of packets

  count: number of packets to capture. 0 means infinity
  store: wether to store sniffed packets or discard them
    prn: function to apply to each packet. If something is returned,
         it is displayed. Ex:
         ex: prn = lambda x: x.summary()
lfilter: python function applied to each packet to determine
         if further action may be done
         ex: lfilter = lambda x: x.haslayer(Padding)
offline: pcap file to read packets from, instead of sniffing them
timeout: stop sniffing after a given time (default: None)
L2socket: use the provided L2socket
opened_socket: provide an object ready to use .recv() on
stop_filter: python function applied to each packet to determine
             if we have to stop the capture after this packet
             ex: stop_filter = lambda x: x.haslayer(TCP)'''

#######################################################################
## Imports
#######################################################################
import os, ifcfg, time, subprocess, sys
from scapy.all import *
   
###############################################################################
## Directory Path
###############################################################################
dir_name = os.path.dirname(os.path.abspath(__file__))
parent = os.path.dirname(dir_name)
# print(parent)
sys.path.append(parent)

###############################################################################
## Related Imports
###############################################################################
from require import ISC_DHCP_SERVER, DHCP_CONF_VLAN


#######################################################################
## Create Vlan
#######################################################################
class vlan_Creation():
    def __init__(self):
        self.interface = ''
        self.du_vlan = ''
        pass
    
    def create_vlan(self):
            time.sleep(5)
            obj = ISC_DHCP_SERVER.test_DHCP_CONF()
            obj.test_read(self.interface,self.du_vlan)
            obj1 = DHCP_CONF_VLAN.test_DHCP_CONF()
            IPADDR = obj1.test_read()
            # IPADDR = '192.168.3.30'
            VLAN_NAME = '{}.{}'.format(self.interface,self.du_vlan)
            d = os.system(f'sudo ip link add link {self.interface} name {self.interface}.{self.du_vlan} type vlan id {self.du_vlan}')
            d = os.system(f'sudo ifconfig {self.interface}.{self.du_vlan} {IPADDR} up')
            d = os.system('sudo /etc/init.d/isc-dhcp-server restart')
            st = subprocess.getoutput('sudo /etc/init.d/isc-dhcp-server status')
            li_of_interfaces = list(ifcfg.interfaces().keys())
            if VLAN_NAME in li_of_interfaces:
                return True,IPADDR
            else:
                return False,IPADDR

    #######################################################################
    ## Check The vlan tag is persent in DHCP Discover message
    #######################################################################
    def check_vlan_tag(self,pkt):
        summary = pkt.summary()
        try:
            if 'DHCP' in summary:
                if pkt.vlan:
                    first_vlan_tag_ru = pkt.vlan
                    print('\nfirst_vlan_tag_of_ru: {}\n'.format(pkt.vlan))
                    self.du_vlan = pkt.vlan + 5
                    # self.create_vlan(DU_vlan)
                    #######################################################################
                    ## Check Vlan comes from RU and Create Vlan in Test PC
                    #######################################################################
                    return True
        except Exception as e:
            # print(e)
            return False
        
    def check_dhcp_ack(self,pkt):
        summary = pkt.summary()
        try:
            if 'DHCP' in summary:
                if pkt.vlan == self.du_vlan and pkt['DHCP'].options[0][1] == 5:
                    print('Got ip to the VLAN...')
                    print('VLAN IP is : {}'.format(pkt['IP'].dst))
                    return True
        except Exception as e:
            # print(e)
            return False


    #######################################################################
    ## Sniffing(reading) live packets
    #######################################################################
    def read_live_packets(self,iface = 'wlp0s20f3'):
        pkts = sniff(iface = iface, stop_filter = self.check_vlan_tag, timeout = 10)
        for pkt in pkts:
            val = self.check_vlan_tag(pkt)
            if val:
                break
        else:
            return False
        wrpcap('vlan_tag.pcap', pkts)
        self.create_vlan()
        pkts2 = sniff(iface = iface, stop_filter = self.check_dhcp_ack,timeout = 10)
        for pkt in pkts2:
            val = self.check_dhcp_ack(pkt)
            if val:
                break
        else:
            return False
        wrpcap('{}/dhcp.pcap'.format(parent), pkts2)
        # wrpcap('{}\M_CTC_ID_001.pcap'.format(parent),pkts)
        return True
        # print(pkts)


    #######################################################################
    ## Check The vlan tag is persent in DHCP Discover message
    #######################################################################
    def ethtool_linked(self,interface):
                    # STARTUP.STORE_DATA(interface,OUTPUT_LIST=OUTPUT_LIST)
        cmd = "sudo ethtool " + interface
        # STARTUP.STORE_DATA(cmd,OUTPUT_LIST=OUTPUT_LIST)
        gp = os.popen(cmd)
        fat=gp.read().split('\n')
        for line in fat:
            # STARTUP.STORE_DATA(line,OUTPUT_LIST=OUTPUT_LIST)
            if "Speed" in line and ('25000' in line or '10000' in line):
                return interface


    #######################################################################
    ## Check SFP Link is detected
    #######################################################################
    def linked_detected(self):
        # t = time.time() + 100
        t = time.time() + 10
        while time.time() < t:
            Interfaces = list(ifcfg.interfaces().keys())
            for interface in Interfaces:
                # print(interface)
                if '.' not in interface:
                    if self.ethtool_linked(interface):
                        self.interface = self.ethtool_linked(interface)
                        if self.interface !=None:
                            print('\n ********** SFP Link is detected!!! ********** \n')
                            return self.interface
                        else:
                            return self.interface
        else:
            print('\n ********** SFP is not Connected!!! ********** \n')
            return False

    #######################################################################
    ## Check SFP Link is detected
    #######################################################################
    def check_tcp_ip(self,pkt):
        summary = pkt.summary()
        try:
            if 'TCP' in summary:
                # pkt.show()
                if  pkt['TCP'].flags == 'RA' or pkt['TCP'].sport == 4334 or pkt['TCP'].sport == 830:
                    print('Got ip to the Fronthaul Interface...')
                    print('Fronthaul Interface IP is : {}'.format(pkt['IP'].dst))
                    self.hostname = pkt['IP'].dst
                    # print(self.hostname)
                    time.sleep(5)
                    return True
        except Exception as e:
            # print(e)
            return False
        pass


if __name__ == "__main__":
    obj = vlan_Creation()
    interface = obj.linked_detected()
    if interface == False:
        pass
    else:
        sniff(iface = interface, stop_filter = obj.check_tcp_ip)
        # obj1 = ISC_DHCP_SERVER.test_DHCP_CONF()
        # obj1.test_read('lo',random.randint(0,1))
        # obj.read_live_packets(iface=obj.interface)
        pass
    pass