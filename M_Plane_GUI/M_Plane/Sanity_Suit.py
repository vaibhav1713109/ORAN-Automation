from M_Plane_Conf_04.M_Plane_Sanity import M_STC_ID_001, M_STC_ID_002, M_STC_ID_003, M_STC_ID_004, M_STC_ID_005, M_STC_ID_006
import time


def test_M_CTC_ID_001():
    # time.sleep(80)
    result_001 = M_STC_ID_001.test_MAIN_FUNC_001()
    if result_001 == True:
        return True
    else:
        raise Exception(result_001) from None
        

def test_M_CTC_ID_002():
    time.sleep(80)
    result_002 = M_STC_ID_002.test_MAIN_FUNC_002()
    if result_002 == True:
        return True
    else:
        raise Exception(result_002) from None

def test_M_CTC_ID_003():
    time.sleep(80)
    result_003 = M_STC_ID_003.test_MAIN_FUNC_003()
    if result_003 == True:
        return True
    else:
        raise Exception(result_003) from None





def test_M_CTC_ID_004():
    time.sleep(80)
    result_004 = M_STC_ID_004.test_MAIN_FUNC_004()
    if result_004 == True:
        return True
    else:
        raise Exception(result_004) from None


def test_M_CTC_ID_005():
    time.sleep(80)
    result_005 = M_STC_ID_005.test_MAIN_FUNC_005()
    if result_005 == True:
        return True
    else:
        raise Exception(result_005) from None

def test_M_CTC_ID_006():
    time.sleep(80)
    result_006 = M_STC_ID_006.test_MAIN_FUNC_006()
    if result_006 == True:
        return True
    else:
        raise Exception(result_006) from None




if __name__ == "__main__":
    pass