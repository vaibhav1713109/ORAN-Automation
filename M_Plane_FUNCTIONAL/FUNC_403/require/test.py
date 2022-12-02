# import os
# import sys
# from fpdf import FPDF


# PDF = FPDF()
# PDF.add_page()
# # dir_path = os.path.dirname(__file__)
# abs_path = os.path.join('dejavu-fonts-ttf-2.37/ttf/','DejaVuSansCondensed.ttf')

# # PDF.set_font("DejaVu", size=9)

# def HEADING(PDF,data,*args):
#     PDF.add_font('DejaVu', '', abs_path, uni=True)
#     PDF.set_font("DejaVu", size=9)
#     PDF.write(5, '\n{}\n'.format('='*75))
#     PDF.write(5,data)
#     PDF.write(5, '\n{}\n'.format('='*75))
#     PDF.set_font("Times",style = '',size = 9)


# st = '''● isc-dhcp-server.service - ISC DHCP IPv4 server
#    Loaded: loaded (/lib/systemd/system/isc-dhcp-server.service; enabled; vendor preset: enabled)
#    Active: active (running) since Tue 2022-07-26 11:34:06 IST; 7min ago
#      Docs: man:dhcpd(8)
#  Main PID: 30976 (dhcpd)
#     Tasks: 1 (limit: 4915)
#    CGroup: /system.slice/isc-dhcp-server.service
#            └─30976 dhcpd -user dhcpd -group dhcpd -f -4 -pf /run/dhcp-server/dhcpd.pid -cf /etc/dhcp/dhcpd.conf eth1.20

# Jul 26 11:40:04 vvdn dhcpd[30976]: DHCPREQUEST for 192.168.214.37 from 98:ae:71:01:64:da (garuda) via eth1.20
# Jul 26 11:40:04 vvdn dhcpd[30976]: DHCPACK on 192.168.214.37 to 98:ae:71:01:64:da (garuda) via eth1.20
# Jul 26 11:40:07 vvdn dhcpd[30976]: reuse_lease: lease age 4 (secs) under 25% threshold, reply with unaltered, existing lease for 192.168.214.37
# Jul 26 11:40:07 vvdn dhcpd[30976]: DHCPREQUEST for 192.168.214.37 from 98:ae:71:01:64:da (garuda) via eth1.20
# Jul 26 11:40:07 vvdn dhcpd[30976]: DHCPACK on 192.168.214.37 to 98:ae:71:01:64:da (garuda) via eth1.20
# Jul 26 11:41:10 vvdn dhcpd[30976]: DHCPREQUEST for 192.168.214.37 from 98:ae:71:01:64:da (garuda) via eth1.20
# Jul 26 11:41:10 vvdn dhcpd[30976]: DHCPACK on 192.168.214.37 to 98:ae:71:01:64:da (garuda) via eth1.20
# Jul 26 11:41:11 vvdn dhcpd[30976]: reuse_lease: lease age 1 (secs) under 25% threshold, reply with unaltered, existing lease for 192.168.214.37
# Jul 26 11:41:11 vvdn dhcpd[30976]: DHCPREQUEST for 192.168.214.37 from 98:ae:71:01:64:da (garuda) via eth1.20
# Jul 26 11:41:11 vvdn dhcpd[30976]: DHCPACK on 192.168.214.37 to 98:ae:71:01:64:da (garuda) via eth1.20'''


# HEADING(PDF=PDF,data = st)
# PDF.output('OUTPUT.pdf')


st = 'sftp://vvdn@192.168.4.15:22/home/vvdn/Downloads/garuda_image/currupt_giru_v4.0.9.zip'

l = st.split(':22/')
print(l[1])