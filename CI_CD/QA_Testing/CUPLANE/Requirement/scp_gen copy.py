import sys, re
import os
import time
from configparser import ConfigParser
import requests

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(root_dir)
configur = ConfigParser()
configur.read('{}/Requirement/inputs.ini'.format(root_dir))


#import pythonnet
import clr
clr.AddReference(r"C:\ORAN_AUTOMATION\CUPLANE\Dependencies\Keysight.SignalStudio.N7631.dll")
from Keysight.SignalStudio.N7631 import *
from Keysight.SignalStudio import *



def ORS_instrument_Configuration():
    try:
        url = "http://localhost:9000/Modules"
        print("============================================================================================")
        print("============================INSTRUMENT CONFIGURATION========================================")
        print("============================================================================================")
        #Get Module List
        payload = dict(id='0',model='S5040A',address='PXI0::2-0.0::INSTR')
        resp = requests.get(url,data=payload)
        print("Get Module List:"+ str(resp.content)[1:]+"\t Response Code:" + str(resp.status_code))
        url = "http://localhost:9000/Modules/0/"
        #Configure Module
        instrumentconfig = r'C:\Users\Administrator\Documents\Keysight\Open RAN Studio\InstrumentConfig.xml'
        #instrumentconfig = "C:\\Demo\\InstrumentConfig.xml"
        files = {
            'data': (instrumentconfig, open(instrumentconfig, 'rb')),
        }
        resp = requests.post(url+"Configure",files = files)
        print("Load Configuration Status:" + str(resp.content)[1:] +"\t Response Code:" + str(resp.status_code))
        print("Instrument configured successfully")
        print("End.")
        print("============================================================================================")

    except Exception as e:
        print(f'ORS_instrument_Configuration Error : {e}')
        return f'ORS_instrument_Configuration Error : {e}'

def vxt_instrument_connection(VXT_Add, api):
    print('Connecting the instrumet')
    inst = VXT_Add
    b = api.ConnectInstrument(inst)
    #b = True
    #print(b)
    #print(type(b))
    return b


def Generate_Download(status, VXT_Add, api):    
    if status:
        print("Generating the configurations")
        api.Generate()
        print("- Connected to the Instrument at " + str(VXT_Add) + ".")
        api.Download()
        return True
    else:
        Error = " ############ Generate_Download Error : Instrument Connection failed ############"
        return Error


def scp_genration(test_case_name,RU_name):
    try:
        vxt_add = configur.get('INFO','VXT_Add')
        text_file_name = f"{root_dir}/Results/{RU_name}/{test_case_name}.txt"
        frequency = configur.get('INFO','DL_Center_Freq')
        ExternalDelayTime = configur.get('INFO','ExternalDelayTime')
        bandwidth = configur.get('INFO','bandwidth')
        # Read the APIs from ORS_APIs.txt file
        with open(text_file_name, 'r') as file:
            lines = file.readlines()
        api = Api()
        api.New()
        # Execute each API one by one
        for line in lines:
            # Your code to call the API and execute it
            if 'Frequency' in line:
                lineindex_of_freq = lines.index(line)
                lines[lineindex_of_freq] = f"api.SignalGenerator.Frequency = (float({frequency})*1000000000)\n"
            elif 'ExternalDelayTime' in line:
                lineindex_of_ext_delay = lines.index(line)
                lines[lineindex_of_ext_delay] = f"api.SignalGenerator.ExternalDelayTime = {ExternalDelayTime}\n"
            elif 'PresetDLTestModel' in line:
                split_line = line.split(',')
                lineindex_of_bandwidth = lines.index(line)
                replaced_line = re.sub('Bandwidth.FR1_.{1,3}M',f'Bandwidth.FR1_{bandwidth}M', split_line[0])
                split_line[0] = replaced_line
                line = ','.join(split_line)
                lines[lineindex_of_bandwidth] = line
            elif 'ULFRCConfig' in line:
                split_line = line.split(',')
                lineindex_of_bandwidth = lines.index(line)
                replaced_line = re.sub('Bandwidth.FR1_.{1,3}M',f'Bandwidth.FR1_{bandwidth}M', split_line[0])
                split_line[0] = replaced_line
                line = ','.join(split_line)
                lines[lineindex_of_bandwidth] = line

        for line in lines:
            print(f'Executing API: {line}')
            exec(f'{line}')
        with open(text_file_name, 'w+') as file1:
            file1.writelines(lines)

        # Generating the scp file
        print("Generating the scp file")
        Result_folder = f"{root_dir}\\Results\\{test_case_name}"
        if not os.path.exists(Result_folder):
            os.mkdir(Result_folder)
        api.SaveSettingsFile(f"{root_dir}\\Results\\{test_case_name}\\CTC_5GNR.scp")

        api.Close()

        time.sleep(5)
        api = Api()
        api.New()
        print(100*'*')
        print("Generating the scp for UL and give trigger..")
        print(100*'*')
        for line in lines:
            print(f'Executing API: {line}')
            exec(f'{line}')

        Result_folder = f"{root_dir}\\Results\\{test_case_name}"
        if not os.path.exists(Result_folder):
            os.mkdir(Result_folder)
        api.NR5GWaveformSettings.RemoveNRCarrier(0)
        print(f'Executing API: api.NR5GWaveformSettings.RemoveNRCarrier(0)')
        api.SaveSettingsFile(f"{root_dir}\\Results\\{test_case_name}\\CTC_5GNR_UL.scp")

        file_exists = os.path.exists(f"{root_dir}\\Results\\{test_case_name}\\CTC_5GNR.scp")

        time.sleep(5)
        if file_exists:
            print("The scp file exist")
        else:
            Error = "Scp_genration Error : The scp file not exists"  
            print(Error)
            return Error
        print('The scp file is successfully generated')
        vxt_connection_status = vxt_instrument_connection(VXT_Add=vxt_add,api=api)
        return Generate_Download(vxt_connection_status,vxt_add,api)
        # return True
 
    except Exception as e:
        print(f'Scp_genration Error : {e}')
        return f'Scp_genration Error : {e}'

    finally:
        print('Api connection closed')
        # api.Close()


if __name__ == "__main__":
    print(sys.argv)
    if len(sys.argv)>2:
        print(scp_genration(sys.argv[1],sys.argv[2]))
        # print(ORS_instrument_Configuration())
        # input('Enter once sync')
    else:
        print('Please run with below format\npython scp_gen.py {test_case_name} {RU_Name}')
