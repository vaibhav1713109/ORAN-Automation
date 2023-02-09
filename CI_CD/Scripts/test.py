st = '''isc-dhcp-server.service - ISC DHCP IPv4 server
Loaded: loaded (/lib/systemd/system/isc-dhcp-server.service; enabled; vendor preset: enabled)
Active: active (running) since Tue 2023-01-24 10:48:33 IST; 6h ago
Docs: man:dhcpd(8)
Main PID: 10024 (dhcpd)
Tasks: 1 (limit: 4915)
CGroup: /system.slice/isc-dhcp-server.service
cpd -user dhcpd -group dhcpd -f -4 -pf /run/dhcp-server/dhcpd.pid -cf /etc/dhcp/dhcpd.conf eth1.36
Jan 24 14:56:46 vvdn dhcpd[10024]: DHCPACK on 192.168.3.38 to 98:ae:71:00:8a:c2 (mcb1) via eth1.36
Jan 24 15:06:25 vvdn dhcpd[10024]: reuse_lease: lease age 1111 (secs) under 25% threshold, reply with unaltered, existing lease for 192.168.3.38
Jan 24 15:06:25 vvdn dhcpd[10024]: DHCPREQUEST for 192.168.3.38 from 98:ae:71:00:8a:c2 (mcb1) via eth1.36
Jan 24 15:06:25 vvdn dhcpd[10024]: DHCPACK on 192.168.3.38 to 98:ae:71:00:8a:c2 (mcb1) via eth1.36
Jan 24 15:48:25 vvdn dhcpd[10024]: Wrote 0 class decls to leases file.
Jan 24 15:48:25 vvdn dhcpd[10024]: Wrote 39 leases to leases file.
Jan 24 15:48:25 vvdn dhcpd[10024]: DHCPREQUEST for 192.168.3.38 from 98:ae:71:00:8a:c2 (mcb1) via eth1.36
Jan 24 15:48:25 vvdn dhcpd[10024]: DHCPACK on 192.168.3.38 to 98:ae:71:00:8a:c2 (mcb1) via eth1.36
Jan 24 16:41:36 vvdn dhcpd[10024]: DHCPREQUEST for 192.168.3.38 from 98:ae:71:00:8a:c2 (mcb1) via eth1.36
Jan 24 16:41:36 vvdn dhcpd[10024]: DHCPACK on 192.168.3.38 to 98:ae:71:00:8a:c2 (mcb1) via eth1.36'''

st = st.split('DHCPACK')
print(st[-1])
import re
# pattern = '([0-255]\.[0-255\.[0-255]\.[0-255])'
pattern = '(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'

ans = re.findall(pattern,st[-1])
print(ans)