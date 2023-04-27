import pyvisa as visa
import time,os,sys
from tabulate import tabulate
#from configparser import ConfigParser


root_dir = os.path.dirname(os.path.abspath(__file__))
print(root_dir)
#configur = ConfigParser()
#configur.read('{}/Requirement/inputs.ini'.format(root_dir))


class vxt_configuration_and_result_capture():
    def __init__(self) -> None:
        self.vxt_add = 'TCPIP::172.17.95.102::inst0::INSTR'
        #self.scp_path = r'C:\Users\Administrator\Music\lpru_scp\BASE_DL_UL.scp'
        self.scp_path = r'C:\Users\Administrator\Documents\power\dl_tc_260_2layer.scp'
        self.evm_limit = 5
        self.power_limit = [23,25]
        self.clgc_gain_calculation_time = 5
        self.state_file_name = f':MMEM:LOAD:STAT "{root_dir}/Base_DL_UL.state"'
        # self.basic_scpis = [
        #             ":INST:SEL NR5G", ":OUTP:STAT OFF", ":FEED:RF:PORT:INP RFIN",':CONF:EVM', ":DISP:EVM:VIEW NORM",
        #             ":INIT:CONT ON",f'''MMEMory:LOAD:EVM:SET ALL,"{self.scp_path}"''']
        # #self.filePathPc = f"/home/vvdn/Pictures/VXT_capture.png"
        self.filePathPc = f"/home/vvdn/Pictures/Meas_res_0001.csv"
        
        
    def visa_connection(self,vxt_add = None, gpib_id= None):
        try:
            if(vxt_add):
                self.rm = visa.ResourceManager()
                self.device = self.rm.open_resource(vxt_add)
                print(f'Connected to {self.device}')
                return 0
            elif(gpib_id):
                self.rm = visa.ResourceManager()
                self.device = self.rm.open_resource('GPIB0::{}::INSTR'.format(gpib_id)) 
                return 0       
            else:
                Error = 'Visa_connection Error: No valid instrument IP or GBIB ID given'
                print(Error)
                return 1
        except Exception as e:
            Error = f'Visa_connection Error : {e}'
            print(Error)
            return 1
        
    def clear_status_reg_of_device(self):
        self.device.write('*CLS')                                #Clear Status Register of device
        self.device.write('*WAI')                                #Wait till Clear command is complete

    def reset_device(self):
        self.device.write('*RST')                                #Reset the device
        self.device.write('*WAI')                                #Wait till Reset command is complete

    def scpi_write(self, cmnd):
        self.device.write(cmnd)
        time.sleep(1) # Wait for 1 second to ensure completion of the SCPI command
        status = self.device.query("*OPC?")
        if int(status) != 1: # Check for any error during the execution of SCPI command
            return 1
        else:
            return 0

    def fetch_EVM_power(self):
        Error = ''
        captured_evm = 0
        output_power = 0
        time.sleep(2)
        try:
            self.device.timeout = 5000
            CMD = ':FETCh:EVM000001?'
            Res = self.device.query_ascii_values(CMD)
            #time.sleep(1)
            print(Res)
            captured_evm = "{:.2f}".format(float(Res[1]))
            output_power = "{:.2f}".format(float(Res[0]))
        except Exception as e:
            Error = self.device.write("SYST:ERR?")
            #Error = 'fetch_EVM_power Error : {}'.format(e))
            print(Error)
            return Error,100
        if float(captured_evm) < float(self.evm_limit) and (float(output_power) > float(self.power_limit[0]) and float(output_power) < float(self.power_limit[1])):
            return captured_evm,output_power, 0
        else:
            return captured_evm,output_power, 1 

    def vxt_configuration(self,scpi_cmds):
        for scpi in scpi_cmds:
            if not self.scpi_write(scpi):
                continue
            else:
                return 1
        return 0
    
    def verify_result_and_capture_screenshot(self):
        try:
            # power_result = self.Check_Power()
            power_evm_result = self.fetch_EVM_power()
            #filepath = r"C:\temp\capture.png"
            filepath = r"C:\Users\Administrator\Documents\capture.png"
            self.device.write(":MMEM:STOR:SCR '{}'".format(filepath))
            print("print taken")
            status = self.device.query('*OPC?')
            time.sleep(10)
            # image=r"C:\Users\Administrator\Documents\Keysight\Instrument\NR5G\screen\capture.png"
            ResultData = bytes(self.device.query_binary_values(f'MMEM:DATA? "{filepath}"', datatype='s'))
            newFile = open(self.filePathPc, "wb")
            newFile.write(ResultData)
            newFile.close()
            print("Constellation Saved")
            # print(power_evm_result)
            if power_evm_result[-1] != 0:
                Error = f'Fail due to unexpected Power/EVM : {power_evm_result[1]} or EVM : {power_evm_result[0]}'
                print(Error)
                return 1
            print(f'{0}\nChannel Power : {power_evm_result[1]}\nEVM : {power_evm_result[0]}\n{0}'.format('*'*100))
            return 0
        except Exception as e:
            Error = 'Capture_screenshot Error : {}'.format(e)
            print(Error)
            return 100
    
    def verify_CRC(self):
        try:
            crc_pass = crc_fail = 0
            data_list = []
            filepath = r"C:\Users\Administrator\Documents\MeasR_1_CC0Bits.csv"
            ResultData = self.device.query(f':MMEM:DATA? "{filepath}"')
            ResultData = ResultData.split('\n')
            Header = ['Channel', 'Slot', 'CRC Passed', 'Bit Length']
            for lines in ResultData:
                lines = lines.split(',')
                if len(lines) > 4:
                    data_list.append([lines[0],lines[1],lines[2],lines[3]])
                    if lines[2] == 'True':
                        crc_pass+=1
                    elif lines[2] == 'False':
                        crc_fail+=1
            print("CRC Captured")
            Data = data_list[1:]
            ACT_RES = tabulate(Data,Header,tablefmt='fancy_grid')
            print(ACT_RES)
            print('*'*100)
            print(f'CRC Pass = {crc_pass}\nCRC Fail = {crc_fail}')
            print('*'*100)
            return data_list
        except Exception as e:
            Error = 'Verify_CRC Error : {}'.format(e)
            print(Error)
            return 100
        pass

    def Constellation_check(self):
        Visa_status = self.visa_connection(self.vxt_add)
        if not Visa_status:
            time.sleep(1)
            self.clear_status_reg_of_device()
            time.sleep(1)
            self.reset_device()
            time.sleep(2)
            # self.common_cmds.extend(scpi_cmds)
            if not self.scpi_write(self.state_file_name):
                time.sleep(3)
                status = self.verify_result_and_capture_screenshot()
                return status 
            else:
                print("VXT Configuration are Failed") 
                return 1
        else:
            return Visa_status
        
    def disconnect_from_VXT(self):
        try:
            self.device.close()
            self.rm.close()
            print("Disconnected from the VXT!")
        except Exception as e:
            Error = 'Capture_screenshot Error : {}'.format(e)
            print(Error)
            return 100

if __name__=="__main__":
    vxt_obj = vxt_configuration_and_result_capture()
    vxt_obj.visa_connection(vxt_obj.vxt_add)
    vxt_obj.verify_CRC()
    # vxt_obj.verify_result_and_capture_screenshot()
    # if not vxt_obj.Constellation_check():
    #     print("PASS")
    # else:
    #     print("FAIL")
    vxt_obj.disconnect_from_VXT()

