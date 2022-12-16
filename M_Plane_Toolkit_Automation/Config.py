import json

dhcp_server_ip=input("Enter IP of ORS: ")
o_ru_ip=input("Enter IP of O-RU: ")
username=input("Enter Username: ")
password=input("Enter Password: ")
sys_log_path=input("Enter System Log Path: ")
sys_log_file=input("Enter System Log File Name: ")
ru_mac=input("Enter Mac Address of O-RU: ")
du_mac=input("Enter Mac Address of ORS: ")
arfcn=input("Enter ARFCN: ")
def write_json(new_data, filename='configurations.json'):
    with open(filename,'w') as file:
        json.dump(new_data, file, indent = 4)

with open ("configurations.json") as json_file:
    data=json.load(json_file)
    x= {"dhcp_server_ip": dhcp_server_ip, "o_ru_ip": o_ru_ip, "username": username, "password": password, "sys_log_path": sys_log_path, "sys_log_file": sys_log_file,"ru_mac":ru_mac,"du_mac":du_mac,"arfcn":arfcn}
    data.update(x)
    
write_json(data)

