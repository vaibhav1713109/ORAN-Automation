import socket
import sys, os
import time
from tkinter.messagebox import NO
from ncclient import manager
import subprocess
from ncclient.transport import errors
from paramiko.ssh_exception import NoValidConnectionsError
from ncclient.operations.errors import TimeoutExpiredError
from ncclient.transport.errors import SessionCloseError
import STARTUP, ifcfg, random, Config
import DHCP_CONF.ISC_DHCP_SERVER as ISC_DHCP_SERVER
import DHCP_CONF.DHCP_CONF_VLAN as DHCP_CONF_VLAN



class M_CTC_ID_004():
    def __init__(self) -> None:
        pass

    def Linked_Detected():
        pass

    def Create_VLAN():
        pass

    def Call_Home():
        # store result for sw_version()
        pass

    def Result_Declaration():
        pass


def tes_Main():
    Obj = M_CTC_ID_004()
    Obj.Result_Declaration()
    pass