import subprocess, ifcfg


class Link_Detect():

    def __init__(self) -> None:
        self.interfaces_name = ifcfg.interfaces()
        self.INTERFACE_NAME = ''
        pass

    ############################################ Return the interface which is detected ############################################
    def test_ethtool_linked(self,interface):
        cmd = "sudo ethtool " + interface
        Output = subprocess.getoutput(cmd).split('\n')
        for line in Output:
            # print(line)
            if "Speed" in line and ('10000' in line or '25000' in line):   
                # print(self.INTERFACE_NAME)
                return interface

    ############################################  Test whether link is detected. ############################################
    def test_linked_detected(self):
        Interfaces = list(self.interfaces_name.keys())
        # print(Interface)
        for i in Interfaces:
            # print(self.test_ethtool_linked(i))
            if '.' not in i:
                if self.test_ethtool_linked(i):
                    self.INTERFACE_NAME = self.test_ethtool_linked(i)
                    # print(linked_interface)
        return self.INTERFACE_NAME,self.interfaces_name



def test_call():
    obj = Link_Detect()
    obj.test_linked_detected()


if __name__ == "__main__":
    i = 0
    while True:
        print(i)
        i+=1
        test_call()