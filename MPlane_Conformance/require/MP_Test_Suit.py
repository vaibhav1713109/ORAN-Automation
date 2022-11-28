###############################################################################
##@ FILE NAME:      M_CTC_ID_001
##@ TEST SCOPE:     M PLANE O-RAN CONFORMANCE \n
##@ Version:        V_1.0.0
##@ Support:        @Ramiyer, @VaibhavDhiman, @PriyaSharma
###############################################################################

###############################################################################
## Package Imports 
###############################################################################
import sys, os, time
from configparser import ConfigParser
from tabulate import tabulate


###############################################################################
## Directory Path
###############################################################################
dir_name = os.path.dirname(os.path.abspath(__file__))
parent = os.path.dirname((dir_name))
print(parent)
sys.path.append(parent)

########################################################################
## For reading data from .ini file
########################################################################
configur = ConfigParser()
configur.read('{}/inputs.ini'.format(dir_name))

###############################################################################
## Related Imports
###############################################################################
from Conformance import M_CTC_ID_001, M_CTC_ID_002, M_CTC_ID_003
from Conformance import M_CTC_ID_007, M_CTC_ID_008, M_CTC_ID_009,M_CTC_ID_019, M_CTC_ID_020
from Conformance import M_CTC_ID_010, M_CTC_ID_011, M_CTC_ID_013, M_CTC_ID_014, M_CTC_ID_015, M_CTC_ID_016, M_CTC_ID_017, M_CTC_ID_018
from Conformance import M_CTC_ID_021, M_CTC_ID_022, M_CTC_ID_023, M_CTC_ID_026, M_CTC_ID_027, M_CTC_ID_012



if __name__ == '__main__':
    # result_001 = M_CTC_ID_001.test_M_ctc_id_001()
    # time.sleep(15)
    # result_002 = M_CTC_ID_002.test_M_ctc_id_002()
    # time.sleep(15)
    # result_003 = M_CTC_ID_003.test_M_ctc_id_003()
    # time.sleep(15)
    result_007 = M_CTC_ID_007.test_m_ctc_id_007()
    time.sleep(15)
    # result_008 = M_CTC_ID_008.test_M_ctc_id_008()
    # time.sleep(60)
    # result_009 = M_CTC_ID_009.test_m_ctc_id_009()
    # time.sleep(15)
    # result_011 = M_CTC_ID_011.test_m_ctc_id_011()
    # time.sleep(15)
    result_012 = M_CTC_ID_012.test_m_ctc_id_012()
    time.sleep(15)
    result_013 = M_CTC_ID_013.test_m_ctc_id_013()
    time.sleep(15)
    # result_018 = M_CTC_ID_018.test_m_ctc_id_018()
    # time.sleep(15)
    # result_019 = M_CTC_ID_019.test_m_ctc_id_019()
    # time.sleep(15)
    # result_020 = M_CTC_ID_020.test_m_ctc_id_020()
    # time.sleep(15)
    # result_021 = M_CTC_ID_021.test_m_ctc_id_021()
    # time.sleep(15)
    # result_022 = M_CTC_ID_022.test_m_ctc_id_022()
    # time.sleep(15)
    # result_023 = M_CTC_ID_023.test_m_ctc_id_023()
    # time.sleep(15)
    # result_026 = M_CTC_ID_026.test_m_ctc_id_026()
    # time.sleep(15)
    # result_010 = M_CTC_ID_010.test_m_ctc_id_010()
    # time.sleep(15)
    # result_027 = M_CTC_ID_027.test_m_ctc_id_027()
    # time.sleep(15)
    # result_015 = M_CTC_ID_015.test_m_ctc_id_015()
    # time.sleep(15)
    result_014 = M_CTC_ID_014.test_m_ctc_id_014()
    time.sleep(15)
    result_016 = M_CTC_ID_016.test_m_ctc_id_016()
    time.sleep(15)
    result_017 = M_CTC_ID_017.test_m_ctc_id_017()
    Result = [
        # ['Transport and Handshake in IPv4 Environment (positive case)','Pass' if result_001 else 'Fail'], 
        # ['Transport and Handshake in IPv4 Environment (negative case: refuse SSH Connection)','Pass' if result_002 else 'Fail'], 
        # ['Transport and Handshake in IPv4 Environment (negative case: Invalid SSH credentials)','Pass' if result_003 else 'Fail'],
        ['Subscription to Notifications','Pass' if result_007 else 'Fail'], 
        # ['M-Plane Connection Supervision (positive case)','Pass' if result_008 else 'Fail'], 
        # ['M-Plane Connection Supervision (positive case)','Pass' if result_009 else 'Fail'], 
        # ['Retrieval without Filter Applied','Pass' if result_010 else 'Fail'], 
        # ['Retrieval with filter applied','Pass' if result_011 else 'Fail'], 
        ['O-RU Alarm Notification Generation','Pass' if result_012 else 'Fail'], 
        ['Retrieval of Active Alarm List','Pass' if result_013 else 'Fail'], 
        ['O-RU Software Update and Install','Pass' if result_014 else 'Fail'], 
        # ['O-RU Software Update (negative case)','Pass' if result_015 else 'Fail'], 
        ['O-RU Software Activate without reset','Pass' if result_016 else 'Fail'], 
        ['Supplemental Reset after Software Activation','Pass' if result_017 else 'Fail'], 
        # ['Sudo on Hybrid M-plane Architecture (positive case)','Pass' if result_018 else 'Fail'], 
        # ['Access Control Sudo (negative case)','Pass' if result_019 else 'Fail'], 
        # ['Access Control NMS (negative case)','Pass' if result_020 else 'Fail'],
        # ['Access Control FM-PM (negative case)','Pass' if result_021 else 'Fail'], 
        # ['Access Control SWM (negative case)','Pass' if result_022 else 'Fail'], 
        # ['Sudo on Hierarchical M-plane architecture (positive case)','Pass' if result_023 else 'Fail'], 
        # ['O-RU configurability test (positive case)','Pass' if result_026 else 'Fail'], 
        # ['O-RU Configurability Test (negative case)','Pass' if result_027 else 'Fail']
        ]
    Header = ['Test Case', 'Verdict']
    print(tabulate(Result, headers=Header,stralign='left',maxcolwidths=[50,20], tablefmt='fancy_grid'))



if __name__ == '__main__':
    pass