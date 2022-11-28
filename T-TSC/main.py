from Noise_Generation import Noise_Generation
from Noise_Tolerance import Noise_Tolerance
from Noise_Transfer1 import NT_PTP_1pps
from Noise_Transfer2 import NT_SyncE_1pps
from SyncE_1pps_Transient_Response import SyncE_1pps_TR
from calnexRest import calnexInit, calnexSet
from MPlane_SyncState import *
from Notification import notification
import sys

global IP, Destination

########################    User Input  ########################
IP = input("Enter the IP of Paragon Neo: ")
IP_Board = input("Enter the IP of Board:")
Link = input("Enter the Line rate as 10G or 25G: ")
FEC = input("RS-FEC status (Enable/Disable): ")
Destination = input("Enter the destination folder path: ")
Mplane = input("Will M-Plane Support in RU? (Yes/No)")

Programs = ["1. Noise Generation\n", 
                "2. Noise Tolerance\n", 
                "3. Noise Transfer - PTP to 1pps\n", 
                "4. Noise Transfer - SyncE to 1pps\n", 
                "5. Transient Response - SyncE to 1pps\n"]

[print(i) for i in Programs]
input_program = input("Enter the programs:")

to_execute = [input_program]
print(len(to_execute))
i=0
if len(to_execute)==1:
    input_split = to_execute[0].split(" ")
    input_split.sort()
else:
    print("Please enter valid input!!")

while(i<len(input_split)):  
    b1=int (input_split[i])-1
    #print (Programs[int(b1)])   
    i+=1
print(Destination)
################################################################
'''
if (Mplane.upper() == 'YES'):
    session_login(IP_Board, 830, 'root', 'root')
'''
########################    Remote Control of Paragon Neo   ########################
try:
    sys.path.append('//'+IP+'/calnex100g/RemoteControl/')
    calnexInit(IP)  #Establishing connection#

    if (Link.upper() == "25G"):
        calnexSet("physical/port/ethernet/Port1/sfp28/select")
    else:
        calnexSet("physical/port/ethernet/Port1/sfpplus/select")

    if (FEC.upper() == "ENABLE"):
        calnexSet("physical/port/ethernet/Port1/sfp28", "Fec", True)
    else:
        calnexSet("physical/port/ethernet/Port1/sfp28", "Fec", False)

    calnexSet("physical/measurement/onepps/unbalanced", "Termination", 'High')

    calnexSet("instrument/preset", "Name", 'Conformance Test - G.8273.2 Standard')



########################    Program Execution   ########################

    for i in range (0, len(input_split)):
        Access = input_split[i]
        if (Access == "1"):
            Noise_Generation("Noise_Generation-Class_C_", Destination, Mplane, IP_Board)
        elif (Access == "2"):
            Noise_Tolerance("Noise_Tolerance_", Destination)
        elif(Access == "3"):
            NT_PTP_1pps("Noise_Transfer-PTP_to_1pps_", Destination,Mplane,IP_Board)
        elif(Access == "4"):
            NT_SyncE_1pps("Noise_Transfer-SyncE_to_1pps_", Destination, Mplane, IP_Board)
        else:
            SyncE_1pps_TR("Transient_Response-SyncE_to_1pps_", Destination, Mplane, IP_Board)

    print("Testing Finished")

except Exception as error:
        print(type(error). __name__)
        notification("Exception: {}".format(str(error)))