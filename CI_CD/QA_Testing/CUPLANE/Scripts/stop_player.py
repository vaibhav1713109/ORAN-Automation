import requests
import time,os
root_dir = os.path.dirname(os.path.dirname(__file__))
# print(root_dir)


def Stop_Player():
    try:
        
        print("============================================================================================")
        print("=========================================STOP FUNCTION======================================")
        print("============================================================================================")


        url = "http://localhost:9000/Modules/0/"

        #url = "http://localhost:9000/Modules/1/"


        payload = dict(state='on', radioframes='0')
        headers = {
        'Content-Type': 'application/json',
        }


        #Getplayer state
        resp = requests.get(url+"Player",data=payload)
        print("Player State:" + resp.text+"\t Response Code:" + str(resp.status_code))

        #stop player
        data = '{"state":"off","radioframes":1}'
        resp = requests.put(url+"Player",data=data,headers = headers)
        print("Stop Player Response:" + str(resp.content)[1:]+"\t Response Code:" + str(resp.status_code))

        print("============================================================================================")
        print("============================================================================================")
        print("The Player stopped the transmission")
        return True
    except Exception as e:
        print(f'Stop_Player Error : {e}')
        return f'Stop_Player Error : {e}'

if __name__ == "__main__":
    Stop_Player()