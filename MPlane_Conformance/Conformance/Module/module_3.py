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
import M_CTC_ID_008, M_CTC_ID_009


###############################################################################
## Initiate PDF
###############################################################################

def execution():
    Out1 = M_CTC_ID_008.test_M_ctc_id_008()
    Out2 = M_CTC_ID_009.test_m_ctc_id_009()
    flag1, flag2 = 'Fail', 'Fail'
    if Out1:
        flag1 = 'Pass'
    if Out2:
        flag2 = 'Pass'
    EVM_Header = ['Test Case', 'Verdict']
    print('\n\n')
    print('+'*100)
    print('\t\t\t Summary')
    print('+'*100)
    Result = [['M-Plane Connection Supervision (positive case)',flag1],['M-Plane Connection Supervision (negative case)',flag2]]
    print(tabulate(Result, headers=EVM_Header,stralign='left',maxcolwidths=[50,20], tablefmt='fancy_grid'))


if __name__ == '__main__':
    execution()
    pass