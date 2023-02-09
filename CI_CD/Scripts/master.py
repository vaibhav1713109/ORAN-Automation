import sys,os
import subprocess

dir_name = os.path.dirname(os.path.abspath(__file__))
overall_summary = []
overall_status = []

def generate_max_tc(tests,L):
    max_tc = {}
    for key in tests:
        level, plane, tc_number = key.split("_")
        if int(level[1]) == L:
            if plane == "M":
                m_count += 1
            elif plane == "S":
                s_count += 1
            else:
                cu_count +=1
        else:
            continue
    max_tc = {"M": m_count, "S": s_count, "CU": cu_count}
    return max_tc

def genrate_keys(tests,test_key):
    tc_count =0
    for key,val in tests.items():
        if key.startswith(test_key):
            tc_count+=1
    return tc_count
    
def parse_script(planes, levels, test_case_numbers):
    script_names = []
    tests = {"L1_M_1":"sw_update.py",
             "L1_S_1":"M_CTC_ID_018.py",
            #  "L1_M_3": "L1_M_3_script.py",
            #  "L1_M_4":"L1_M_4_script.py",
            #  "L1_S_1":"L1_S_1_script.py",
            #  "L1_S_2":"L1_S_2_script.py",
            #  "L1_S_3":"L1_S_3_script.py",
            #  "L1_CU_1":"L1_CU_1_script.py",
            #  "L1_CU_2":"L1_CU_2_script.py",
             "L2_M_1":"sw_update.py",
             "L2_S_1":"M_CTC_ID_018.py",
            #  "L2_M_3":"L2_M_3_script.py",
            #  "L2_M_4":"L2_M_4_script.py",
            #  "L2_M_5":"L2_M_5_script.py",
            #  "L2_S_1":"L2_S_1_script.py",
            #  "L2_S_2":"L2_S_2_script.py",
            #  "L2_S_3":"L2_S_3_script.py",
            #  "L2_S_4":"L2_S_4_script.py",
            #  "L2_S_5":"L2_S_5_script.py",
            #  "L2_S_6":"L2_S_6_script.py",
            #  "L2_CU_1":"L2_CU_1_script.py",
            #  "L2_CU_2":"L2_CU_2_script.py",
            #  "L2_CU_3":"L2_CU_3_script.py",
            #  "L3_M_1":"L3_M_1_script.py"
             } 

    if test_case_numbers:
        for level in levels:
            for plane in planes:
                for test_case_number in test_case_numbers:
                    Key_from_param = f"L{level}_{plane}_{test_case_number}"
                    if tests.get(Key_from_param):
                        script_names.append([Key_from_param,tests[Key_from_param]])
    else:
        for level in levels:
            for plane in planes: 
                test_key = f'L{level}_{plane}'
                max_tc = genrate_keys(tests=tests, test_key=test_key)        
                for key in range(1, max_tc+1):
                    Key_from_param = f"L{level}_{plane}_{key}"
                    if tests.get(Key_from_param):
                        script_names.append([Key_from_param,tests[Key_from_param]])
    return script_names

def execute_script(script_name):
    # script_name = '{}/{}'.format()
    Result = subprocess.getoutput("python {0}/{1}".format(dir_name,script_name))
    return Result
    
def check_and_generte_summary(Script_name,Result):
    print(Result)
    Result = Result.split('\n')
    Result = Result[-1]
    overall_status.append((Script_name,Result))
    pass



def main():
    
    plane = None
    level = None
    test_case_numbers = []
    if len(sys.argv) > 1:
        planes = sys.argv[1].split(",")
        if len(sys.argv) > 2:
            levels = list(map(int, sys.argv[2].split(",")))
            if len(sys.argv) > 3:
                test_case_numbers = list(map(int, sys.argv[3].split(",")))
        else:
            levels = [i for i in range(1, 5)]
    else:
        planes = ["M", "S", "CU"]
        levels = [i for i in range(1, 5)]
    script_names = parse_script(planes, levels, test_case_numbers)
    
    for script_name in script_names:
        Result = execute_script(script_name[1])
        # overall_summary.append(script_name.split('.')[0])
        check_and_generte_summary(''.join((script_name[0],script_name[1].split('.')[0])),Result)
    # print('*'*100)
    # print(overall_summary)
    print('*'*100)
    for data in overall_status:
        print(data[0],'\t\t=\t',data[1])

if __name__ == "__main__":
    main()