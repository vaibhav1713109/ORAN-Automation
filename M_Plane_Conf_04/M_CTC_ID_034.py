
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
from ncclient.transport import errors
#xml_1 = open('o-ran-interfaces.xml').read()
from paramiko.ssh_exception import NoValidConnectionsError
from ncclient.operations.errors import TimeoutExpiredError
from ncclient.transport.errors import SessionCloseError
import lxml.etree
import maskpass
import STARTUP



def session_login(host, port, user, password,rmt, pswrd):
    try:
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
                cap = m.create_subscription()
                print('-'*100)
                print('>subscribe')
                print('-'*100)
                dict_data = xmltodict.parse(str(cap))
                if dict_data['nc:rpc-reply']['nc:ok']== None:
                    print('\nOk\n')
                print('-'*100)

                
                xml_data = open("/home/vvdn/Python_script/GARUDA_AUTOMAT/Yang_xml/troubleshooting_start.xml").read()
                print('*'*100)
                print('\t\t*******  TER NETCONF Client sends <rpc><start-troubleshooting-logs> to the O-RU NETCONF Server ********')
                print('*'*100)
                print('\n> user-rpc\n')
                print('-'*100)
                print(xml_data)
                print('-'*100)
                d = m.dispatch(to_ele(xml_data))
                print('-'*100)
                print('\t\t*******Rpc Reply ********')
                print('-'*100)
                print(d)
                print('*'*100)
                print('\t\t******* O-RU NETCONF Server starts generating one or more file(s) containing troubleshooting logs  and send <notification><troubleshooting-log-generated>********')
                print('*'*100)
                timeout = time.time() + 60
                while time.time() < timeout:
                    n = m.take_notification()
                    notify = n.notification_xml
                    dict_n = xmltodict.parse(str(notify))
                    
                    try:
                        notf = dict_n['notification']['troubleshooting-log-generated']
                        file_name = dict_n['notification']['troubleshooting-log-generated']['log-file-name']
                        if notf:
                            x = xml.dom.minidom.parseString(notify)
                            #xml = xml.dom.minidom.parseString(user_name)

                            xml_pretty_str = x.toprettyxml()

                            print(xml_pretty_str)
                            print('-'*100)
                            break
                    
                    except:
                        pass
            except RPCError as e:
                return [e.tag, e.type, e.severity, e,e.message]

            
            # Troubleshooting log uploaded
            pub_k = subprocess.getoutput('cat /etc/ssh/ssh_host_rsa_key.pub')
            pk = pub_k.split()

            pub_key = pk[1]
            xml_data1 = open("/home/vvdn/Python_script/GARUDA_AUTOMAT/Yang_xml/TC_34.xml").read()
            xml_data = xml_data1.format(rmt_path=rmt,password=pswrd,pub_key= pub_key,t_logs = file_name)
            try:
                print('*'*100)
                print('\t\t******* Configuring File upload rpc toward Netconf ********')
                print('*'*100)
                print('\n> user-rpc\n')
                print('-'*100)
                print(xml_data)
                print('-'*100)
                print('\t\t******* Rpc Reply********')
                print('*'*100)
                d1 = m.dispatch(to_ele(xml_data))
                print(d1)
                print('-'*100)
                print('\n\n\t\t****** When file upload is completed, the O-RU NETCONF Server sends <notification><upload-notification> with status SUCCESS. ***********\n\n')
                print('-'*100)
                timeout = time.time() + 30
                while time.time() < timeout:
                
                    n = m.take_notification()
                    notify = n.notification_xml
                    dict_n = xmltodict.parse(str(notify))
                    try:
                        notf = dict_n['notification']['file-upload-notification']
                        if notf:
                            x = xml.dom.minidom.parseString(notify)
                            #xml = xml.dom.minidom.parseString(user_name)

                            xml_pretty_str = x.toprettyxml()

                            print(xml_pretty_str)
                            print('-'*100)
                            status = dict_n['notification']['file-upload-notification']['status']
                            if status != 'SUCCESS':
                                return f'File-upload-status {status}'
                            break
                        
                    except:
                        pass
            except RPCError as e:
                return [e.tag, e.type, e.severity, e.path ,e.message]
                    
    except RPCError as e:
            return [e.tag, e.type, e.severity, e.path, e.message]

    # except FileNotFoundError as e:
    #     print('-'*100)
    #     print("*"*30+'FileNotFoundError'+"*"*30)
    #     print('-'*100)
    #     print("\t\t",e)
    #     print('-'*100)
    #     return e
    
    # except lxml.etree.XMLSyntaxError as e:
    #         print('-'*100)
    #         print("*"*30+'XMLSyntaxError'+"*"*30)
    #         print('-'*100)
    #         print("\t\t",e)
    #         print('-'*100)
    #         return e 
    # 
    except Exception as e:
        print('-'*100)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(f"Error occured in line number {exc_tb.tb_lineno}")
        print('-'*100)
        print(e)
        print('-'*100)
        return e             
    



if __name__ == '__main__':
   #give the input configuration in xml file format
   #xml_1 = open('o-ran-hardware.xml').read()
   #give the input in the format hostname, port, username, password 
    print('-'*100)
    rmt = input('Give remote file path :\n')
    print(rmt)
    print('-'*100)
    pswrd = input('Give DU password :\n')
    print(pswrd)
    print('-'*100)
    
    try:
        
        print('-'*100)
        USER_N = input('Enter SUDO username for login : ')
        print('-'*100)
        PSWRD = maskpass.askpass('Enter SUDO password for login : ',mask='*')
        print('-'*100)
        m = manager.call_home(host = '', port=4334, hostkey_verify=False,username = USER_N, password = PSWRD, allow_agent = False , look_for_keys = False)
        li = m._session._transport.sock.getpeername()
        sid = m.session_id
        if m:
            print('-'*100)
            STARTUP.kill_ssn(li[0],830, USER_N, PSWRD,sid)
            users, slots = STARTUP.demo(li[0], 830, USER_N, PSWRD)
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
        * @file    M_CTC_ID_034_.txt
        * @brief    M PLANE O-RAN  Conformance
        * @credits Created based on Software Release for GIRU_revC-- v{val[2]}
                            
                            ''')
            
            
            time.sleep(5)
            res = session_login(li[0],830,USER_N, PSWRD,rmt,pswrd)

            if res:
                STARTUP.GET_SYSTEM_LOGS(li[0],USER_N,PSWRD)  
                print('\n','*'*100)
                if type(res) == list:
                    print('\n','*'*100)
                    print('*'*20,'FAIL_REASON','*'*20)
                    print('\n','*'*100)
                    print('ERROR')
                    print(f"\t{'error-tag' : <20}{':' : ^10}{res[0]: ^10}")
                    print(f"\t{'error-type' : <20}{':' : ^10}{res[1]: ^10}")
                    print(f"\t{'error-severity' : <20}{':' : ^10}{res[2]: ^10}")
                    print(f"\t{'path' : <20}{':' : ^10}{res[3]: ^10}")
                    print(f"\t{'Description' : <20}{':' : ^10}{res[4]: ^10}")
                else:
                    print('\n','*'*100)
                    print(f"{'FAIL_REASON' : <50}{'=' : ^20}{res : ^20}")
                    print('\n','*'*100)
                print('\n','*'*100)
                print(f"{'STATUS' : <50}{'=' : ^20}{'FAIL' : ^20}")
                print('\n','*'*100)

            else:
                # For Capturing the logs
                STARTUP.GET_SYSTEM_LOGS(li[0],USER_N,PSWRD)  
                print('\n','*'*100)
                print(f"{'STATUS' : <50}{'=' : ^20}{'PASS' : ^20}")
                print('\n','*'*100)
                
    except Exception as e:
        print('-'*100)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(f"Error occured in line number {exc_tb.tb_lineno}")
        print('-'*100)
        print(e)
        print('-'*100)

    # except errors.SSHError as e:
    #     print('-'*100)
    #     print(e,': SSH Socket connection lost....')
    #     print('-'*100)

    # except socket.timeout as e:
    #     print('-'*100)
    #     print(e,': Call Home is not initiated, Timout expired....')
    #     print('-'*100)

    # except errors.AuthenticationError as e:
    #         print('-'*100)
    #         print(e,"Invalid username/password........")
    #         print('-'*100)

    # except NoValidConnectionsError as e:
    #     print('-'*100)
    #     print(e,'')
    #     print('-'*100)

    # except TimeoutError as e:
    #     print('-'*100)
    #     print(e,': Call Home is not initiated, Timout Expired....')
    #     print('-'*100)

    # except SessionCloseError as e:
    #     print('-'*100)
    #     print(e,"Unexpected_Session_Closed....")
    #     print('-'*100)

    # except TimeoutExpiredError as e:
    #     print('-'*100)
    #     print(e,"....")
    #     print('-'*100)

    # except OSError as e:
    #     print('-'*100)
    #     print(e,': Call Home is not initiated, Please wait for sometime........')
    #     print('-'*100)