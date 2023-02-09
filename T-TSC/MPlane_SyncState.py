import os, time
from ncclient import manager
from ncclient.operations.rpc import RPCError
import xmltodict
import xml.dom.minidom
from Notification import *
from ncclient.xml_ import to_ele

def session_login(host, port, user, password):
    with manager.connect(host=host, port=port, username=user, hostkey_verify=False, password=password) as m:
        print('-'*100)
        print('\n\t\t********** Connect to the NETCONF Server ***********\n')
        print('-'*100)
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

        try:

            sub = """<create-subscription xmlns="urn:ietf:params:xml:ns:netconf:notification:1.0">
                        <filter type="subtree">
                                <synchronization-state-change xmlns="urn:o-ran:sync:1.0"></synchronization-state-change>
                        </filter>
                    </create-subscription>"""
            rpc=m.dispatch(to_ele(sub))
            
            while (1):
                notf = m.take_notification(True).notification_xml 
                if notf is None:
                    time.sleep(10)
                else:
                    notf_data = xmltodict.parse(str(notf))
                    LockState = (notf_data['notification']['synchronization-state-change']['sync-state'])
                    if (LockState == "LOCKED"):
                        break

        except RPCError as e:
            print('-'*100)
            print('\n\n\t\t********** SYSTEM ERROR************\n\n')
            print('-'*100)
            print(e)
            notification(e)
        
        return LockState

if __name__ == '__main__':    
    pass
#   session_login('192.168.1.10',830, 'root', 'root')
    
