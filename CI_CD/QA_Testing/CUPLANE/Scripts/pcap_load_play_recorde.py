import requests
import time,os,sys
from configparser import ConfigParser
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# print(root_dir)
configur = ConfigParser()
configur.read('{}/Requirement/inputs.ini'.format(root_dir))



def Pcap_Load_and_Data_play_record_(test_case_name,Duplex_Type,eAxID):
    try:
        print("============================================================================================")
        print("============================PLAYER AND RECORDER FUNCTION====================================")
        print("============================================================================================")

        url = "http://localhost:9000/Modules/0/"

        #url = "http://localhost:9000/Modules/1/"

        #Player Recorder Functions
        filename = f"{root_dir}\\{Duplex_Type}\\Results\\{test_case_name}\\EAXCID{eAxID}\\CTC_5GNR.pcap"
        print(filename)
        files = {
        'data': (filename, open(filename, 'rb')),
        }
        payload = dict(state='on', radioframes='0')
        headers = {
        'Content-Type': 'application/json',
        }
        
        #load pcap
        resp = requests.post(url+"Player/pcap",files = files)
        print("Load Pcap Status:" + str(resp.content)[1:] +"\t Response Code:" + str(resp.status_code))
        
        #start Recorder
        data = '{"state":"on","radioframes":1}'
        resp = requests.put(url+"Recorder",data=data,headers = headers)
        print("Start Recorder Response:" + str(resp.content)[1:]+"\t Response Code:" + str(resp.status_code))
        
        #Get Recorder state
        resp = requests.get(url+"Recorder",data=payload)
        print("Recorder State:" + resp.text+"\t Response Code:" + str(resp.status_code))
        
        #start player
        data = '{"state":"on","radioframes":0}'
        resp = requests.put(url+"Player",data=data,headers = headers)
        # input()
        print("Start Player Response:" + str(resp.content)[1:]+"\t Response Code:" + str(resp.status_code))
        
        # input()
        #Getplayer state
        resp = requests.get(url+"Player",data=payload)
        print("Player State:" + resp.text+"\t Response Code:" + str(resp.status_code))
        
        time.sleep(3)
        
        #Get Recorder state
        resp = requests.get(url+"Recorder",data=payload)
        #time.sleep(15)
        print("Recorder State:" + resp.text+"\t Response Code:" + str(resp.status_code))
        
        #stop recorder
        data = '{"state":"off","radioframes":1}'
        resp = requests.put(url+"Recorder",data=data,headers = headers)
        print("Stop Recorder Response:" + str(resp.content)[1:]+"\t Response Code:" + str(resp.status_code))
        
        #getRecorder pcap
        file = open(filename[:-5] + "_captured.pcap", "wb")
        resp = requests.get(url+"Recorder/pcap")
        file.write(resp.content)
        file.close()
        print("Copied the Pcap")
        
        print("The Packets are Transmiting ....")
        
        print("============================================================================================")
        print("============================================================================================")
        return True
    except Exception as e:
        print(f'Pcap_Load_and_Data_play_record_ Error : {e}')
        return f'Pcap_Load_and_Data_play_record_ Error : {e}'
    
if __name__ == "__main__":
    if len(sys.argv)>2:
        test_case_name = sys.argv[1]
        Pcap_Load_and_Data_play_record_(test_case_name,sys.argv[2],sys.argv[3])
    else:
        print('Please run with below format\npython pcap_load_play_recorde.py {test_case_name} {Duplex_Type Eg. TDD/FDD} {eaxcid}')