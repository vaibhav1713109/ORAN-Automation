import requests
import xmltodict
from dict2xml import dict2xml
from bs4 import BeautifulSoup
url = "http://localhost:9000/Modules"

print("\n********************INSTRUMENT CONFIGURATION********************\n")

#Get Module List
payload = dict(id='0',model='S5040A',address='PXI0::2-0.0::INSTR')
resp = requests.get(url,data=payload)
print("Get Module List:"+ str(resp.content)[1:]+"\t Response Code:" + str(resp.status_code))
url = "http://localhost:9000/Modules/0/"
#Configure Module
instrumentconfig = 'C:\\Users\\Administrator\\Documents\\Keysight\\Open RAN Studio\\InstrumentConfig.xml'
with open('C:\\Users\\Administrator\\Documents\\Keysight\\Open RAN Studio\\InstrumentConfig.xml', 'r') as f:
    data = f.read()
Bs_data = BeautifulSoup(data, "xml")
my_dict = xmltodict.parse(str(Bs_data))

my_dict['ModuleConfigSchema']['Modules']['FpgaModule']['TimeSyncConfig']['PtpMode'] = "Disabled"

xml = dict2xml(my_dict)


with open('C:\\Users\\Administrator\\Documents\\Keysight\\Open RAN Studio\\InstrumentConfig.xml', 'w') as f:
    f.writelines(xml)
files = {
    'data': (instrumentconfig, open(instrumentconfig, 'rb')),
}
resp = requests.post(url+"Configure",files = files)
print("Load Configuration Status:" + str(resp.content)[1:] +"\t Response Code:" + str(resp.status_code))
print("Instrument Configured Successfully")
print("End.")
print("\n************************MASTER DISABLED**************************\n")
