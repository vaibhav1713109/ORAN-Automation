import time,datetime, paramiko
from MPlane_SyncState import *
from Notification import notification

def NT_SyncE_1pps(ResultFile, Destination, MPlane, IP_Board):

    print('-'*100)
    print('-'*36 + "Noise Transfer - PTP to 1pps"+'-'*36)

    try:
        ResultFile = ResultFile+str(datetime.date.today())

        from calnexRest import calnexGet, calnexSet, calnexCatGenerateReport, calnexDownloadFile

        def is_link_up(port):   #Checking Port Link
                """ Is the link up on the specified port """
                eth_link = "UNDEFINED"
                link_state = "UNDEFINED"

                leds = calnexGet("results/statusleds")
                if port == 0:
                    eth_link = 'ethLink_0'
                else:
                    eth_link = 'ethLink_1'

                for led in leds:
                    if led['Name'] == eth_link:
                        link_state = led['State']
                if link_state == 'Link':
                    return True
                else:
                    return False
        def ssh():  #SSH Session communication for acquiring PTP status from DUT
            try:
                cmd = "cat /tmp/ptp_sync_status.txt"
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect("192.168.1.10",22,"root","b1b3")
                stdin, stdout, stderr = ssh.exec_command(cmd)
                ptp_response = stdout.readlines()
                ssh.close()
                return ptp_response
            except Exception as error:
                notification("SSH Exception: {}".format(str(error)))
                return

        #Select Preset as Conformance Test
        #calnexSet("instrument/preset", "Name", 'Conformance Test - G.8273.2 Standard')
        i=0
        try:
            while(i<5):
            
                port1_link = is_link_up(1)
                port2_link = is_link_up(2)

                FEC_Status_Port1 = calnexGet("physical/port/ethernet/Port1/sfp28")  #Checking the port status
                FEC_Status_Port2 = calnexGet("physical/port/ethernet/Port2/sfp28")
                if (FEC_Status_Port1["Fec"] and FEC_Status_Port2["Fec"]):
                    print("RS-FEC is enabled on both ports.")
                else:
                    print("RS-FEC is disabled on both ports.")
                
                if port1_link and port2_link:   #Loop termination if link up
                    break   
                else:
                    i+=1

        except Exception as error:
                if port1_link: 
                    notification("Port 2 is not up!!!")
                else:
                    notification("Port 1 is not up!!!")
        
        #Enabling the 1pps time error in Measurement
        calnexSet("app/conformance/test", "Test", 'SyncE to 1pps Noise Transfer')

        #Configure the clock as Slave mode
        calnexSet("app/mse/testmode", "TestMode", 'SlaveClock')

        #Starting the Generation
        calnexSet("app/conformance/generation/start")
        
        if (MPlane.isupper()== "NO"):
            while(1):
                try:
                    status = ssh()
                    if (status[0] == '0\n'):
                        time.sleep(20)

                    else:
                        print(status[0])
                        break
                except Exception as error:
                    notification("SSH Data reading error: {}".format(str(error)))
        else:
            PTP_State = session_login(IP_Board, 830, 'root', 'root') 
            print('-'*100)
            print(f"\nPTP Synchronization: {PTP_State}")
              
        #Starting the Measurement
        calnexSet("app/conformance/measurement/start")

        time.sleep(10)

        #Selecting metrics for the report
        calnexSet("cat/measurement/SyncE/B/TIE/-/isenabled", "Value", False)
        calnexSet("cat/measurement/ESMC/B/ESMC/Rx/isenabled", "Value", False)
        calnexSet("cat/measurement/ESMC/B/ESMC/Tx/isenabled", "Value", False)
        calnexSet("cat/measurement/PortEvents/E/PortEvents/-/isenabled", "Value", False)
        calnexSet("cat/measurement/1ppsTEAbsolute/F/ONEPPS/-/isenabled", "Value", False)
        calnexSet("cat/measurement/1ppsTEAbsolute/F/FILTEREDTIMEERROR/-/isenabled", "Value", False)
        calnexSet("cat/measurement/1ppsTEAbsolute/F/CTE/-/isenabled", "Value", False)
        time.sleep(5)

        #calnexSet("cat/measurement/1ppsTEAbsolute/F/TransientResponse/-/isenabled", "Value", True)
        calnexSet("cat/measurement/1ppsTEAbsolute/F/SyncENoiseTransfer/-/mask", "MaskName", 'G.8273.2 Class A,B T-BCs Noise Transfer')
        calnexSet("cat/measurement/1ppsTEAbsolute/F/SyncENoiseTransfer/-/visiblewindow", "XMin", 0, "XMax", 0, "YMin", 0, "YMax", 0)
        #Get the elapsed time and replace the time.sleep method.
        time.sleep(4680)
        while(1):
            ETA = calnexGet("app/conformance/estimatedremainingtime")
            if (ETA["EstimatedRemainingTime"]) == 0:
                break
            else:
                print('Looping')
                time.sleep(5)
        #Stopping the generation after the measurement period.
        calnexSet("app/conformance/measurement/stop")
    
        calnexSet("app/conformance/generation/stop")   #Stopping the generation.
    
        #Report data to be exported
        calnexSet("cat/report/data", "EditableFields", [{"Key":"Report Title","Value":"Noise Transfer - SyncE to 1pps"},{"Key":"Report Description","Value":""},{"Key":"Company","Value":"VVDN Technologies Pvt Ltd"},{"Key":"User Name","Value":""},{"Key":"Network Operator","Value":""},{"Key":"Test Location","Value":"Kochi, India"},{"Key":"Notes","Value":""},{"Key":"Device Under Test;0","Value":"MAVU_DBRU"},{"Key":"Device Under Test;1","Value":"TRX1"},{"Key":"Frequency Reference Source;0","Value":"INTERNAL"},{"Key":"Frequency Reference Source;1","Value":""},{"Key":"Sync-E Source;0","Value":"INTERNAL"},{"Key":"Sync-E Source;1","Value":""},{"Key":"E1 or T1 Source;0","Value":""},{"Key":"E1 or T1 Source;1","Value":""},{"Key":"1pps Source;0","Value":"INTERNAL"},{"Key":"1pps Source;1","Value":""},{"Key":"1588 Information;0","Value":""},{"Key":"1588 Information;1","Value":""},{"Key":"E Description","Value":""},{"Key":"F Description","Value":""}])

        time.sleep(10)

        #Creating the report and saved in the file management of Neo
        calnexCatGenerateReport(ResultFile)

        #dest_folder = "/home/vcbelt0294/Desktop/Automation/S_Plane/Demo/Reports"

        calnexDownloadFile("CatFolder",'Reports', ResultFile,Destination )

        notification("Noise Transfer - SyncE to 1PPS Test Finished!")

        calnexSet("app/conformance/generation/stop")
    
    except Exception as error:

        notification("Exception: {}".format(str(error)))
        print("Testing Aborted due to exception!")
        print('-'*100)
        calnexSet("app/conformance/measurement/stop")   #Stopping the measurement.

        calnexSet("app/conformance/generation/stop")   #Stopping the generation.

    return
