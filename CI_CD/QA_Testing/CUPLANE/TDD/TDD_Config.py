import sys
import os
import time
from configparser import ConfigParser
import subprocess
import shutil

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(root_dir)
configur = ConfigParser()
configur.read('{}/Requirement/inputs.ini'.format(root_dir))
sys.path.append(root_dir)
eaxids = configur.get('INFO','eaxcid').split()
print(eaxids)
from Scripts.scp_gen import *
from Scripts.scp_gen_prach import *
from Scripts.pcap_gen import *
from Scripts.pcap_gen_prach import *
from Scripts.pcap_load_play_recorde import *
from Scripts.VXT_configuration_result_capture import *
from Scripts.orb_gen import *
from Scripts.orb_gen_prach import *
from Scripts.vsa_constellation_and_result_capture import *
from Scripts.stop_player import *
from Scripts.genrate_report import *



def main(test_case_name,Duplex_Type):
    # python_path = 'C:/Users/Administrator/AppData/Local/Programs/Python/Python310/python.exe'
    python_path = 'python'
    DL_data = {}
    dl_crc_data = {}
    UL_data = {}
    ul_crc_data = {}
    eaxids = configur.get('INFO','eaxcid').split()
    eaxids = ['1','1']
    print(eaxids)
    Center_Freq = configur.get('INFO','DL_Center_Freq')
    bandwidth = configur.get('INFO','bandwidth')
    power_limit = configur.get('INFO','power_limit').split()
    evm_limit = configur.get('INFO','evm_limit')
    for eaxid in eaxids:
        try:
            if 'PRACH' not in test_case_name:
                print('{0}\n#{1}#\n{0}'.format('*'*100,'scp_gen.py'.center(98)))
                scp_gen_status = scp_genration(test_case_name=test_case_name,Duplex_Type= Duplex_Type,eAxID=eaxid)
                if scp_gen_status != True:
                    return scp_gen_status
                # process1 = subprocess.Popen([python_path,'{0}/ORS_Common_Scripts/scp_gen.py'.format(root_dir),test_case_name,Duplex_Type])
                # while process1.poll() is None:
                #     timeout = True
            else:
                print('{0}\n#{1}#\n{0}'.format('*'*100,'scp_gen_prach.py'.center(98)))
                scp_gen_status = scp_genration_prach(test_case_name=test_case_name,Duplex_Type= Duplex_Type, eAxID = eaxid)
                if scp_gen_status != True:
                    return scp_gen_status
                # process1 = subprocess.Popen([python_path,'{0}/ORS_Common_Scripts/scp_gen_prach.py'.format(root_dir),test_case_name,Duplex_Type])
                # while process1.poll() is None:
                #     timeout = True


            time.sleep(3)
            if 'PRACH' not in test_case_name:
                print('{0}\n#{1}#\n{0}'.format('*'*100,'pcap_gen.py'.center(98)))
                pcap_gen_status = ors_pcap_genration(test_case_name=test_case_name,duplex_type= Duplex_Type, eAxID = eaxid)
                if pcap_gen_status != True:
                    return pcap_gen_status
                # process2 = subprocess.Popen([python_path,'{0}/ORS_Common_Scripts/pcap_gen.py'.format(root_dir),test_case_name])
                # while process2.poll() is None:
                #     timeout = True
            else:
                print('{0}\n#{1}#\n{0}'.format('*'*100,'pcap_gen_prach.py'.center(98)))
                pcap_gen_status = ors_pcap_genration_prach(test_case_name=test_case_name,Duplex_Type= Duplex_Type,eAxID = eaxid)
                if pcap_gen_status != True:
                    return pcap_gen_status
                # process2 = subprocess.Popen([python_path,'{0}/ORS_Common_Scripts/pcap_gen_prach.py'.format(root_dir),test_case_name])
                # while process2.poll() is None:
                #     timeout = True


            time.sleep(3)
            print('{0}\n#{1}#\n{0}'.format('*'*100,'pcap_load_play_recorde.py'.center(98)))
            pcap_load_and_Play_gen_status = Pcap_Load_and_Data_play_record_(test_case_name=test_case_name,Duplex_Type= Duplex_Type,eAxID = eaxid)
            if pcap_load_and_Play_gen_status != True:
                    return pcap_load_and_Play_gen_status
            # process3 = subprocess.Popen([python_path,'{0}/ORS_Common_Scripts/pcap_load_play_recorde.py'.format(root_dir),test_case_name])
            # while process3.poll() is None:
            #     timeout = True


            time.sleep(3)
            if 'PRACH' not in test_case_name:
                print('{0}\n#{1}#\n{0}'.format('*'*100,'VXT_configuration_result_capture.py'.center(98)))
                vxt_configuration_obj = vxt_configuration_and_result_capture(test_case_name=test_case_name,duplex_type= Duplex_Type,eAxID = eaxid)
                vxt_configuration_status = vxt_configuration_obj.Constellation_check()
                # if vxt_configuration_status != True:
                #     return vxt_configuration_status
                print(vxt_configuration_status)
                DL_data[eaxid] = [eaxid,Center_Freq,bandwidth,vxt_configuration_status[0],
                                evm_limit,vxt_configuration_status[1],power_limit[0],power_limit[1],vxt_configuration_status[2],vxt_configuration_status[3]]
                if type(vxt_configuration_status[-1]) == list:
                    dl_crc_data[eaxid] = vxt_configuration_status[-1]

                # process4 = subprocess.Popen([python_path,'{0}/ORS_Common_Scripts/VXT_configuration_result_capture.py'.format(root_dir),test_case_name])
                # while process4.poll() is None:
                #     timeout = True



            time.sleep(3)
            print('{0}\n#{1}#\n{0}'.format('*'*100,'orb_gen.py'.center(98)))
            if 'PRACH' not in test_case_name:
                orb_gen_status = Generate_ORB(test_case_name=test_case_name,duplex_type= Duplex_Type,eAxID = eaxid)
                if orb_gen_status != True:
                        return orb_gen_status
                print(orb_gen_status)
            else:
                orb_gen_status = Generate_ORB_prach(test_case_name=test_case_name,duplex_type= Duplex_Type,eAxID = eaxid)
                if orb_gen_status != True:
                        return orb_gen_status
                print(orb_gen_status)
            # process7 = subprocess.Popen([python_path,'{0}/ORS_Common_Scripts/orb_gen.py'.format(root_dir),test_case_name])
            # while process7.poll() is None:
            #     timeout = True

            # input('Please check the constellation...')


            time.sleep(3)
            print('{0}\n#{1}#\n{0}'.format('*'*100,'vsa_constellation_and_result_capture.py'.center(98)))
            vsa_result_status = VSA_Function(test_case_name=test_case_name,duplex_type= Duplex_Type,eAxID = eaxid)
            # if vxt_result_status != True:
            #         return vxt_result_status
            UL_data[eaxid] = [eaxid,Center_Freq,bandwidth,vsa_result_status[0],
                                evm_limit,vsa_result_status[2],vsa_result_status[-1]]
            ul_crc_data[eaxid] = vsa_result_status[1]
            print(vsa_result_status)
            # process6 = subprocess.Popen([python_path,'{0}/ORS_Common_Scripts/vsa_constellation_and_result_capture.py'.format(root_dir),test_case_name])
            # while process6.poll() is None:
            #     timeout = True
            print(DL_data, UL_data, dl_crc_data, ul_crc_data)
        
        except Exception as e:
            print(f'TDD_Config Error : {e}')

        finally:
            time.sleep(3)
            print('{0}\n#{1}#\n{0}'.format('*'*100,'stop_player.py'.center(98)))
            stop_payer_status = Stop_Player()
            print(stop_payer_status)
            # input('Press Enter after changing channel... ')
            # process5 = subprocess.Popen([python_path,'{0}/ORS_Common_Scripts/stop_player.py'.format(root_dir),test_case_name])
            # while process5.poll() is None:
            #     timeout = True
    return DL_data, UL_data, dl_crc_data, ul_crc_data


if __name__ == "__main__":
    print(sys.argv)
    if len(sys.argv)>2:
        report_path = f"{root_dir}\\{sys.argv[2]}\\Results\\{sys.argv[1]}\\{sys.argv[1]}.pdf"
        input_file = f'{root_dir}\\{sys.argv[2]}\\Requirement\\inputs.ini'
        output_file = f'{root_dir}\\Requirement\\inputs.ini'
        input_file_status = os.path.exists(f'{root_dir}\\{sys.argv[2]}\\Requirement\\inputs.ini')
        if input_file_status:
            shutil.copyfile(input_file, output_file)
        sync_status = ''
        sync_status = input('Check wether RU is sync or not Y/N..')
        if sync_status != 'Y':
            Result = ORS_instrument_Configuration()
            if Result!= True:
                print('Instrument Configuration are failed...')
                sys.exit(1)
            input('Enter once sync')
        Result = main(sys.argv[1],sys.argv[2])
        print(Result)
        if type(Result) == tuple:
            genrate_report(list(Result[0].values()),report_path,Result[2],list(Result[1].values()),Result[3])
            pass
    else:
        print('Please run with below format\npython TDD_Config.py {test_case_name} {Duplex_Type Eg. TDD/FDD}')