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
configur.read('{}/inputs.ini'.format(dir_name))

###############################################################################
# Related Imports
###############################################################################
from Conformance import  M_CTC_ID_014, M_CTC_ID_016, M_CTC_ID_017

def select_testcase():
    li_executable_testCase = [False]*36
    TestCases = [
        ['O-RU Software Update and Install', 14],
        ['O-RU Software Activate without reset', 16],
        ['Supplemental Reset after Software Activation', 17]
    ]
    Header = ['Test Case', 'Test Case ID']
    print(tabulate(TestCases, headers=Header, stralign='left',
          maxcolwidths=[50, 20], tablefmt='fancy_grid'))


    ###############################################################################
    # Take User Inputs
    ###############################################################################
    user_input = [int(x) for x in input(
        'Enter space sperated test case: ').split()]
    print(user_input)
    
    
    verdict_table = []
    for selectCase in user_input:
        print('#'*100)
        print(f"\t\tExecuted test case is {selectCase}")
        print('#'*100)
        if selectCase == 14:
            result_014 = M_CTC_ID_014.test_m_ctc_id_014()
            if result_014:
                verdict_table.append(['O-RU Software Update and Install','Pass'])
            else:
                verdict_table.append(['O-RU Software Update and Install','Fail'])

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
        
        else:
            print(f'{selectCase} is not executable/ not present in table..')
    Header = ['Test Case', 'Verdict']
    print(tabulate(verdict_table, headers=Header, stralign='left',
          maxcolwidths=[50, 20], tablefmt='fancy_grid'))


if __name__ == '__main__':
    select_testcase()
