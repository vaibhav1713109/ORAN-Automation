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
from math import *
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
    user_input = list(map(int,configur.get('INFO','selected_test_case').split()))
    print(f'Selected Test Cases are : {user_input}')
    
    Header = ['Test Case', 'Test Case ID', 'Execution Time']
    verdict_table = []

    st = time.time()
    for selectCase in user_input:
        print('#'*100)
        print(f'\t\tExecuted test case is {selectCase}')
        print('#'*100)
        selectCase = int(selectCase)
        if selectCase == 1:
            start_time = time.time()
            result_001 = M_CTC_ID_001.test_M_ctc_id_001()
            end_time = time.time()
            total_time = '{:.2f}'.format(end_time-start_time)
            if result_001:
                verdict_table.append(['Transport and Handshake in IPv4 Environment (positive case)','Pass',str(total_time)])
            else:
                verdict_table.append(['Transport and Handshake in IPv4 Environment (positive case)','Fail', str(total_time)])

        elif selectCase == 2:
            start_time = time.time()
            result_002 = M_CTC_ID_002.test_M_ctc_id_002()
            end_time = time.time()
            total_time = '{:.2f}'.format(end_time-start_time)
            if result_002:
                verdict_table.append(['Transport and Handshake in IPv4 Environment (negative case: refuse SSH Connection)','Pass',str(total_time)])
            else:
                verdict_table.append(['Transport and Handshake in IPv4 Environment (negative case: refuse SSH Connection)','Fail',str(total_time)])

        elif selectCase == 3:
            start_time = time.time()
            result_003 = M_CTC_ID_003.test_M_ctc_id_003()
            end_time = time.time()
            total_time = '{:.2f}'.format(end_time-start_time)
            if result_003:
                verdict_table.append(['Transport and Handshake in IPv4 Environment (negative case: Invalid SSH credentials)','Pass',str(total_time)])
            else:
                verdict_table.append(['Transport and Handshake in IPv4 Environment (negative case: Invalid SSH credentials)','Fail',str(total_time)])

        elif selectCase == 7:
            start_time = time.time()
            result_007 = M_CTC_ID_007.test_m_ctc_id_007()
            end_time = time.time()
            total_time = '{:.2f}'.format(end_time-start_time)
            if result_007:
                verdict_table.append(['Subscription to Notifications','Pass',str(total_time)])
            else:
                verdict_table.append(['Subscription to Notifications','Fail',str(total_time)])

        elif selectCase == 8:
            start_time = time.time()
            result_008 = M_CTC_ID_008.test_M_ctc_id_008()
            end_time = time.time()
            total_time = '{:.2f}'.format(end_time-start_time)
            if result_008:
                verdict_table.append(['M-Plane Connection Supervision (positive case)','Pass',str(total_time)])
            else:
                verdict_table.append(['M-Plane Connection Supervision (positive case)','Fail',str(total_time)])

        elif selectCase == 9:
            start_time = time.time()
            result_009 = M_CTC_ID_009.test_m_ctc_id_009()
            end_time = time.time()
            total_time = '{:.2f}'.format(end_time-start_time)
            if result_009:
                verdict_table.append(['M-Plane Connection Supervision (negative case)','Pass',str(total_time)])
            else:
                verdict_table.append(['M-Plane Connection Supervision (negative case)','Fail',str(total_time)])

        elif selectCase == 10:
            start_time = time.time()
            result_010 = M_CTC_ID_010.test_m_ctc_id_010()
            end_time = time.time()
            total_time = '{:.2f}'.format(end_time-start_time)
            if result_010:
                verdict_table.append(['Retrieval without Filter Applied','Pass',str(total_time)])
            else:
                verdict_table.append(['Retrieval without Filter Applied','Fail',str(total_time)])

        elif selectCase == 11:
            start_time = time.time()
            result_011 = M_CTC_ID_011.test_m_ctc_id_011()
            end_time = time.time()
            total_time = '{:.2f}'.format(end_time-start_time)
            if result_011:
                verdict_table.append(['Retrieval with Filter Applied','Pass',str(total_time)])
            else:
                verdict_table.append(['Retrieval with Filter Applied','Fail',str(total_time)])

        elif selectCase == 12:
            start_time = time.time()
            result_012 = M_CTC_ID_012.test_m_ctc_id_012()
            end_time = time.time()
            total_time = '{:.2f}'.format(end_time-start_time)
            if result_012:
                verdict_table.append(['O-RU Alarm Notification Generation','Pass',str(total_time)])
            else:
                verdict_table.append(['O-RU Alarm Notification Generation','Fail',str(total_time)])
        
        elif selectCase == 13:
            start_time = time.time()
            result_013 = M_CTC_ID_013.test_m_ctc_id_013()
            end_time = time.time()
            total_time = '{:.2f}'.format(end_time-start_time)
            if result_013:
                verdict_table.append(['Retrieval of Active Alarm List','Pass',str(total_time)])
            else:
                verdict_table.append(['Retrieval of Active Alarm List','Fail',str(total_time)])
        
        if selectCase == 14:
            start_time = time.time()
            result_014 = M_CTC_ID_014.test_m_ctc_id_014()
            end_time = time.time()
            total_time = '{:.2f}'.format(end_time-start_time)
            if result_014:
                verdict_table.append(['O-RU Software Update and Install','Pass',str(total_time)])
            else:
                verdict_table.append(['O-RU Software Update and Install','Fail',str(total_time)])

        elif selectCase == 15:
            start_time = time.time()
            result_015 = M_CTC_ID_015.test_m_ctc_id_015()
            end_time = time.time()
            total_time = '{:.2f}'.format(end_time-start_time)
            if result_015:
                verdict_table.append(['O-RU Software Update (negative case)','Pass',str(total_time)])
            else:
                verdict_table.append(['O-RU Software Update (negative case)','Fail',str(total_time)])

        elif selectCase == 16:
            start_time = time.time()
            result_016 = M_CTC_ID_016.test_m_ctc_id_016()
            end_time = time.time()
            total_time = '{:.2f}'.format(end_time-start_time)
            if result_016:
                verdict_table.append(['O-RU Software Activate without reset','Pass',str(total_time)])
            else:
                verdict_table.append(['O-RU Software Activate without reset','Fail',str(total_time)])

        elif selectCase == 17:
            start_time = time.time()
            result_017 = M_CTC_ID_017.test_m_ctc_id_017()
            end_time = time.time()
            total_time = '{:.2f}'.format(end_time-start_time)
            if result_017:
                verdict_table.append(['Supplemental Reset after Software Activation','Pass',str(total_time)])
            else:
                verdict_table.append(['Supplemental Reset after Software Activation','Fail',str(total_time)])
        
        
        elif selectCase == 18:
            start_time = time.time()
            result_018 = M_CTC_ID_018.test_m_ctc_id_018()
            end_time = time.time()
            total_time = '{:.2f}'.format(end_time-start_time)
            if result_018:
                verdict_table.append(['Sudo on Hybrid M-plane Architecture (positive case)','Pass',str(total_time)])
            else:
                verdict_table.append(['Sudo on Hybrid M-plane Architecture (positive case)','Fail',str(total_time)])

        elif selectCase == 19:
            start_time = time.time()
            result_019 = M_CTC_ID_019.test_m_ctc_id_019()
            end_time = time.time()
            total_time = '{:.2f}'.format(end_time-start_time)
            if result_019:
                verdict_table.append(['Access Control Sudo (negative case)','Pass',str(total_time)])
            else:
                verdict_table.append(['Access Control Sudo (negative case)','Fail',str(total_time)])

        elif selectCase == 20:
            start_time = time.time()
            result_020 = M_CTC_ID_020.test_m_ctc_id_020()
            end_time = time.time()
            total_time = '{:.2f}'.format(end_time-start_time)
            if result_020:
                verdict_table.append(['Access Control NMS (negative case)','Pass',str(total_time)])
            else:
                verdict_table.append(['Access Control NMS (negative case)','Fail',str(total_time)])

        elif selectCase == 21:
            start_time = time.time()
            result_021 = M_CTC_ID_021.test_m_ctc_id_021()
            end_time = time.time()
            total_time = '{:.2f}'.format(end_time-start_time)
            if result_021:
                verdict_table.append(['Access Control FM-PM (negative case)','Pass',str(total_time)])
            else:
                verdict_table.append(['Access Control FM-PM (negative case)','Fail',str(total_time)])

        elif selectCase == 22:
            start_time = time.time()
            result_022 = M_CTC_ID_022.test_m_ctc_id_022()
            end_time = time.time()
            total_time = '{:.2f}'.format(end_time-start_time)
            if result_022:
                verdict_table.append(['Access Control SWM (negative case)','Pass',str(total_time)])
            else:
                verdict_table.append(['Access Control SWM (negative case)','Fail',str(total_time)])

        elif selectCase == 23:
            start_time = time.time()
            result_023 = M_CTC_ID_023.test_m_ctc_id_023()
            end_time = time.time()
            total_time = '{:.2f}'.format(end_time-start_time)
            if result_023:
                verdict_table.append(['Sudo on Hierarchical M-plane architecture (positive case)','Pass',str(total_time)])
            else:
                verdict_table.append(['Sudo on Hierarchical M-plane architecture (positive case)','Fail',str(total_time)])

        elif selectCase == 26:
            start_time = time.time()
            result_026 = M_CTC_ID_026.test_m_ctc_id_026()
            end_time = time.time()
            total_time = '{:.2f}'.format(end_time-start_time)
            if result_026:
                verdict_table.append(['O-RU configurability test (positive case)','Pass',str(total_time)])
            else:
                verdict_table.append(['O-RU configurability test (positive case)','Fail',str(total_time)])

        elif selectCase == 27:
            start_time = time.time()
            result_027 = M_CTC_ID_027.test_m_ctc_id_027()
            end_time = time.time()
            total_time = '{:.2f}'.format(end_time-start_time)
            if result_027:
                verdict_table.append(['O-RU configurability test (negative case)','Pass',str(total_time)])
            else:
                verdict_table.append(['O-RU configurability test (negative case)','Fail',str(total_time)])
        else:
            print(f'{selectCase} is not executable/ not present in table..')
    en = time.time()
    print('Total Excecution Time : {:.2f} sec.'.format(en-st) )


if __name__ == '__main__':
    select_testcase()