import sys
import psutil
import os
import time
import clr
from configparser import ConfigParser

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# print(root_dir)
configur = ConfigParser()
configur.read('{}/Requirement/inputs.ini'.format(root_dir))

sys.path.append(r"C:\ORAN_AUTOMATION\CUPLANE\Dependencies")

clr.AddReference(r"C:\ORAN_AUTOMATION\CUPLANE\Dependencies\Agilent.SA.Vsa.Interfaces.dll")
#clr.AddReference(r"C:\ORAN_AUTOMATION\CUPLANE\Dependencies\Agilent.SA.Vsa.DigitalDemod.Interfaces.dll")
clr.AddReference("System")
clr.AddReference("System.Linq")
clr.AddReference("System.Threading.Tasks")
from Agilent.SA.Vsa import*
#from Agilent.SA.Vsa.DigitalDemod import*

def VSA_Function(test_case_name,duplex_type,eAxID):
    try:
        output_summary = []
        print("============================================================================================")
        print("=========================== 89600 VSA CONFIGURATION ========================================")
        print("============================================================================================")


        if ("Agilent.SA.Vsa.Vector-x64.exe" in (p.name() for p in psutil.process_iter())):
            print("89600 VSA Application is already running.")
        else:
            print("Starting 89600 VSA Application...")
            # os.startfile("C:\Program Files\Keysight\89600 Software 2023\89600 VSA Software\Agilent.SA.Vsa.Vector-x64.exe")
            os.startfile(r"C:\Program Files\Keysight\89600 Software 2023_U1\89600 VSA Software\Agilent.SA.Vsa.Vector-x64.exe")
            time.sleep(30)

        app = ApplicationFactory.Create()
        app.Preset()
        app.Measurements.SelectedItem.PresetTraces()
        app.Display.Traces.RemoveExtra()
        app.Measurements.SelectedItem.Restart()
        time.sleep(3)
        print("- Recall .setx file to VSA")
        if 'PRACH' not in test_case_name:
            file_name = root_dir + '\\' + duplex_type +"\Results\{0}\{1}\CTC_5GNR.NR_Carrier_1-1_UL.setx".format(test_case_name,f'EAXCID{eAxID}')
        else:
            file_name = root_dir + '\\' + duplex_type +"\Results\{0}\{1}\CTC_5GNR.NR_Carrier_1-0_PRACH.setx".format(test_case_name,f'EAXCID{eAxID}')
        try:
            app.RecallSetup(file_name)
            app.Title = "UL_Constellation _Verification"
            time.sleep(3)
            print("- Recall Recording .ORB file to VSA")
            orb_filename = root_dir + '\\' + duplex_type +"\Results\{0}\EAXCID{1}\CTC_5GNR_recovered_iq.{1}_mu1_ant1.iqt.orb".format(test_case_name,eAxID)
            # orb_filename = root_dir + '\\' + duplex_type +"\Results\{0}\captured 2023-04-13--19-01-06.1_mu1_ant1.iqt.orb".format(test_case_name)
            app.Measurements.SelectedItem.Input.Recording.RecallFile(orb_filename, "ORB", RecordPaddingType.RepetitionPadding, 5.0)
            # app.Measurements.SelectedItem.Input.Recording.RecallFile(orb_filename)
        except Exception as e:
            print(e)
        finally:
            app.Measurements.SelectedItem.Restart()
        time.sleep(2)
        app.Display.Traces[3].IsVisible = bool(0)
        app.Display.Traces[3].DataName = "No Data"
        app.Display.Traces.SelectedIndex = 2
        app.Display.Traces.SelectedItem.DataName = "Slot Summary1"

        ############## Saving the result of Slot Summary1 ##############
        save_filename = root_dir + '\\' + duplex_type +"\Results\{0}\EAXCID{1}\VSA_Screenshot_1".format(test_case_name,eAxID)
        time.sleep(3)
        app.Display.Printer.SaveBitmap(save_filename, BitmapType.Png)
        time.sleep(1)

        ################ Decoded Data Info ################
        if 'PRACH' not in test_case_name:
            app.Display.Traces.SelectedIndex = 2
            app.Display.Traces.SelectedItem.DataName = "Decoded Info1"
            mesure_data2 = app.Display.Traces.SelectedItem.MeasurementData
            crc_pass = crc_fail = 0
            decoded_data_info = mesure_data2.SummaryNames
            print("{0}\n#{1}#\n{0}".format('='*100,'Decoded Info Data'.center(98)))
            crc_data = []
            for name in decoded_data_info:
                print(f"{name} : {mesure_data2.Summary(name)}")
                crc_data.append(f"{name} : {mesure_data2.Summary(name)}")
                if 'CRC=Fail' in mesure_data2.Summary(name):
                    output_summary.append('Crc is Fail')
                    crc_fail+=1
                elif 'CRC=Pass' in mesure_data2.Summary(name):
                    crc_pass ==1
            print(crc_data)
            
        ############## Saving the result of Decoded Info1 ##############
        image_path = root_dir + '\\' + duplex_type +"\Results\{0}\EAXCID{1}"
        save_filename = root_dir + '\\' + duplex_type +"\Results\{0}\EAXCID{1}\VSA_Screenshot_2".format(test_case_name,eAxID)
        time.sleep(1)
        app.Display.Printer.SaveBitmap(save_filename, BitmapType.Png)

        
        ################ Summary Info ################
        app.Display.Traces.SelectedIndex = 4
        app.Display.Traces.SelectedItem.DataName = "Summary1"
        mesure_data = app.Display.Traces.SelectedItem.MeasurementData
        # print(mesure_data)
        # print(dir(mesure_data))
        print("{0}\n#{1}#\n{0}".format('='*100,'Summary Info'.center(98)))
        EVM_status = False
        summary_info = mesure_data.SummaryNames
        print(summary_info)
        captured_evm = 0 
        for name in summary_info:
            if name in ['ChannelPower','EVM','FrequencyError','EVMPk']:
                print(f"{name} : {mesure_data.Summary(name)}")
                if name == 'EVM' and '**' in str(mesure_data.Summary(name)):
                    output_summary.append('EVM is more then 5%')
                    EVM_status = False
                elif name == 'EVM'  and float(mesure_data.Summary(name)) < float(5):
                    output_summary.append('EVM is more then 5%')
                    EVM_status = True
                    captured_evm = str(mesure_data.Summary(name))
                else:
                    pass

        ################ Result Declaration ################
        print("{0}\n#{1}#\n{0}".format('='*100,'Result Declaration'.center(98)))
        # print(crc_status,EVM_status)
        if crc_fail != 0 or EVM_status!=True:
            Error = f'CRC : {"Fail" if (crc_pass ==0 and crc_fail == 0) or crc_fail >0 else "Pass"}\nEVM : {"Pass" if EVM_status ==True else "Fail"}'
            print(Error)
            return (captured_evm), crc_data, 'Fail', image_path
            
        else:
            print(f'CRC : Pass\nEVM : Pass')
            return str(captured_evm), crc_data, 'Pass', image_path
    except Exception as e:
        print(f'VSA_Function Error : {e}')
        return 0, [], 'Fail', ''


if __name__ == "__main__":
    if len(sys.argv)>3:
        test_case_name = sys.argv[1]
        duplex_type = sys.argv[2]
        VSA_Function(test_case_name,duplex_type,sys.argv[3])
    else:
        print('Please run with below format\npython vsa_constellation_and_result_capture.py {test_case_name} {duplex_type} {eaxcid}')
