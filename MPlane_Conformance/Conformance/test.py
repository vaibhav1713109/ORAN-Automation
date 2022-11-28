from ncclient import manager
from ncclient.xml_ import to_ele
from  ncclient.transport.errors import TransportError, SSHUnknownHostError, AuthenticationError
import time,socket
import logging

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

user = 'operator'
ip_address = '192.168.4'

for i in range(1):
    try:
        session = call_home(host='', port=4334, hostkey_verify=False, username='operator', password='admin123',timeout=60)
        print(session.session_id)
        xml_data='''<hello xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
    <capabilities>
      <capability>urn:ietf:params:netconf:base:1.1</capability>
    </capabilities>
  </hello>
'''
        rpc_command = to_ele(xml_data)
        d = session.rpc(rpc_command)
        print(d)
        session.close_session()
        time.sleep(5)

    except SSHUnknownHostError as e:
        LISTEN = f'''> listen --ssh --login {user}\nWaiting 60s for an SSH Call Home connection on port 4334...'''
        print(LISTEN)

        SSH_AUTH = f'''The authenticity of the host '::ffff:{ip_address}' cannot be established.
        ssh-rsa key fingerprint is 59:9e:90:48:f1:d7:6e:35:e8:d1:f6:1e:90:aa:a3:83:a0:6b:98:5a.
        Are you sure you want to continue connecting (yes/no)? no
        nc ERROR: Checking the host key failed.
        cmd_listen: Receiving SSH Call Home on port 4334 as user "{user}" failed.'''
        print(SSH_AUTH)
        print('{}\n'.format('-'*100))
    
    except AuthenticationError as e:
        print(e)
        print('Authenhdskdsdsjk')
        # socket.socket().close()
        # time.sleep(10)
        try:
            session.close_session()
        except Exception as e:
            print(e)

    except Exception as e:
        # socket.socket().close()
        print(e)
        # time.sleep(10)
        try:
            session.close_session()
        except Exception as e:
            print(e)
    finally:
        pass
        # time.sleep(10)
# import paramiko
# command = "cat {} | grep supervision;".format('/media/sd-mmcblk0p4/stli_bn40.log')
# ssh = paramiko.SSHClient()
# ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
# print('192.168.42.37', 22 ,'operator', 'admin123')
# ssh.connect('192.168.42.37', 22 ,'operator', 'admin123')
# stdin, stdout, stderr = ssh.exec_command(command)
# lines = stdout.readlines()
# for i in lines:
#     print(i)



# from netconf_client.connect import CallhomeManager
# from netconf_client.ncclient import Manager
# import xml.dom.minidom

# try:
#     with CallhomeManager(port=4334) as mgr:
#         print(dir(mgr))
#         mss = mgr.accept_one_ssh( port=830, username='operator', password='admin123', timeout = 10)
#         # for i in mss.server_capabilities:
#         #     print(i)
#         mss.session_id
#         hello_msg = mss.server_hello
#         s = xml.dom.minidom.parseString(hello_msg)
#         xml_pretty_str = s.toprettyxml()
#         print(xml_pretty_str)
# except Exception as e:
#     print(e)
# finally:
#     mss.close()