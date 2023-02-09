###############################################################################
# Package Imports
###############################################################################
import sys
import os
import subprocess, json

###############################################################################
# Directory Path
###############################################################################
dir_name = os.path.dirname(os.path.abspath(__file__))
parent = os.path.dirname(dir_name)
# print(parent)
sys.path.append(parent)


###############################################################################
# Related Imports
###############################################################################
# from require import STARTUP
from Scripts import sw_update, M_CTC_ID_018


class Master_Class():
    def __init__(self, Planes, Levels, Test_Ids) -> None:
        with open('{}/test_case.json'.format(dir_name)) as test_cases:
            self.Planes, self.Levels, self.Test_Ids = Planes, Levels, Test_Ids
            self.overall_summary = []
            self.overall_status = []
            #### {level_plane_id:'id_api'} ####
            self.All_Test_Cases = json.load(test_cases)
            self.Running_Cases = []

    ###############################################################################
    # Return no of key according to level & plane combinations 
    ###############################################################################
    def genrate_keys(self,test_key):
        tc_count =0
        for key,val in self.All_Test_Cases.items():
            if key.startswith(test_key):
                tc_count+=1
        return tc_count

    ###############################################################################
    # Add the test Cases into a list which are going to run 
    ###############################################################################
    def add_test_cases(self):
        if self.Test_Ids:
            for plane in self.Planes:
                for level in self.Levels:
                    for test_id in self.Test_Ids:
                        test_key = f'L{level}_{plane}_{test_id}'
                        if self.All_Test_Cases.get(test_key):
                            self.Running_Cases.append(self.All_Test_Cases[test_key])
        else:
            for plane in self.Planes:
                for level in self.Levels:
                    test_key = f'L{level}_{plane}'
                    max_keys = self.genrate_keys(test_key)
                    for key in range(1,max_keys+1):
                        test_key = f'L{level}_{plane}_{key}'
                        if self.All_Test_Cases.get(test_key):
                            self.Running_Cases.append(self.All_Test_Cases[test_key])
                            
        return self.Running_Cases

    ###############################################################################
    # Main Function which will do the combination of performing test case and executing them 
    ###############################################################################
    def main_function(self):
        test_case_numbers = []
        if len(self.Planes) > 0:
            if len(self.Levels) > 0:
                if len(self.Test_Ids) > 0:
                    print(self.Test_Ids)
            else:
                self.Levels = [i for i in range(1, 5)]
        else:
            self.Planes = ["M", "S", "CU"]
            self.Levels = [i for i in range(1, 5)]
        self.add_test_cases()
        
        for test_case in self.Running_Cases:
            self.Execute_Script(test_case)
        self.check_and_generte_summary()

    def Execute_Script(self,test_case):
        print('\n')
        print('='*100)
        print('##### EXECUTING TEST CASE IS {} #####'.format(test_case).center(100))
        print('='*100)
        Result = eval(test_case)()
        self.overall_status.append([test_case.split('.')[0],'Pass' if Result[0] else 'Fail',Result[2]])
        self.overall_summary.append('{}'.format(test_case.split('.')[0]))
        self.overall_summary.extend(Result[1])
        
    
    def check_and_generte_summary(self):
        ###############################################################################
        # Overall Summary of Testing
        ###############################################################################
        print('\n\n')
        print('#'*150)
        for i in self.overall_summary:
            if type(i) == str:
                print('-'*100)
                print("##{}##".format(f"Test Case : {i}".center(96)))
                print('-'*100)
            elif len(i[1]) == 0:
                print('\n')
                print('='*100)
                print("{1} {0} {1}".format(i[0],'*'*5).center(100))
                print('='*100)
            else:
                print(f"{f'{i[0]}' : <66}{'=' : ^5}{f'{i[1]}' : <20}")

        ###############################################################################
        # Overall Status of Testing
        ###############################################################################
        print('\n\n')
        for i in self.overall_status:
            if type(i) == str:
                print('{0}\n\t\t{1}{2}{1}\n{0}'.format('='*100, '*'*20, i))
            elif len(i[1]) == 0:
                print('='*100)
                print("{1} {0} {1}".format(i[0],'*'*5).center(100))
                print('='*100)
                print(f"{'Test Case ID' : <30}{'Status' : <20}{'Execution Time' : ^20}")
            else:
                print(f"{f'{i[0]}' : <30}{f'{i[1]}' : <20}{f'{i[2]}' : ^20}")



        

if __name__ == "__main__":
    Planes = input('Enter Space Saprated Plane: ').upper().strip().split()
    Levels = input('Enter Space Saprated Level: ').upper().strip().split()
    Test_ids = input('Enter Space Saprated Test Ids: ').strip().split()
    obj1 = Master_Class(Planes,Levels,Test_ids)
    obj1.main_function()
    pass
