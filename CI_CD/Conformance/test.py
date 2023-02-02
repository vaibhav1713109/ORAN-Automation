# s = '''<?xml version="1.0" ?>
# <data xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
#         <software-inventory xmlns="urn:o-ran:software-management:1.0">
#                 <software-slot>
#                         <name>swSlot1</name>
#                         <status>VALID</status>
#                         <active>false</active>
#                         <running>true</running>
#                         <access>READ_WRITE</access>
#                         <product-code>STL O-RU</product-code>
#                         <vendor-code>VN</vendor-code>
#                         <build-id>90f0b6c</build-id>
#                         <build-name>Beta Release</build-name>
#                         <build-version>5.0.4</build-version>
#                         <files>
#                                 <name>boot</name>
#                                 <version>1.0.0</version>
#                                 <local-path>/media/sd-mmcblk0p1/BOOT0001.BIN</local-path>
#                                 <integrity>OK</integrity>
#                         </files>
#                         <files>
#                                 <name>kernel</name>
#                                 <version>1.0.0</version>
#                                 <local-path>/media/sd-mmcblk0p1/image0001.ub</local-path>
#                                 <integrity>OK</integrity>
#                         </files>
#                         <files>
#                                 <name>rootfs</name>
#                                 <version>1.0.0</version>
#                                 <local-path>/media/sd-mmcblk0p2/</local-path>
#                                 <integrity>OK</integrity>
#                         </files>
#                 </software-slot>
#                 <software-slot>
#                         <name>swSlot2</name>
#                         <status>VALID</status>
#                         <active>true</active>
#                         <running>false</running>
#                         <access>READ_WRITE</access>
#                         <product-code>VVDN O-RU</product-code>
#                         <vendor-code>VN</vendor-code>
#                         <build-id>90f0b6c</build-id>
#                         <build-name>Beta Release</build-name>
#                         <build-version>1.0.14</build-version>
#                         <files>
#                                 <name>boot</name>
#                                 <version>1.0.0</version>
#                                 <local-path>/media/sd-mmcblk0p1/BOOT0002.BIN</local-path>
#                                 <integrity>OK</integrity>
#                         </files>
#                         <files>
#                                 <name>kernel</name>
#                                 <version>1.0.0</version>
#                                 <local-path>/media/sd-mmcblk0p1/image0002.ub</local-path>
#                                 <integrity>OK</integrity>
#                         </files>
#                         <files>
#                                 <name>rootfs</name>
#                                 <version>1.0.0</version>
#                                 <local-path>/media/sd-mmcblk0p3/</local-path>
#                                 <integrity>OK</integrity>
#                         </files>
#                 </software-slot>
#                 <software-slot>
#                         <name>swRecoverySlot</name>
#                         <status>VALID</status>
#                         <active>false</active>
#                         <running>false</running>
#                         <access>READ_ONLY</access>
#                         <product-code>VVDN=O-RU</product-code>
#                         <vendor-code>VN</vendor-code>
#                         <build-id>factory_img</build-id>
#                         <build-name>Beta Release</build-name>
#                         <build-version>1.0.7</build-version>
#                         <files>
#                                 <name>boot</name>
#                                 <version>1.0.0</version>
#                                 <local-path>/media/sd-mmcblk0p1/BOOT0003.BIN</local-path>
#                                 <integrity>OK</integrity>
#                         </files>
#                         <files>
#                                 <name>kernel</name>
#                                 <version>1.0.0</version>
#                                 <local-path>/media/sd-mmcblk0p1/golden.ub</local-path>
#                                 <integrity>OK</integrity>
#                         </files>
#                         <files>
#                                 <name>rootfs</name>
#                                 <version>1.0.0</version>
#                                 <local-path>/media/sd-mmcblk0p1/golden.ub</local-path>
#                                 <integrity>OK</integrity>
#                         </files>
#                 </software-slot>
#         </software-inventory>
# </data>'''

# import xmltodict
# slot_n1 = xmltodict.parse(str(s))
# inactive_slot = 'swSlot2'
# SLOTS1 = slot_n1['data']['software-inventory']['software-slot']
# del SLOTS1[2]
# print(SLOTS1)
# for slot in SLOTS1:
#     if slot['status'] == 'INVALID':
#         print(s)
#         print(f'SW slot status is Invid for {slot["name"]}...')
#     elif slot['name'] == inactive_slot:
#         if (slot['active'] == 'true') and slot['running'] == 'false':
#             pass
#         else:
#             print(s)
#             print(f"SW Inventory didn't update for {inactive_slot}...")

#     elif slot['name'] != inactive_slot:
#         if (slot['active'] != 'false') and slot['running'] != 'true':
#             print(s)
#             print(f"SW Inventory didn't update for {slot['name'] }...")
# print(s)
import os, sys
dir_name = os.path.dirname(os.path.abspath(__file__))
parent = os.path.dirname(dir_name)
# print(parent)
sys.path.append(parent)
d = {'Netopeer Connection, capability exchange and create-subscription :': 'Successful!!', 'Software VVDN_LPRU_v1.0.16.zip Activate :': 'Successfully activate on swSlot1!!', 'O-RU going for reboot:': 'Successful!!'}
from require import STARTUP
pdf = STARTUP.PDF_CAP()
a = tuple(zip(d.keys(),d.values()))
STARTUP.render_table_data(pdf,a)
STARTUP.CREATE_LOGS('test',PDF=pdf)
for i in a:
        print(f"{f'{i[0]}' : <70}{'=' : ^20}{f'{i[1]}' : ^20}")
