###############################################################################
##@ FILE NAME:      M_CTC_ID_001
##@ TEST SCOPE:     M PLANE O-RAN CONFORMANCE \n
##@ Version:        V_1.0.0
##@ Support:        @Ramiyer, @VaibhavDhiman, @PriyaSharma
###############################################################################

###############################################################################
## Package Imports 
###############################################################################
import sys, os
from configparser import ConfigParser
from tabulate import tabulate


###############################################################################
## Directory Path
###############################################################################
dir_name = os.path.dirname(os.path.abspath(__file__))
parent = os.path.dirname((dir_name))
# print(parent)
sys.path.append(parent)

########################################################################
## For reading data from .ini file
########################################################################
configur = ConfigParser()
configur.read('{}/inputs.ini'.format(dir_name))

###############################################################################
## Related Imports
###############################################################################
import M_CTC_ID_014, M_CTC_ID_015, M_CTC_ID_016, M_CTC_ID_017


###############################################################################
## Initiate PDF
###############################################################################

def execution():
    Out1 = M_CTC_ID_015.test_m_ctc_id_015()
    Out2 = M_CTC_ID_014.test_m_ctc_id_014()
    Out3 = M_CTC_ID_016.test_m_ctc_id_016()
    Out4 = M_CTC_ID_017.test_m_ctc_id_017()
    flag1, flag2, flag3, flag4 = 'Fail', 'Fail', 'Fail', 'Fail'
    if Out1:
        flag1 = 'Pass'
    if Out2:
        flag2 = 'Pass'
    if Out3:
        flag3 = 'Pass'
    if Out4:
        flag4 = 'Pass'
    EVM_Header = ['Test Case', 'Verdict']
    print('\n\n')
    print('+'*100)
    print('\t\t\t Summary')
    print('+'*100)
    Result = [['O-RU Software Update (negative case)',flag1],['O-RU Software Update and Install',flag2],
            ['O-RU Software Activate without reset',flag3],['Supplemental Reset after Software Activation',flag4]]
    print(tabulate(Result, headers=EVM_Header,stralign='left',maxcolwidths=[50,20], tablefmt='fancy_grid'))


if __name__ == '__main__':
    execution()
    pass