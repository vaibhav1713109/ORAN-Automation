import datetime, time, paramiko
from MPlane_SyncState import *
from Notification import notification

def Noise_Generation(ResultFile, Destination, MPlane, IP_Board):

    print('-'*100)
    print('-'*42 + "Noise Generation"+'-'*42)

    Measurement_time = int(input("Enter the Measurement period for Noise Generation Test [in sec]: "))

    try:
    
        ResultFile = ResultFile+str(datetime.date.today())   # Enter the Result File name

        from calnexRest import  calnexGet, calnexSet, calnexCatGenerateReport, calnexDownloadFile

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
                    notification("Status of Port No: {} is not up".format(port))
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


        #calnexSet("instrument/preset", "Name", 'Conformance Test - G.8273.2 Standard')  #Select Preset as Conformance Test

        #Conditional based looping to check the port link
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

        calnexSet("app/conformance/test", "Test", 'Noise Generation')

        calnexSet("app/mse/testmode", "TestMode", 'SlaveClock') #Configure the clock as Slave mode

        calnexSet("app/conformance/generation/start")   #Starting the Generation

        #Waiting for the PTP to acquire Sync and checking the temp file for status.
        if (MPlane.isupper() == "NO"):
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

        calnexSet("app/conformance/measurement", "OnePps", True)    #Enabling the 1pps time error in Measurement

        time.sleep(3)

        calnexSet("app/conformance/measurement/start")  #Starting the Measurement

        time.sleep(50)
        calnexSet("cat/measurement/PortEvents/E/PortEvents/-/isenabled", "Value", False)
        calnexSet("cat/measurement/Sync/D/PDV/-/isenabled", "Value", False)
        calnexSet("cat/measurement/Sync/D/CF/-/isenabled", "Value", False)
        calnexSet("cat/measurement/DelayReq/D/PDV/-/isenabled", "Value", False)
        calnexSet("cat/measurement/DelayReq/D/CF/-/isenabled", "Value", False)
        calnexSet("cat/measurement/1ppsTEAbsolute/F/DTE/-/isenabled", "Value", True)
        calnexSet("cat/measurement/1ppsTEAbsolute/F/DTETDEV/-/isenabled", "Value", True)
        calnexSet("cat/measurement/1ppsTEAbsolute/F/DTEMTIE/-/isenabled", "Value", True)
        calnexSet("cat/measurement/1ppsTEAbsolute/F/DTEHF/-/isenabled", "Value", True)
        calnexSet("cat/measurement/1ppsTEAbsolute/F/ONEPPS/-/threshold/limit", "Value", 0.03)
        calnexSet("cat/measurement/1ppsTEAbsolute/F/ONEPPS/-/offsetremoval", "Enable", True)
        calnexSet("cat/measurement/1ppsTEAbsolute/F/CTE/-", "Parameters", {"AveragingPeriod":100}, "verifyMode", 1)
        calnexSet("cat/measurement/1ppsTEAbsolute/F/DTEMTIE/-/mask", "MaskName", 'G.8273.2 T-BC Class C Dynamic TE LF Const. Temp.')
        calnexSet("cat/measurement/1ppsTEAbsolute/F/DTEMTIE/-/visiblewindow", "XMin", 0, "XMax", 0, "YMin", 0, "YMax", 0)
        calnexSet("cat/measurement/1ppsTEAbsolute/F/DTETDEV/-/mask", "MaskName", 'G.8273.2 T-BC Class C Dynamic TE LF Const. Temp.')
        calnexSet("cat/measurement/1ppsTEAbsolute/F/DTETDEV/-/visiblewindow", "XMin", 0, "XMax", 0, "YMin", 0, "YMax", 0)
        calnexSet("cat/measurement/1ppsTEAbsolute/F/FILTEREDTIMEERROR/-/threshold/limit", "Value", 0.03)
        calnexSet("cat/measurement/1ppsTEAbsolute/F/FILTEREDTIMEERROR/-/threshold/enable", "Value", True)
        calnexSet("cat/measurement/1ppsTEAbsolute/F/FILTEREDTIMEERROR/-/visiblewindow", "XMin", 0, "XMax", 0, "YMin", 0, "YMax", 0)
        calnexSet("cat/measurement/1ppsTEAbsolute/F/CTE/-/threshold/limit", "Value", 0.01)
        calnexSet("cat/measurement/1ppsTEAbsolute/F/DTE/-/threshold/limit", "Value", 0.03)
        calnexSet("cat/measurement/1ppsTEAbsolute/F/DTE/-/threshold/enable", "Value", True)
        calnexSet("cat/measurement/1ppsTEAbsolute/F/DTE/-/visiblewindow", "XMin", 0, "XMax", 0, "YMin", 0, "YMax", 0)
        
        time.sleep(Measurement_time)
        #Get the elapsed time and replace the time.sleep method.
        while(1):
            ETA = calnexGet("app/conformance/elapsedtime")
            if (ETA["MeasurementElapsedTime"]) >= Measurement_time:
                break
            else:
                print('Looping')
                time.sleep(5)

        calnexSet("app/conformance/measurement/stop")   #Stopping the measurement.

        calnexSet("app/conformance/generation/stop")   #Stopping the generation.

        #Report data to be exported
        calnexSet("cat/report/data", "EditableFields", [{"Key":"Report Title","Value":"Noise Generation - Class C"},{"Key":"Report Description","Value":""},{"Key":"Company","Value":"VVDN Technologies Pvt Ltd"},{"Key":"User Name","Value":""},{"Key":"Network Operator","Value":""},{"Key":"Test Location","Value":"Kochi, India"},{"Key":"Notes","Value":""},{"Key":"Device Under Test;0","Value":"MAVU_DBRU"},{"Key":"Device Under Test;1","Value":"TRX1"},{"Key":"Frequency Reference Source;0","Value":"INTERNAL"},{"Key":"Frequency Reference Source;1","Value":""},{"Key":"Sync-E Source;0","Value":"INTERNAL"},{"Key":"Sync-E Source;1","Value":""},{"Key":"E1 or T1 Source;0","Value":""},{"Key":"E1 or T1 Source;1","Value":""},{"Key":"1pps Source;0","Value":"INTERNAL"},{"Key":"1pps Source;1","Value":""},{"Key":"1588 Information;0","Value":""},{"Key":"1588 Information;1","Value":""},{"Key":"E Description","Value":""},{"Key":"F Description","Value":""}])

        time.sleep(5)

        calnexCatGenerateReport(ResultFile)

        calnexDownloadFile("CatFolder",'Reports', ResultFile,Destination )

        notification("Noise Generation Test Finished!")
        print("\nNoise Generation is executed successfully!")
        
        calnexSet("app/conformance/generation/stop")
    
    except Exception as error:
        
        notification("Exception: {}".format(str(error)))
        print("Test Aborted due to exception!")
        print('-'*100)
        calnexSet("app/conformance/measurement/stop")   #Stopping the measurement.

        calnexSet("app/conformance/generation/stop")   #Stopping the generation.
        
    return