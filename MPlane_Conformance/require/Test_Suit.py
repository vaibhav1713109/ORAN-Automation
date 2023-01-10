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



def test_M_CTC_ID_001():
    result_001 = M_CTC_ID_001.test_M_ctc_id_001()
    if result_001 == True:
        pass
    else:
        raise Exception(result_001) from None


def test_M_CTC_ID_002():
    time.sleep(15)
    result_002 = M_CTC_ID_002.test_M_ctc_id_002()
    if result_002 == True:
        pass
    else:
        raise Exception(result_002) from None
    

def test_M_CTC_ID_003():
    time.sleep(15)
    result_003 = M_CTC_ID_003.test_M_ctc_id_003()
    if result_003[0] == True:
        # DHCP_CONF_BASE.test_call()
        # xml_data3 = '''<reset xmlns="urn:o-ran:operations:1.0"></reset>'''
        # d3 = result_003[1].dispatch(to_ele(xml_data3))
        # time.sleep(40)
        pass
    else:
        raise Exception(result_003) from None




# # def test_M_CTC_ID_007():
# #     time.sleep(80)
# #     result_007 = M_CTC_ID_007.test_m_ctc_id_007()
# #     if result_007 == True:
# #         pass
# #     else:
# #         raise Exception(result_007) from None
        

def test_M_CTC_ID_008():
    time.sleep(15)
    result_008 = M_CTC_ID_008.test_M_ctc_id_008()
    if result_008 == True:
        pass
    else:
        raise Exception(result_008) from None

def test_M_CTC_ID_009():
    time.sleep(60)
    result_009 = M_CTC_ID_009.test_m_ctc_id_009()
    if result_009 == True:
        pass
    else:
        raise Exception(result_009) from None





def test_M_CTC_ID_011():
    time.sleep(15)
    result_011 = M_CTC_ID_011.test_m_ctc_id_011()
    if result_011 == True:
        pass
    else:
        raise Exception(result_011) from None


# # def test_M_CTC_ID_012():
#     # time.sleep(15)
# #     result_012 = M_CTC_ID_012.test_m_ctc_id_012()
# #     if result_012 == True:
# #         pass
# #     else:
# #         raise Exception(result_012) from None

# # def test_M_CTC_ID_013():
#     # time.sleep(15)
# #     result_013 = M_CTC_ID_013.test_m_ctc_id_013()
# #     if result_013 == True:
# #         pass
# #     else:
# #         raise Exception(result_013) from None




def test_M_CTC_ID_018():
    time.sleep(15)
    result_018 = M_CTC_ID_018.test_m_ctc_id_018()
    if result_018 == True:
        pass
    else:
        raise Exception(result_018) from None


def test_M_CTC_ID_019():
    time.sleep(15)
    result_019 = M_CTC_ID_019.test_m_ctc_id_019()
    if result_019 == True:
        pass
    else:
        raise Exception(result_019) from None


def test_M_CTC_ID_020():
    time.sleep(15)
    result_020 = M_CTC_ID_020.test_m_ctc_id_020()
    if result_020 == True:
        pass
    else:
        raise Exception(result_020) from None


def test_M_CTC_ID_021():
    time.sleep(15)
    result_021 = M_CTC_ID_021.test_m_ctc_id_021()
    if result_021 == True:
        pass
    else:
        raise Exception(result_021) from None


def test_M_CTC_ID_022():
    time.sleep(15)
    result_022 = M_CTC_ID_022.test_m_ctc_id_022()
    if result_022 == True:
        pass
    else:
        raise Exception(result_022) from None


def test_M_CTC_ID_023():
    time.sleep(15)
    result_023 = M_CTC_ID_023.test_m_ctc_id_023()
    if result_023 == True:
        pass
    else:
        raise Exception(result_023) from None


def test_M_CTC_ID_026():
    time.sleep(15)
    result_026 = M_CTC_ID_026.test_m_ctc_id_026()
    if result_026 == True:
        pass
    else:
        raise Exception(result_026) from None

def test_M_CTC_ID_010():
    time.sleep(15)
    result_010 = M_CTC_ID_010.test_m_ctc_id_010()
    if result_010 == True:
        pass
    else:
        raise Exception(result_010) from None

def test_M_CTC_ID_027():
    time.sleep(15)
    result_027 = M_CTC_ID_027.test_m_ctc_id_027()
    if result_027 == True:
        pass
    else:
        raise Exception(result_027) from None

def test_M_CTC_ID_015():
    time.sleep(15)
    result_015 = M_CTC_ID_015.test_m_ctc_id_015()
    if result_015 == True:
        pass
    else:
        raise Exception(result_015) from None        

# def test_M_CTC_ID_014():
#     time.sleep(15)
#     result_014 = M_CTC_ID_014.test_m_ctc_id_014()
#     if result_014 == True:
#         pass
#     else:
#         raise Exception(result_014) from None



# def test_M_CTC_ID_016():
#     time.sleep(15)
#     result_016 = M_CTC_ID_016.test_m_ctc_id_016()
#     if result_016 == True:
#         pass
#     else:
#         raise Exception(result_016) from None


# def test_M_CTC_ID_017():
#     time.sleep(15)
#     result_017 = M_CTC_ID_017.test_m_ctc_id_017()
#     if result_017 == True:
#         pass
#     else:
#         raise Exception(result_017) from None

if __name__ == '__main__':
    pass