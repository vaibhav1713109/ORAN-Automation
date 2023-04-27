import subprocess, ifcfg, time
# from scapy.all import *

class Link_Detect():
    def __init__(self) -> None:
        self.interfaces_name = ifcfg.interfaces()
        self.INTERFACE_NAME = ''
        self.hostname = ''
        self.du_hostname = ''
        pass




    ############################################ Return the interface which is detected ############################################
    def test_ethtool_linked(self,interface):
        cmd = "ethtool " + interface
        Output = subprocess.getoutput(cmd).split('\n')
        for line in Output:
            # print(line)
            if "Speed" in line and ('10000' in line or '25000' in line):   
                # print(self.INTERFACE_NAME)
                return interface


    ############################################  Test whether link is detected. ############################################
    def link_detected(self):
        t = time.time()+60
        while t > time.time():
            Interfaces = list(self.interfaces_name.keys())
            # print(Interface)
            for i in Interfaces:
                # print(self.test_ethtool_linked(i))
                if '.' not in i:
                    self.INTERFACE_NAME = self.test_ethtool_linked(i)
                    if self.INTERFACE_NAME:
                        print('SFP link detected!!')
                        return self.INTERFACE_NAME,self.interfaces_name
        else:
            print('\n ********** SFP is not Connected!!! ********** \n')
            return False

    
def test_call():
    obj = Link_Detect()
    obj.link_detected()
    if obj.INTERFACE_NAME:
        print('Link Detected!!', obj.INTERFACE_NAME)
    # obj.ping_status()

if __name__ == "__main__":
    test_call()
