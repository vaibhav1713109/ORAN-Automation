import sys,os
from configparser import ConfigParser
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# print(root_dir)
configur = ConfigParser()
configur.read('{}/Requirement/inputs.ini'.format(root_dir))

import clr
sys.path.append("C:\Windows\Microsoft.NET\Framework\\v4.0.30319")
sys.path.append(r"C:\ORAN_AUTOMATION\CUPLANE\Dependencies")

clr.AddReference(r"C:\ORAN_AUTOMATION\CUPLANE\Dependencies\Open RAN Studio API.dll")
clr.AddReference(r"C:\ORAN_AUTOMATION\CUPLANE\Dependencies\xRAN Configuration.dll")
clr.AddReference(r"C:\ORAN_AUTOMATION\CUPLANE\Dependencies\xRAN Transport.dll")
clr.AddReference(r"C:\ORAN_AUTOMATION\CUPLANE\Dependencies\Errors Logging Tracing.dll")
# clr.AddReference(r"C:\ORAN_AUTOMATION\CUPLANE\Dependencies\Agilent.SA.Vsa.Interfaces.dll")
#clr.AddReference(r"C:\ORAN_AUTOMATION1\Dependencies\KalApi.dll")
clr.AddReference(r"C:\ORAN_AUTOMATION\CUPLANE\Dependencies\System.Runtime.InteropServices.RuntimeInformation.dll")
clr.AddReference("System")
clr.AddReference("System.Linq")
clr.AddReference("System.Threading.Tasks")
from Keysight.OpenRanStudio import*
from ErrorsLoggingTracing.Exceptions import*
# from Agilent.SA.Vsa import*


def Generate_ORB(test_case_name,duplex_type,eAxID):
    try:
        print("============================================================================================")
        print("============================Generate ORB from captured PCAP=================================")
        print("============================================================================================")
        
        
        #Api.ApplicationDirectory = "C:\Program Files\Keysight\Open RAN Studio"
        #Instantiation creates all resources necessary to subsequent API usage
        myApi = Api()
        
        pcap_filename = f"{root_dir}\\{duplex_type}\\Results\\{test_case_name}\\EAXCID{eAxID}\\CTC_5GNR_captured.pcap"
        orstx_filename = f"{root_dir}\\{duplex_type}\\Results\\{test_case_name}\\EAXCID{eAxID}\\CTC_5GNR.orstx"
        print(pcap_filename)
        print(orstx_filename)
        
        print("- Import PCAP in Explorer")
        myProject = myApi.Explorer(pcap_filename,orstx_filename)
        
        print("- Inspecting eAxID value of the packets")
        index = myProject.GetEaxcId(0)
        print("eAxID: ", index)
        
        print("- Filter Uplink Packets")
        # myProject.FilterPackets(OrsConfiguration.NumerologyType.Mu1, OrsConfiguration.DataDirection.UL, index, FieldTypes.MessageType.U_Plane)
        # myProject.FilterPackets(OrsConfiguration.DataDirection.UL, index, FieldTypes.MessageType.U_Plane)
        myProject.FilterPackets(OrsConfiguration.DataDirection.UL, index, FieldTypes.MessageType.U_Plane)
        
        save_file = f"{root_dir}\\{duplex_type}\\Results\\{test_case_name}\\EAXCID{eAxID}\\CTC_5GNR_recovered_iq"
        print("- Extract Uplink U plane IQ Data")
        myProject.RecoverIQTD(index, OrsConfiguration.DataDirection.UL, save_file)
        #myApi.close()
        print("ORB_Created Successfully")
        return True

    except Exception as e:
        print(f'Generate_ORB Error : {e}')
        return f'Generate_ORB Error : {e}'


if __name__ == "__main__":
    print(sys.argv)
    if len(sys.argv)>2:
        print(Generate_ORB(sys.argv[1],sys.argv[2],sys.argv[3]))
    else:
        print('Please run with below format\npython orb_gen.py {test_case_name} {duplex_type} {eAxID}')
