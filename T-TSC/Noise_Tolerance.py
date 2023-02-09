# Include wrapper
import time, datetime, paramiko
from Notification import notification

def Noise_Tolerance(ResultFile, Destination, ):

    print('-'*100)
    print('-'*42 + "Noise Tolerance"+'-'*43)

    try:
        ResultFile = ResultFile+str(datetime.date.today())

        from calnexRest import calnexGet, calnexSet, calnexCatGenerateReport, calnexDownloadFile

        def is_link_up(port):
                """ Is the link up on the specified port """
                eth_link = "UNDEFINED"
                link_state = "UNDEFINED"

                leds = calnexGet("results/statusleds")
                if port == 0:
                    eth_link = 'ethLink_0'
                else:
                    eth_link = 'ethLink_1'

                for led in leds:
                    # print (led)
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
        calnexSet("app/conformance/test", "Test", 'Noise Tolerance')

        #Configure the clock as Slave mode
        calnexSet("app/mse/testmode", "TestMode", 'SlaveClock')
        calnexSet("app/conformance/measurement", "OnePps", True)
        #Starting the Generation
        calnexSet("app/conformance/generation/start")

        #Waiting for the PTP to acquire Sync and checking the temp file for status.
        while(1):
            try:
                status = ssh()
                if (status[0] == '0\n'):
                    time.sleep(20)

                else:
                    #print(status[0])
                    break
            except Exception as error:
                notification("SSH Data reading error: {}".format(str(error)))
        
        #Starting the Measurement
        calnexSet("app/conformance/measurement/start")

        time.sleep(10)
        
        calnexSet("cat/measurement/PortEvents/E/PortEvents/-/isenabled", "Value", False)
        calnexSet("cat/measurement/Sync/D/CF/-/isenabled", "Value", False)
        calnexSet("cat/measurement/Sync/D/PDV/-/isenabled", "Value", False)
        calnexSet("cat/measurement/DelayReq/D/PDV/-/isenabled", "Value", False)
        calnexSet("cat/measurement/DelayReq/D/CF/-/isenabled", "Value", False)
        calnexSet("cat/measurement/1ppsTEAbsolute/F/FILTEREDTIMEERROR/-/isenabled", "Value", False)
        calnexSet("cat/measurement/1ppsTEAbsolute/F/CTE/-/isenabled", "Value", False)
        count = 0
        while(1):
            ETA = calnexGet("app/conformance/estimatedremainingtime")
            if (ETA["EstimatedRemainingTime"]) != 0:
                status = ssh()
                if (status[0] == '1\n'):
                    count =0
                    time.sleep(5)
                else:
                    if(count == 0):
                        notification("Slave Clock is in Holdover!")
                        count+=1
                    time.sleep(5)
            else:
                break

        #Stopping the generation after the measurement period.
        calnexSet("app/conformance/measurement/stop")

        #Report data to be exported
        calnexSet("cat/report/data", "EditableFields", [{"Key":"Report Title","Value":"Noise Tolerance"},{"Key":"Report Description","Value":""},{"Key":"Company","Value":"VVDN Technologies Pvt Ltd"},{"Key":"User Name","Value":""},{"Key":"Network Operator","Value":""},{"Key":"Test Location","Value":"Kochi, India"},{"Key":"Notes","Value":""},{"Key":"Device Under Test;0","Value":" "},{"Key":"Device Under Test;1","Value":"TRX1"},{"Key":"Frequency Reference Source;0","Value":"INTERNAL"},{"Key":"Frequency Reference Source;1","Value":""},{"Key":"Sync-E Source;0","Value":"INTERNAL"},{"Key":"Sync-E Source;1","Value":""},{"Key":"E1 or T1 Source;0","Value":""},{"Key":"E1 or T1 Source;1","Value":""},{"Key":"1pps Source;0","Value":"INTERNAL"},{"Key":"1pps Source;1","Value":""},{"Key":"1588 Information;0","Value":""},{"Key":"1588 Information;1","Value":""},{"Key":"E Description","Value":""},{"Key":"F Description","Value":""}])

        time.sleep(10)

        calnexCatGenerateReport(ResultFile)

        calnexDownloadFile("CatFolder",'Reports', ResultFile,Destination )

        notification("Noise Tolerance Test Finished")

        calnexSet("app/conformance/generation/stop")

    except Exception as error:
        
        notification("Exception: {}".format(str(error)))
        
        calnexSet("app/conformance/measurement/stop")   #Stopping the measurement.

        calnexSet("app/conformance/generation/stop")   #Stopping the generation.
    
    return