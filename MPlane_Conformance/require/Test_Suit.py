###############################################################################
# @ FILE NAME:      M Plane Test Suit
# @ TEST SCOPE:     M PLANE O-RAN CONFORMANCE \n
# @ Version:        V_1.0.0
# @ Support:        @Ramiyer, @VaibhavDhiman, @PriyaSharma
###############################################################################

###############################################################################
# Package Imports
###############################################################################
import sys
import os
import time
from configparser import ConfigParser
from tabulate import tabulate


###############################################################################
# Directory Path
###############################################################################
dir_name = os.path.dirname(os.path.abspath(__file__))
parent = os.path.dirname((dir_name))
print(parent)
sys.path.append(parent)

########################################################################
# For reading data from .ini file
########################################################################
configur = ConfigParser()
configur.read('{}/Conformance/inputs.ini'.format(parent))

###############################################################################
# Related Imports
###############################################################################
from Conformance import M_CTC_ID_001, M_CTC_ID_002, M_CTC_ID_003
from Conformance import M_CTC_ID_007, M_CTC_ID_008, M_CTC_ID_009,M_CTC_ID_019, M_CTC_ID_020
from Conformance import M_CTC_ID_010, M_CTC_ID_011, M_CTC_ID_013, M_CTC_ID_015, M_CTC_ID_018
from Conformance import M_CTC_ID_021, M_CTC_ID_022, M_CTC_ID_023, M_CTC_ID_026, M_CTC_ID_027, M_CTC_ID_012
from Conformance import  M_CTC_ID_014, M_CTC_ID_016, M_CTC_ID_017

def select_testcase():
    TestCases = [
        ['Transport and Handshake in IPv4 Environment (positive case)', 1],
        ['Transport and Handshake in IPv4 Environment (negative case: refuse SSH Connection)', 2],
        ['Transport and Handshake in IPv4 Environment (negative case: Invalid SSH credentials)', 3],
        ['Subscription to Notifications', 7],
        ['M-Plane Connection Supervision (positive case)', 8],
        ['M-Plane Connection Supervision (negative case)', 9],
        ['Retrieval without Filter Applied', 10],
        ['Retrieval with filter applied', 11],
        ['O-RU Alarm Notification Generation', 12],
        ['Retrieval of Active Alarm List', 13],
        ['O-RU Software Update and Install', 14],
        ['O-RU Software Update (negative case)', 15],
        ['O-RU Software Activate without reset', 16],
        ['Supplemental Reset after Software Activation', 17],
        ['Sudo on Hybrid M-plane Architecture (positive case)', 18],
        ['Access Control Sudo (negative case)', 19],
        ['Access Control NMS (negative case)', 20],
        ['Access Control FM-PM (negative case)', 21],
        ['Access Control SWM (negative case)', 22],
        ['Sudo on Hierarchical M-plane architecture (positive case)', 23],
        ['O-RU configurability test (positive case)', 26],
        ['O-RU Configurability Test (negative case)', 27]
    ]
    Header = ['Test Case', 'Test Case ID']
    print(tabulate(TestCases, headers=Header, stralign='left',
          maxcolwidths=[50, 20], tablefmt='fancy_grid'))


    ###############################################################################
    # Take User Inputs
    ###############################################################################
    # user_input = [int(x) for x in input(
    #     'Enter space sperated test case: ').split()]
    user_input = configur.get('INFO','selected_test_case').split()
    print(user_input)
    
    
    verdict_table = []
    for selectCase in user_input:
        print('#'*100)
        print(f'\t\tExecuted test case is {selectCase}')
        print('#'*100)
        selectCase = int(selectCase)
        if selectCase == 1:
            result_001 = M_CTC_ID_001.test_M_ctc_id_001()
            if result_001:
                verdict_table.append(['Transport and Handshake in IPv4 Environment (positive case)','Pass'])
            else:
                verdict_table.append(['Transport and Handshake in IPv4 Environment (positive case)','Fail'])

        elif selectCase == 2:
            result_002 = M_CTC_ID_002.test_M_ctc_id_002()
            if result_002:
                verdict_table.append(['Transport and Handshake in IPv4 Environment (negative case: refuse SSH Connection)','Pass'])
            else:
                verdict_table.append(['Transport and Handshake in IPv4 Environment (negative case: refuse SSH Connection)','Fail'])

        elif selectCase == 3:
            result_003 = M_CTC_ID_003.test_M_ctc_id_003()
            if result_003:
                verdict_table.append(['Transport and Handshake in IPv4 Environment (negative case: Invalid SSH credentials)','Pass'])
            else:
                verdict_table.append(['Transport and Handshake in IPv4 Environment (negative case: Invalid SSH credentials)','Fail'])

        elif selectCase == 7:
            result_007 = M_CTC_ID_007.test_m_ctc_id_007()
            if result_007:
                verdict_table.append(['Subscription to Notifications','Pass'])
            else:
                verdict_table.append(['Subscription to Notifications','Fail'])

        elif selectCase == 8:
            result_008 = M_CTC_ID_008.test_M_ctc_id_008()
            if result_008:
                verdict_table.append(['M-Plane Connection Supervision (positive case)','Pass'])
            else:
                verdict_table.append(['M-Plane Connection Supervision (positive case)','Fail'])

        elif selectCase == 9:
            result_009 = M_CTC_ID_009.test_m_ctc_id_009()
            if result_009:
                verdict_table.append(['M-Plane Connection Supervision (negative case)','Pass'])
            else:
                verdict_table.append(['M-Plane Connection Supervision (negative case)','Fail'])

        elif selectCase == 10:
            result_010 = M_CTC_ID_010.test_m_ctc_id_010()
            if result_010:
                verdict_table.append(['Retrieval without Filter Applied','Pass'])
            else:
                verdict_table.append(['Retrieval without Filter Applied','Fail'])

        elif selectCase == 11:
            result_011 = M_CTC_ID_011.test_m_ctc_id_011()
            if result_011:
                verdict_table.append(['Retrieval with Filter Applied','Pass'])
            else:
                verdict_table.append(['Retrieval with Filter Applied','Fail'])

        elif selectCase == 12:
            result_012 = M_CTC_ID_012.test_m_ctc_id_012()
            if result_012:
                verdict_table.append(['O-RU Alarm Notification Generation','Pass'])
            else:
                verdict_table.append(['O-RU Alarm Notification Generation','Fail'])
        
        elif selectCase == 13:
            result_013 = M_CTC_ID_013.test_m_ctc_id_013()
            if result_013:
                verdict_table.append(['Retrieval of Active Alarm List','Pass'])
            else:
                verdict_table.append(['Retrieval of Active Alarm List','Fail'])
        
        if selectCase == 14:
            result_014 = M_CTC_ID_014.test_m_ctc_id_014()
            if result_014:
                verdict_table.append(['O-RU Software Update and Install','Pass'])
            else:
                verdict_table.append(['O-RU Software Update and Install','Fail'])

        elif selectCase == 15:
            result_015 = M_CTC_ID_015.test_m_ctc_id_015()
            if result_015:
                verdict_table.append(['O-RU Software Update (negative case)','Pass'])
            else:
                verdict_table.append(['O-RU Software Update (negative case)','Fail'])

        elif selectCase == 16:
            result_016 = M_CTC_ID_016.test_m_ctc_id_016()
            if result_016:
                verdict_table.append(['O-RU Software Activate without reset','Pass'])
            else:
                verdict_table.append(['O-RU Software Activate without reset','Fail'])

        elif selectCase == 17:
            result_017 = M_CTC_ID_017.test_m_ctc_id_017()
            if result_017:
                verdict_table.append(['Supplemental Reset after Software Activation','Pass'])
            else:
                verdict_table.append(['Supplemental Reset after Software Activation','Fail'])
        
        
        elif selectCase == 18:
            result_018 = M_CTC_ID_018.test_m_ctc_id_018()
            if result_018:
                verdict_table.append(['Sudo on Hybrid M-plane Architecture (positive case)','Pass'])
            else:
                verdict_table.append(['Sudo on Hybrid M-plane Architecture (positive case)','Fail'])

        elif selectCase == 19:
            result_019 = M_CTC_ID_019.test_m_ctc_id_019()
            if result_019:
                verdict_table.append(['Access Control Sudo (negative case)','Pass'])
            else:
                verdict_table.append(['Access Control Sudo (negative case)','Fail'])

        elif selectCase == 20:
            result_020 = M_CTC_ID_020.test_m_ctc_id_020()
            if result_020:
                verdict_table.append(['Access Control NMS (negative case)','Pass'])
            else:
                verdict_table.append(['Access Control NMS (negative case)','Fail'])

        elif selectCase == 21:
            result_021 = M_CTC_ID_021.test_m_ctc_id_021()
            if result_021:
                verdict_table.append(['Access Control FM-PM (negative case)','Pass'])
            else:
                verdict_table.append(['Access Control FM-PM (negative case)','Fail'])

        elif selectCase == 22:
            result_022 = M_CTC_ID_022.test_m_ctc_id_022()
            if result_022:
                verdict_table.append(['Access Control SWM (negative case)','Pass'])
            else:
                verdict_table.append(['Access Control SWM (negative case)','Fail'])

        elif selectCase == 23:
            result_023 = M_CTC_ID_023.test_m_ctc_id_023()
            if result_023:
                verdict_table.append(['Sudo on Hierarchical M-plane architecture (positive case)','Pass'])
            else:
                verdict_table.append(['Sudo on Hierarchical M-plane architecture (positive case)','Fail'])

        elif selectCase == 26:
            result_026 = M_CTC_ID_026.test_m_ctc_id_026()
            if result_026:
                verdict_table.append(['O-RU configurability test (positive case)','Pass'])
            else:
                verdict_table.append(['O-RU configurability test (positive case)','Fail'])

        elif selectCase == 27:
            result_027 = M_CTC_ID_027.test_m_ctc_id_027()
            if result_027:
                verdict_table.append(['O-RU configurability test (negative case)','Pass'])
            else:
                verdict_table.append(['O-RU configurability test (negative case)','Fail'])

        else:
            print(f'{selectCase} is not executable/ not present in table..')
    Header = ['Test Case', 'Verdict']
    print(tabulate(verdict_table, headers=Header, stralign='left',
          maxcolwidths=[50, 20], tablefmt='fancy_grid'))


if __name__ == '__main__':
    select_testcase()