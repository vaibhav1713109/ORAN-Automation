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
import M_CTC_ID_001, M_CTC_ID_002, M_CTC_ID_003


###############################################################################
## Initiate PDF
###############################################################################

def execution():
    Out1 = M_CTC_ID_001.test_M_ctc_id_001()
    Out2 = M_CTC_ID_002.test_M_ctc_id_002()
    Out3 = M_CTC_ID_003.test_M_ctc_id_003()
    flag1, flag2, flag3 = 'Fail', 'Fail', 'Fail'
    if Out1:
        flag1 = 'Pass'
    if Out2:
        flag2 = 'Pass'
    Header = ['Test Case', 'Verdict']
    print('\n\n')
    print('+'*100)
    print('\t\t\t Summary')
    print('+'*100)
    Result = [['Transport and Handshake in IPv4 Environment (positive case)',flag1], 
        ['Transport and Handshake in IPv4 Environment (negative case: refuse SSH Connection)',flag2], 
        ['Transport and Handshake in IPv4 Environment (negative case: Invalid SSH credentials)',flag3]]
    print(tabulate(Result, headers=Header,stralign='left',maxcolwidths=[50,20], tablefmt='fancy_grid'))


if __name__ == '__main__':
    execution()
    pass
