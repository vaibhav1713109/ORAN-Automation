from logging import exception
import socket
import sys, os, warnings
#warnings.simplefilter("ignore", DeprecationWarning)
from ncclient import manager, operations
import string
from ncclient.operations import rpc
from ncclient.operations.rpc import RPCError
from ncclient.xml_ import to_ele
import xmltodict
import xml.dom.minidom
import subprocess
import paramiko
import time
import re
from ncclient.transport import errors
#xml_1 = open('o-ran-interfaces.xml').read()
from paramiko.ssh_exception import NoValidConnectionsError
from ncclient.operations.errors import TimeoutExpiredError
from ncclient.transport.errors import SessionCloseError
import maskpass
import STARTUP






def session_login(host, port, user, password,macs,ip_a):
    with manager.connect(host=host, port=port, username=user, hostkey_verify=False, password=password, allow_agent = False , look_for_keys = False) as m:
        
        try:
            print('-'*100)
            print('\n\n\t\t********** Connect to the NETCONF Server ***********\n\n')
            print('-'*100)
        
            # rpc=m.create_subscription()
            print(f'''> connect --ssh --host {host} --port 830 --login {user}
                    Interactive SSH Authentication
                    Type your password:
                    Password: 
                    > status
                    Current NETCONF session:
                    ID          : {m.session_id}
                    Host        : {host}
                    Port        : {port}
                    Transport   : SSH
                    Capabilities:
                    ''')
            for i in m.server_capabilities:
                print("\t",i)
            # print('-'*100)
            # print("\n\n########### Initial Get#####################\n\n")
            # print('-'*100)    
            # print('-'*100)
            # print('\n>get --filter-xpath /o-ran-sync:sync')
            # print('-'*100)
            # SYNC = '''<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            #     <sync xmlns="urn:o-ran:sync:1.0">
            #     </sync>
            #     </filter>
            #     '''
            # data  = m.get(SYNC).data_xml
            # dict_Sync = xmltodict.parse(str(data))
            # x = xml.dom.minidom.parseString(data)
            

            # xml_pretty_str = x.toprettyxml()

            # print(xml_pretty_str)
            # print('-'*100)


            print('-'*100)
            print("\n\n###########Step 1 The TER NETCONF Client periodically tests O-RU’s sync-status until the LOCKED state is reached.#####################\n\n")
            print('-'*100)    
            print('-'*100)
            print('\n>get --filter-xpath /o-ran-sync:sync')
            print('-'*100)
            while True:
                SYNC = '''<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <sync xmlns="urn:o-ran:sync:1.0">
                </sync>
                </filter>
                '''
                data  = m.get(SYNC).data_xml
                dict_Sync = xmltodict.parse(str(data))
                state = dict_Sync['data']['sync']['sync-status']['sync-state']
                if state == 'LOCKED':

                    x = xml.dom.minidom.parseString(data)
                    

                    xml_pretty_str = x.toprettyxml()

                    print(xml_pretty_str)
                    print('-'*100)
                    break
    
            cap = m.create_subscription()
            print('-'*100)
            print('\t\t********** Create Subscription ***********')
            print('-'*100)
            print('>subscribe')
            print('-'*100)
            dict_data = xmltodict.parse(str(cap))
            if dict_data['nc:rpc-reply']['nc:ok']== None:
                print('\nOk\n')
            print('-'*100)
            print('\t\t********** Interface yang  Get Filter ***********')
            print('-'*100)
            print('\n>get --filter-xpath /ietf-interfaces:interfaces')
            print('-'*100)
            v_name1 = '''
                    <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                    <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
                    </interfaces>
                    </filter>
            '''
            interface_s = m.get(v_name1).data_xml
            x = xml.dom.minidom.parseString(interface_s)
            

            xml_pretty_str = x.toprettyxml()

            print(xml_pretty_str)
            print('-'*100)
            num = ip_a[3]
            xml_data = open("Yang_FUNC_xml/M_FTC_ID_060.xml").read()
            xml_data = xml_data.format(interface_name=ip_a,mac=mac,number=num)
            u1 =f'''
                 <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                 {xml_data}
                 </config>'''
            print('*'*100)
            print('\t\t*******  TER NETCONF Client sends <Intarface xml> to the O-RU NETCONF Server ********')
            print('*'*100)
            print('\n> edit-config --target running --config --defop replace\n')
            print('-'*100)
            print('\t\t*******  Replace with XMl ********')
            print('*'*100)
            print(xml_data)
            print('-'*100)
            d = m.edit_config(target='running',config=u1)
            print('-'*100)
            print(d)
            print('*'*100)
            dict_data = xmltodict.parse(str(d))
            '''d = m.dispatch(to_ele(xml_data))
            print('-'*100)
            print(d)
            print('*'*100)
            dict_data = xmltodict(str(d))
            if dict_data ['nc:rpc-reply']['nc:reject-reason']== ' Invalid value {vlan-id} in "vlan-id" element':
                pass
            else :
                return ['nc:rpc-reply']['nc:reject-reason']
                
            '''

        except RPCError as e:
            if e.message[0:13] == 'Invalid value':
                print('-'*100)
                print("\n\n###########  Rpc Reply ####################\n\n")
                print('-'*100)
                print('ERROR')
                print('-'*100)
                print(f"\t{'tag' : <20}{':' : ^10}{e.tag: ^10}")
                print(f"\t{'type' : <20}{':' : ^10}{e.type: ^10}")
                print(f"\t{'severity' : <20}{':' : ^10}{e.severity: ^10}")
                print(f"\t{'path' : <20}{':' : ^10}{e.path: ^10}")
                print(f"\t{'message' : <20}{':' : ^10}{e.message: ^10}")
            #print(f"{'error-info' : <20}{':' : ^10}{e: ^10}")
               # print(f"\n{'Description' : <20}{':' : ^10}{e.message: ^10}")
            #print(f"{'error-tag' : <20}{':' : ^10}{e.errlist: ^10}")
            else:
                return [e.tag, e.type, e.severity, e,e.message]
            print('-'*100)


       
def isValidMACAddress(str):
 
    # Regex to check valid MAC address
    regex = ("^([0-9A-Fa-f]{2}[:-])" +
             "{5}([0-9A-Fa-f]{2})|" +
             "([0-9a-fA-F]{4}\\." +
             "[0-9a-fA-F]{4}\\." +
             "[0-9a-fA-F]{4})$")
 
    # Compile the ReGex
    p = re.compile(regex)
 
    # If the string is empty
    # return false
    if (str == None):
        return False
 
    # Return if the string
    # matched the ReGex
    if(re.search(p, str)):
        return True
    else:
        return False



if __name__ == '__main__':
   #give the input configuration in xml file format
   #xml_1 = open('o-ran-hardware.xml').read()
   #give the input in the format hostname, port, username, password 
    print('-'*100)
    user = input('Enter username for login : ')
    print('\n','-'*100)
    pswd = maskpass.askpass('Enter password for login : ', mask='*')
    print('-'*100)
    


    try:
        m = manager.call_home(host = '', port=4334, hostkey_verify=False,username = user, password = pswd, timeout = 60, allow_agent = False , look_for_keys = False)
        li = m._session._transport.sock.getpeername()
       # print(li)
        sid = m.session_id
        #print(sid)
        if m:
            STARTUP.kill_ssn(li[0],830, user, pswd,sid)
            
            users, slots, macs = STARTUP.demo(li[0], 830, user, pswd)
            # users['root'] = 'root'
            del slots['swRecoverySlot']
            
            for key, val in slots.items():
                if val[0] == 'true' and val[1] == 'true':
                    print(f'''**
        * --------------------------------------------------------------------------------------------
        *              VVDN CONFIDENTIAL
        *  -----------------------------------------------------------------------------------------------
        * Copyright (c) 2016 - 2020 VVDN Technologies Pvt Ltd.
        * All rights reserved
        *
        * NOTICE:
        *  This software is confidential and proprietary to VVDN Technologies.
        *  No part of this software may be reproduced, stored, transmitted,
        *  disclosed or used in any form or by any means other than as expressly
        *  provided by the written Software License Agreement between
        *  VVDN Technologies and its license.
        *
        * PERMISSION:
        *  Permission is hereby granted to everyone in VVDN Technologies
        *  to use the software without restriction, including without limitation
        *  the rights to use, copy, modify, merge, with modifications.
        *
        * ------------------------------------------------------------------------------------------------
        * @file    M_FTC_ID_053_.txt
        * @brief    M PLANE O-RAN  FUNCTIONAL
        * @credits Created based on Software Release for GIRU_revC-- v{val[2]}
                        
                        ''')

            

            
            # print('-'*100)
            # print('\t\t*******User Available In RU ********')
            # print('-'*100)
            # print('-'*100)

            # print('-'*100)    
            print(f"{'Interface_Name' : <30}{'|' : ^10}{'MAC_ADD': ^10}")
            print('-'*100)
            for key, val in macs.items():
                print(f"{key : <30}{'=' : ^10}{val: ^10}")
            # users['root'] = 'root'
            print('-'*100)
            # print('-'*100)
            # print(f"{'SR_NO' : <30}{'User_Name' : <30}{'=' : ^10}{'Password': ^10}")
            # print('-'*100)
            # i=1
            # for key, val in users.items():
            #     print(f"{i : <30}{key : <30}{'=' : ^10}{val: ^10}")
            #     i+=1
            
            print('-'*100)
            ip_a = 'eth0'
            mac = macs[ip_a]
            time.sleep(5)
            res = session_login(li[0],830,user,pswd,mac,ip_a)
            #print(res)
            if res:
                time.sleep(5)
                
                print('\n','*'*100)
                STARTUP.GET_SYSTEM_LOGS(li[0], user, pswd)
                print('\n','*'*100)
                if type(res) == list:
                    print('\n','*'*100)
                    print('*'*20,'FAIL_REASON','*'*20)
                    print('\n','*'*100)
                    print(f"{'error-tag' : <20}{':' : ^10}{res[0]: ^10}")
                    print(f"{'error-type' : <20}{':' : ^10}{res[1]: ^10}")
                    print(f"{'error-severity' : <20}{':' : ^10}{res[2]: ^10}")
                    #print(f"{'error-info' : <20}{':' : ^10}{res[3]: ^10}")
                    print(f"{'Description' : <20}{':' : ^10}{res[4]: ^10}")
                else:
                    print(f"{'configuration-status' : <20}{':' : ^10}{res: ^10}")
                print('\n','*'*100)
                print(f"{'STATUS' : <50}{'=' : ^20}{'FAIL' : ^20}")
                print('\n','*'*100)

            else:
                # For Capturing the logs
                time.sleep(5)
                
                print('\n','*'*100)
                STARTUP.GET_SYSTEM_LOGS(li[0], user, pswd)
                print('\n','*'*100)
                print(f"{'STATUS' : <50}{'=' : ^20}{'PASS' : ^20}")
                print('\n','*'*100)
                

    except errors.SSHError as e:
        print('-'*100)
        print(e,': SSH Socket connection lost....')
        print('-'*100)
    
    except socket.timeout as e:
        print('-'*100)
        print(e,': Call Home is not initiated....')
        print('-'*100)
    except socket.timeout as e:
        print('-'*100)
        print(e,': Call Home is not initiated, Timout expired....')
        print('-'*100)

    except errors.AuthenticationError as e:
            print('-'*100)
            print(e,"Invalid username/password........")
            print('-'*100)

    except NoValidConnectionsError as e:
        print('-'*100)
        print(e,'')
        print('-'*100)

    except TimeoutError as e:
        print('-'*100)
        print(e,': Call Home is not initiated, Timout Expired....')
        print('-'*100)

    except SessionCloseError as e:
        print('-'*100)
        print(e,"Unexpected_Session_Closed....")
        print('-'*100)

    except TimeoutExpiredError as e:
        print('-'*100)
        print(e,"....")
        print('-'*100)

    except OSError as e:
        print('-'*100)
        print(e,': Call Home is not initiated, Please wait for sometime........')
        print('-'*100)


    except exception as e:
        print('-'*100)
        print("*"*30+'Exception'+"*"*30)
        print('-'*100)
        print('\t\t',e)
        print('-'*100)

                
                
    except exception as e:
        print('-'*100)
        print("*"*30+'Exception'+"*"*30)
        print('-'*100)
        print('\t\t',e)
        print('-'*100)

