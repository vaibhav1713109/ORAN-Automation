import pyvisa
import time,os,sys,csv
from tabulate import tabulate
from configparser import ConfigParser


root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# print(root_dir)
configur = ConfigParser()
configur.read('{}/Requirement/inputs.ini'.format(root_dir))
sys.path.append(root_dir)
from Scripts.genrate_report import *


class vxt_configuration_and_result_capture():
    def __init__(self,test_case_name,duplex_type,eAxID) -> None:
        self.test_case_name = test_case_name
        self.duplex_type = duplex_type
        self.vxt_add = configur.get('INFO','VXT_Add')
        self.eaxid = eAxID
        self.bandwidth = configur.get('INFO','bandwidth')
        self.DL_Center_Freq = configur.get('INFO','DL_Center_Freq')
        self.Ext_Gain = float(configur.get('INFO','Ext_Gain'))*(-1)
        self.crc_file_name = "MeasR_00{}.csv".format(self.eaxid)
        print(self.vxt_add,self.bandwidth,self.DL_Center_Freq,self.Ext_Gain)
        self.base_extended = [
                    ":INST:SEL NR5G", ":OUTP:STAT OFF", ":FEED:RF:PORT:INP RFIN",':CONF:EVM', ":DISP:EVM:VIEW NORM",":INIT:CONT ON",
                    ":CCAR:REF {}GHZ".format(self.DL_Center_Freq),":RAD:STAN:PRES:CARR B{}M".format(self.bandwidth),":RAD:STAN:PRES:FREQ:RANG FR1", 
                    ":RAD:STAN:PRES:DMOD TDD", ":RAD:STAN:PRES:SCS SCS30K", ':RAD:STAN:PRES:RBAL DLTM1DOT1', 
                    ":RAD:STAN:PRES:DLIN:BS:CAT ALAR", ":RAD:STAN:PRES:IMM", ":EVM:CCAR0:DC:PUNC ON", ":EVM:CCAR0:PHAS:COMP:AUTO ON", ":EVM:CCAR0:PDCC1:INCL ON",
                    ":EVM:CCAR0:DEC:PDSC DESCrambled", ":EVM:CCAR0:DEC:PDCC DESCrambled", ":EVM:CCAR0:DEC:PBCH DESCrambled", ":DISP:EVM:WIND2:DATA DINF", ":EVM:CCAR0:PDSC1:MCS:TABL TABL2", 
                    ":EVM:CCAR0:PDSC1:MCS 4", ":EVM:CCAR0:PDSC2:MCS:TABL TABL2", ":EVM:CCAR0:PDSC2:MCS 4", 
                    ":EVM:CCAR0:PDSC3:MCS:TABL TABL2", ":EVM:CCAR0:PDSC3:MCS 4", ":EVM:CCAR0:PDSC4:MCS:TABL TABL2", 
                    ":EVM:CCAR0:PDSC4:MCS 4", ":CORR:BTS:GAIN {}".format(self.Ext_Gain)
                        ]
        self.compression_scpi = [
                    ":INST:SEL NR5G", ":OUTP:STAT OFF", ":FEED:RF:PORT:INP RFIN", ':CONF:EVM', ":DISP:EVM:VIEW NORM",":INIT:CONT ON",
                    ":CCAR:REF {}GHZ".format(self.DL_Center_Freq),":RAD:STAN:PRES:CARR B{}M".format(self.bandwidth),
                    ":RAD:STAN:PRES:FREQ:RANG FR1", ":RAD:STAN:PRES:DMOD TDD", ":RAD:STAN:PRES:SCS SCS30K",
                    ':RAD:STAN:PRES:RBAL DLTM3DOT1A', ":RAD:STAN:PRES:DLIN:BS:CAT ALAR", ":RAD:STAN:PRES:IMM", 
                    ":EVM:CCAR0:DC:PUNC ON",":EVM:CCAR0:PDCC1:INCL ON", ":EVM:CCAR0:DEC:PDSC DESCrambled", ":EVM:CCAR0:DEC:PDCC DESCrambled", ":EVM:CCAR0:DEC:PBCH DESCrambled", 
                    ":EVM:CCAR0:PDSC1:MCS:TABL TABL2", ":DISP:EVM:WIND2:DATA DINF", ":EVM:CCAR0:PDSC1:MCS 27", 
                    ":EVM:CCAR0:PDSC2:MCS:TABL TABL2", ":EVM:CCAR0:PDSC2:MCS 27", ":EVM:CCAR0:PDSC3:MCS:TABL TABL2", 
                    ":EVM:CCAR0:PDSC3:MCS 27", ":EVM:CCAR0:PDSC4:MCS:TABL TABL2", ":EVM:CCAR0:PDSC4:MCS 27",
                    ":CORR:BTS:GAIN {}".format(self.Ext_Gain), ":MMEM:STOR:SCR 'lat.png'"
                    ]
        
    def visa_connection(self,vxt_add = None, gpib_id= None):
        try:
            if(vxt_add):
                self.device = pyvisa.ResourceManager().open_resource(vxt_add)
                return True
            elif(gpib_id):
                self.device = pyvisa.ResourceManager().open_resource('GPIB0::{}::INSTR'.format(gpib_id)) 
                return True        
            else:
                Error = 'Visa_connection Error: No valid instrument IP or GBIB ID given'
                print(Error)
                return Error
        except Exception as e:
            Error = f'Visa_connection Error : {e}'
            print(Error)
            return Error
        
    def clear_status_reg_of_device(self):
        self.device.write('*CLS')                                #Clear Status Register of device
        self.device.write('*WAI')                                #Wait till Clear command is complete

    def reset_device(self):
        self.device.write('*RST')                                #Reset the device
        self.device.write('*WAI')                                #Wait till Reset command is complete
    
    def scpi_write(self, cmnd):
        self.device.write(cmnd)
        Error = ''
        for _ in range(10):
            try:
                status = self.device.query("*OPC?")
                print(cmnd , status[0])
                if status[0] == '1':
                    # print(status)
                    break
            except Exception as e:
                Error = f'Scpi_write Error {cmnd} : {e}'
                print(Error)
                time.sleep(1)
        else:
            return Error

    def Check_EVM_power(self):
        evm_limit = configur.get('INFO','evm_limit')
        power_limit = configur.get('INFO','power_limit').split()
        clgc_gain_calculation_time = configur.getint('INFO','clgc_gain_calculation_time')
        Error = ''
        captured_evm = 0
        output_power = 0
        for _ in range(3):
            for _ in range(10):
                try:
                    time.sleep(3)
                    self.device.timeout = 5000
                    CMD = ':FETCh:EVM000001?'
                    Res = self.device.query_ascii_values(CMD)
                    # print(Res)
                    captured_evm = "{:.2f}".format(float(Res[1]))
                    output_power = "{:.2f}".format(float(Res[0]))
                    print(captured_evm,output_power)
                    break
                except Exception as e:
                    Error = 'Check_EVM_power Error : {}'.format(e)
                    print(Error)
            if Error:
                return [Error]
            elif float(captured_evm) < float(evm_limit) and (float(output_power) > float(power_limit[0]) and float(output_power) < float(power_limit[1])):
                return captured_evm,output_power, True
            else:
                time.sleep(clgc_gain_calculation_time)
                pass
        else:
            return captured_evm,output_power, False
        
    def Check_Power(self):
        output_power = 0
        power_limit = configur.get('INFO','power_limit').split()
        Error = ''
        for _ in range(3):
            for _ in range(10):
                try:
                    time.sleep(3)
                    self.device.timeout = 5000
                    CMD = ':FETC:CHP?'
                    Res = self.device.query_ascii_values(CMD)
                    output_power = "{:.2f}".format(float(Res[1]))
                    break
                except Exception as e:
                    Error = 'Check_Power Error : {}'.format(e)
                    print(Error)
            
            if Error:
                return [Error]
            elif float(output_power) > float(power_limit[0]) and float(output_power) < float(power_limit[1]):
                return output_power, True
            else:
                pass
        else:
            return output_power, False

    def vxt_configuration(self,scpi_cmds):
        try:
            for scpi in scpi_cmds:
                self.scpi_write(scpi)
                time.sleep(1) 
            return True
        except Exception as e:
            Error = 'Run_scpi_cmnd Error : {}'.format(e)
            print(Error)
            return Error

    def verify_result_and_capture_screenshot(self):
        try:
            # power_result = self.Check_Power()
            power_evm_result = self.Check_EVM_power()
            crc_data = self.verify_CRC()
            filepath = r"C:\temp\capture.png"
            self.device.write(":MMEM:STOR:SCR '{}'".format(filepath))
            print("print taken")
            status = self.device.query('*OPC?')
            time.sleep(10)
            # image=r"C:\Users\Administrator\Documents\Keysight\Instrument\NR5G\screen\capture.png"
            filePathPc = f"{root_dir}\\{self.duplex_type}\\Results\\{self.test_case_name}\\EAXCID{self.eaxid}\\VXT_capture.png"
            ResultData = bytes(self.device.query_binary_values(f'MMEM:DATA? "{filepath}"', datatype='s'))
            newFile = open(filePathPc, "wb")
            newFile.write(ResultData)
            newFile.close()
            print("Constellation Saved")
            if power_evm_result[-1] != True:
                Error = f"{'*'*100}\nFail due to unexpected Power or EVM \nChannel Power : {power_evm_result[1]} \nEVM : {power_evm_result[0]}\n{'*'*100}"
                output_power = power_evm_result[1]
                captured_evm = power_evm_result[0]
                print(Error)
                return captured_evm, output_power, 'Fail', filePathPc, crc_data
            output_power = power_evm_result[1]
            captured_evm = power_evm_result[0]
            print(f"{'*'*100}\nChannel Power : {output_power}\nEVM : {captured_evm}\n{'*'*100}")
            return captured_evm, output_power, 'PASS', filePathPc, crc_data
        except Exception as e:
            Error = 'Capture_screenshot Error : {}'.format(e)
            print(Error)
            return Error

    def Constellation_check(self):
        if 'Comp' in self.test_case_name:
            scpi_cmds = self.compression_scpi
        else:
            scpi_cmds = self.base_extended
        Visa_status = self.visa_connection(self.vxt_add)
        if Visa_status:
            time.sleep(1)
            self.clear_status_reg_of_device()
            time.sleep(1)
            self.reset_device()
            time.sleep(1)
            # self.common_cmds.extend(scpi_cmds)
            if self.vxt_configuration(scpi_cmds):
                self.scpi_write(':SENS:POW:RANG:OPT IMM')
                time.sleep(3)
                return self.verify_result_and_capture_screenshot()
            else:
                return 'VXT Configuration are Failed'
        else:
            return Visa_status
    
    def RF_OFF(self,VXT_Add):
        scpi_cmds = [":OUTP OFF"]
        Visa_status = self.visa_connection(VXT_Add)
        if Visa_status:
            time.sleep(1)
            self.clear_status_reg_of_device()
            time.sleep(1)
            self.reset_device()
            time.sleep(1)
            self.common_cmds.extend(scpi_cmds)
            if self.vxt_configuration():
                return self.verify_result_and_capture_screenshot()
            else:
                return 'VXT Configuration are Failed'
        else:
            return Visa_status



    def verify_CRC(self):
        time.sleep(10)
        self.scpi_write(':MMEM:STOR:RES "{}"'.format(self.crc_file_name))
        data_list = []
        Error = ''
        for _ in range(10):
            try:
                filepath = "C:\\Users\\Administrator\\Documents\\Keysight\\Instrument\\NR5G\\data\\EVM\\results\\{}_CC0Bits.csv".format(self.crc_file_name.split('.')[0])
                ResultData = self.device.query(f':MMEM:DATA? "{filepath}"')
                status = self.device.query(':SYST:ERR?')
                # print(status)
                # if 'No error' in status:
                ResultData = ResultData.split('\n')
                for lines in ResultData:
                    lines = lines.split(',')
                    if len(lines) > 4:
                        data_list.append([lines[0],lines[1],lines[2],lines[3]])
                print("CRC Captured")
                return data_list
            except Exception as e:
                Error = 'Verify_CRC Error : {}'.format(e)
                status = self.device.query(':SYST:ERR?')
                print(status)
                print(Error)
        else:
            return Error


if __name__=="__main__":
    if len(sys.argv) > 2:
        DL_data = {}
        crc_data = {}
        eaxid = configur.get('INFO','eaxcid').split()
        Center_Freq = configur.get('INFO','DL_Center_Freq')
        bandwidth = configur.get('INFO','bandwidth')
        power_limit = configur.get('INFO','power_limit').split()
        evm_limit = configur.get('INFO','evm_limit')
        test_case_name = sys.argv[1]
        duplex_type = sys.argv[2]
        print(test_case_name)
        vxt_obj = vxt_configuration_and_result_capture(test_case_name,duplex_type)
        report_path = f"{root_dir}\\{duplex_type}\\Results\\{test_case_name}"
        for i in eaxid:
            Result = vxt_obj.Constellation_check()
            print(Result)
            # Visa_status = vxt_obj.visa_connection(vxt_obj.vxt_add)
            # crc_result = vxt_obj.verify_CRC()
            DL_data[i] = [i,Center_Freq,bandwidth,Result[0],
                                evm_limit,Result[1],power_limit[0],power_limit[1],Result[2]]
            if type(Result[-1]) == list:
                crc_data[i] = Result[-1]
        DL_data = {'1': ['1', '3.700005', '100', '2.01', '2.5', '22.24', '21.5', '25', 'c:\\ORAN_AUTOMATION\\CUPLANE\\TDD\\Results\\Base_DL_UL\\EAXCID1\\VXT_capture.png']}
        print(DL_data)
        print(crc_data)
        if type(DL_data) == dict:
             genrate_report(list(DL_data.values()),report_path,crc_data)
        # vxt_obj.visa_connection(vxt_obj.vxt_add)
        # vxt_obj.Check_EVM_power()
    else:
        print('Please run with below format\npython VXT_configuration_result_capture.py {test_case_name} {duplex_type}')