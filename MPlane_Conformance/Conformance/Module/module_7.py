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
import M_CTC_ID_018, M_CTC_ID_019, M_CTC_ID_020, M_CTC_ID_021, M_CTC_ID_022, M_CTC_ID_023


###############################################################################
## Initiate PDF
###############################################################################

def execution():
    Out1 = M_CTC_ID_018.test_m_ctc_id_018()
    time.sleep(10)
    Out2 = M_CTC_ID_019.test_m_ctc_id_019()
    time.sleep(10)
    Out3 = M_CTC_ID_020.test_m_ctc_id_020()
    time.sleep(10)
    Out4 = M_CTC_ID_021.test_m_ctc_id_021()
    time.sleep(10)
    Out5 = M_CTC_ID_022.test_m_ctc_id_022()
    time.sleep(10)
    Out6 = M_CTC_ID_023.test_m_ctc_id_023()
    flag1, flag2, flag3, flag4, flag5, flag6 = 'Fail', 'Fail', 'Fail', 'Fail', 'Fail', 'Fail'
    if Out1:
        flag1 = 'Pass'
    if Out2:
        flag2 = 'Pass'
    if Out3:
        flag3 = 'Pass'
    if Out4:
        flag4 = 'Pass'
    if Out5:
        flag5 = 'Pass'
    if Out6:
        flag6 = 'Pass'
    EVM_Header = ['Test Case', 'Verdict']
    print('\n\n')
    print('+'*100)
    print('\t\t\t Summary')
    print('+'*100)
    Result = [['Sudo on Hybrid M-plane Architecture (positive case)',flag1],['Access Control Sudo (negative case)',flag2],
            ['Access Control NMS (negative case)',flag3],['Access Control FM-PM (negative case)',flag4],
            ['Access Control SWM (negative case)',flag5],['Sudo on Hierarchical M-plane architecture (positive case)',flag6]]
    print(tabulate(Result, headers=EVM_Header,stralign='left',maxcolwidths=[50,20], tablefmt='fancy_grid'))


if __name__ == '__main__':
    execution()
    pass