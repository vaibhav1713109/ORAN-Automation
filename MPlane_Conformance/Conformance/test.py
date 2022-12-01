import os, sys, xmltodict
from lxml import etree
from ncclient import manager
import paramiko
from datetime import datetime
from tabulate import tabulate
from fpdf import FPDF
from pathlib import Path
from configparser import ConfigParser
import time,socket
import logging
from ncclient.xml_ import to_ele, new_ele
from binascii import hexlify
logger = logging.getLogger('ncclient.manager')

def call_home(*args, **kwds):
    host = kwds["host"]
    port = kwds.get("port",4334)
    timeout = kwds["timeout"]
    srv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv_socket.bind((host, port))
    srv_socket.settimeout(timeout)
    srv_socket.listen()

    sock, remote_host = srv_socket.accept()
    logger.info('Callhome connection initiated from remote host {0}'.format(remote_host))
    kwds['sock'] = sock
    srv_socket.close()
    return manager.connect_ssh(*args, **kwds)


def session_login(host = '0.0.0.0',USER_N = '',PSWRD = ''):
    try:
        session = call_home(host = '0.0.0.0', port=4334, hostkey_verify=False,username = USER_N, password = PSWRD,timeout = 5,allow_agent = False , look_for_keys = False)
        hostname, call_home_port = session._session._transport.sock.getpeername()   #['ip_address', 'TCP_Port']
    except Exception as e:
        session = manager.connect(host = host, port=830, hostkey_verify=False,username = USER_N, password = PSWRD,timeout = 60,allow_agent = False , look_for_keys = False)
    return session



xml_data = '''
<hello xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
     <capabilities>
     </capabilities>
     <session-id/>
   </hello>

'''
try:
    session = session_login(host = '192.168.49.42',USER_N = 'root',PSWRD = 'root')
    print(dir(to_ele(xml_data)))
    print((to_ele(xml_data).xpath))
    rpc_reply = session.dispatch(to_ele(xml_data))
    print(rpc_reply)
except Exception as e:
    print(e.tag)
    print(e.type)
    print(e.severity)
    print(e.path)
    print(e.message)

