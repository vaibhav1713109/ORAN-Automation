from scapy.all import *
import ifcfg

def checktcp_ip(pkt):
	summary = pkt.summary()
	if 'TCP' in summary:
		interfaces = ifcfg.interfaces()
		mac_address = interfaces['eth1']['ether']
		
		if mac_address == pkt.src:
			interface = pkt['IP'].dst
			du_intercae =pkt['IP'].src
			print(interface,du_intercae)
			return True
		if mac_address == pkt.dst:
			interface = pkt['IP'].src
			du_intercae =pkt['IP'].dst
			print(interface,du_intercae)
			return True

interface = ''
du_intercae = ''
pkt = sniff(iface = 'eth1', stop_filter = checktcp_ip, timeout = 20)


# interfaces = ifcfg.interfaces()
# mac_address = interfaces['eth1']['ether']

# if mac_address == pkt_1.src:
# 	interface = pkt_1['IP'].src
# 	du_intercae =pkt_1['IP'].dst
# elif mac_address == pkt_1.dst:
# 	interface = pkt_1['IP'].dst
# 	du_intercae =pkt_1['IP'].src
