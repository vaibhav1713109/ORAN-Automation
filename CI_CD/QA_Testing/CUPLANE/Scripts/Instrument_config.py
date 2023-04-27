import sys, re, xmltodict
import os
import time
from configparser import ConfigParser
import requests
from dict2xml import dict2xml
from bs4 import BeautifulSoup

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# print(root_dir)
configur = ConfigParser()
configur.read('{}/Requirement/inputs.ini'.format(root_dir))




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
        with open('C:\\Users\\Administrator\\Documents\\Keysight\\Open RAN Studio\\InstrumentConfig.xml', 'r') as f:
            data = f.read()

        Bs_data = BeautifulSoup(data, "xml")
        my_dict = xmltodict.parse(str(Bs_data))
        my_dict['ModuleConfigSchema']['Modules']['FpgaModule']['TimeSyncConfig']['PtpMode'] = "Master"
        my_dict['ModuleConfigSchema']['Modules']['FpgaModule']['PortConfig']['PortSettings']['PortInfo'][0]['OruAddress'] = configur.get('INFO','ru_mac')
        xml = dict2xml(my_dict)
        with open('C:\\Users\\Administrator\\Documents\\Keysight\\Open RAN Studio\\InstrumentConfig.xml', 'w') as f:
            f.writelines(xml)
        files = {
            'data': (instrumentconfig, open(instrumentconfig, 'rb')),
        }
        resp = requests.post(url+"Configure",files = files)
        print("Load Configuration Status:" + str(resp.content)[1:] +"\t Response Code:" + str(resp.status_code))
        print("Instrument configured successfully")
        print("End.")
        print("============================================================================================")
        return True

    except Exception as e:
        print(f'ORS_instrument_Configuration Error : {e}')
        return f'ORS_instrument_Configuration Error : {e}'