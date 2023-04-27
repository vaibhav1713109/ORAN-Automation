import sys,os,time
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
# clr.AddReference(r"C:\ORAN_AUTOMATION\CUPLANE\Dependencies\KalApi.dll")
clr.AddReference(r"C:\ORAN_AUTOMATION\CUPLANE\Dependencies\System.Runtime.InteropServices.RuntimeInformation.dll")
clr.AddReference("System")
clr.AddReference("System.Linq")
clr.AddReference("System.Threading.Tasks")
from Keysight.OpenRanStudio import*
from ErrorsLoggingTracing.Exceptions import*
# from Agilent.SA.Vsa import*


def ors_pcap_genration_prach(test_case_name,Duplex_Type,eAxID):
	try:
		myApi = Api()
		print("- Import Waveform Project (.scp)")
		#The method opens a project file (Signal Studio uses file extension ".scp") previously saved from Keysight Signal Studio. 
		file_name = f"{root_dir}\\{Duplex_Type}\\Results\\{test_case_name}\\EAXCID{eAxID}\\CTC_5GNR.scp"
		myProject = myApi.ImportWaveformProject(file_name)

		print("- Set ORS Configuration")
		myConfig = OrsConfiguration(myProject)

		#Set the flow/eAxC index table size -- Flow_TableSize(DataDirection  dir, int  size )
		myConfig.Flow_TableSize(OrsConfiguration.DataDirection.DL, 1)  
		myConfig.Flow_TableSize(OrsConfiguration.DataDirection.UL, 1)

		if len(sys.argv) > 2:
			bit_width = sys.argv[1]
		else:
			bit_width = 16
		eAxID = int(eAxID, 16)
		myConfig.Flow_TableEntry(OrsConfiguration.DataDirection.UL, 1, eAxID, 4, 4, 4, 4, OrsConfiguration.UPlaneCmpType.STATIC, OrsConfiguration.UPlaneCmpMethod.NONE, 16)

		# Set slot ID numbering scheme
		myConfig.Numerology_SlotIdNumberingScheme(2, muFR1 = 1, muFR2 = 4) 
		
		# Set bandwidth for IQ recovery
		myConfig.Numerology_RecoverIqFlowBandwidth(OrsConfiguration.Bandwidth.FR1_100M) 

		# Set numerology for IQ recovery
		myConfig.Numerology_RecoverIqFlowMu(OrsConfiguration.NumerologyType.Mu1) 

		myConfig.Numerology_PrachIqOption(True)
		if ('A3' in test_case_name):
			myConfig.Numerology_PrachPreambleFormat(OrsConfiguration.PRACH_Format.FormatA3)
			myConfig.Numerology_PrachScs(OrsConfiguration.PRACH_SCS.SCS30k)
		elif ('B4' in test_case_name):
			myConfig.Numerology_PrachPreambleFormat(OrsConfiguration.PRACH_Format.FormatB4)
			myConfig.Numerology_PrachScs(OrsConfiguration.PRACH_SCS.SCS30k)
		elif ('C2' in test_case_name):
			myConfig.Numerology_PrachPreambleFormat(OrsConfiguration.PRACH_Format.FormatC2)
			myConfig.Numerology_PrachScs(OrsConfiguration.PRACH_SCS.SCS30k)


		# Set the MTU, which impacts how stimulus packets are fragmented (on O-RAN application layer).
		myConfig.Networking_Mtu(9600)  

		# Sets VLAN ID
		myConfig.Options_VlanId(100) 

		# Sets Beam Forming Method
		myConfig.Beam_Method(OrsConfiguration.BfMethod.DISABLED)


		#Force the full-scale scaler to perform digital power scaling relative to 256QAM disregarding carrier modulation
		myConfig.Options_UseDpsFsFixed256QamScaler(True) 

		#myConfig.FlowIdxMap_AddCarrierMapEntry(0, 1) #Add mapping from a carrier (index) to a flow/eAxC ID. This variant is for simple waveforms (no MIMO). --AddCarrierMapEntry  ( int  carrierIdx,  int  flowId,  RAT_T  rat = RAT_T.NR)  
		myConfig.FlowIdxMap_AddCarrierMapEntry(0, eAxID)

		print("- Export Configuration file")
		myApi.ExportStimulus(myConfig)
		#myApi.GenerateBlerXmlFile()

		file_exists = os.path.exists(f"{root_dir}\\{Duplex_Type}\\Results\\{test_case_name}\\EAXCID{eAxID}\\CTC_5GNR.pcap")

		time.sleep(5)
		if file_exists:
			print("The pcap file exist")
		else:
			Error = "ORS_pcap_genration Error : The pcap file not exists"
			print(Error)
			return Error

		print('The pcap file is successfully generated')
		return True

	except Exception as e:
		print(f'ORS_pcap_genration Error : {e}')
		return f'ORS_pcap_genration Error : {e}'
	



if __name__ == "__main__":
	if len(sys.argv)>2:
		print(ors_pcap_genration_prach(sys.argv[1],sys.argv[2]))
	else:
		print('Please run with below format\npython pcap_gen.py {test_case_name} {Duplex_Type}')
