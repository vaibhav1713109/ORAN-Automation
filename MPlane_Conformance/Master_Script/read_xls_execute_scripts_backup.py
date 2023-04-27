import pandas as pd
import subprocess, shutil
import xml.etree.ElementTree as ET
import time
import os,sys, random
from tabulate import tabulate

###############################################################################
## Directory Path
###############################################################################
dir_name = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(dir_name)
print(dir_name)
print(root_dir)
sys.path.append(root_dir)

#from require.Notification import notification

def create_table_and_send_to_space(data):
    Header = ['Test Case', 'Status']
    ACT_RES = tabulate(data,Header,tablefmt='fancy_grid')
    # notification(ACT_RES)


def create_xml_file():
    os.remove('{}/test_status.xml'.format(dir_name)) if os.path.exists('{}/test_status.xml'.format(dir_name)) else None
    root = ET.Element("testsuites")
    testsuite = ET.SubElement(root, "testsuite")
    testsuite.set("name", "cd_testings")
    testsuite.set("tests", "0")
    testsuite.set("skipped", "0")
    testsuite.set("failures", "0")
    testsuite.set("time", "0")
    tree = ET.ElementTree(root)
    tree.write('{}/test_status.xml'.format(dir_name), encoding="utf-8", xml_declaration=True)

def append_Timeout_failure_in_xml_file(script_name, plane, status, elapsed_time):
    tree = ET.parse('{}/test_status.xml'.format(dir_name))
    root = tree.getroot()
    testsuite = root.find('testsuite')
    testsuite.set('tests', str(int(testsuite.get('tests'))+1))
    testsuite.set('failures', str(int(testsuite.get('failures'))+1))
    testsuite.set('time', str(float(testsuite.get('time'))+elapsed_time))
    testcase = ET.SubElement(testsuite, 'testcase')
    testcase.set('name', script_name)
    testcase.set('classname', plane)
    testcase.set('time', str(elapsed_time))
    failure = ET.SubElement(testcase, 'failure')
    failure.set('type', status)
    failure.text = f"The testcase execution time reached beyond {elapsed_time}"
    tree.write('{}/test_status.xml'.format(dir_name), encoding='utf-8', xml_declaration=True)

def append_pass_in_xml_file(script_name, plane, status, elapsed_time):
    tree = ET.parse('{}/test_status.xml'.format(dir_name))
    root = tree.getroot()
    testsuite = root.find('testsuite')
    testsuite.set('tests', str(int(testsuite.get('tests'))+1))
    testsuite.set('time', str(float(testsuite.get('time'))+elapsed_time))
    testcase = ET.SubElement(testsuite, 'testcase')
    testcase.set('name', script_name)
    testcase.set('classname', plane)
    testcase.set('time', str(elapsed_time))
    #ET.SubElement(testcase, status)
    tree.write('{}/test_status.xml'.format(dir_name), encoding='utf-8', xml_declaration=True)

def append_fail_in_xml_file(script_name, plane, status, elapsed_time, return_code):
    tree = ET.parse('{}/test_status.xml'.format(dir_name))
    root = tree.getroot()
    testsuite = root.find('testsuite')
    testsuite.set('tests', str(int(testsuite.get('tests'))+1))
    testsuite.set('failures', str(int(testsuite.get('failures'))+1))
    testsuite.set('time', str(float(testsuite.get('time'))+elapsed_time))
    testcase = ET.SubElement(testsuite, 'testcase')
    testcase.set('name', script_name)
    testcase.set('classname', plane)
    testcase.set('time', str(elapsed_time))
    failure = ET.SubElement(testcase, 'failure')
    failure.set('type', status)
    failure.text = f"The expected return code was 0, But obtained : {return_code}"
    tree.write('{}/test_status.xml'.format(dir_name), encoding='utf-8', xml_declaration=True)

def append_skiped_in_xml_file(script_name, plane, status, elapsed_time):
    tree = ET.parse('{}/test_status.xml'.format(dir_name))
    root = tree.getroot()
    testsuite = root.find('testsuite')
    testsuite.set('tests', str(int(testsuite.get('tests'))+1))
    testsuite.set('skipped', str(int(testsuite.get('skipped'))+1))
    testsuite.set('time', str(float(testsuite.get('time'))+elapsed_time))
    testcase = ET.SubElement(testsuite, 'testcase')
    testcase.set('name', script_name)
    testcase.set('classname', plane)
    testcase.set('time', str(elapsed_time))
    skipped = ET.SubElement(testcase, status)
    tree.write('{}/test_status.xml'.format(dir_name))

def read_excel_and_execute(ru_name,Pass,Fail,Skip):
    df = pd.read_excel('{}/test_case.xlsx'.format(dir_name))
    create_xml_file()

    for i, row in df.iterrows():
        execute = row['Execute']
        script_name = row['Script Name']
        script_path = row['Script Path']
        arguments = row['Arguments']
        timeout = row['Timeout']
        plane = row['Plane']
        parent_dir = root_dir.rsplit('/',1)
        input_file_path = f"{root_dir}/{ru_name}/inputs.ini"
        output_file_path = f"{root_dir}/MPLANE/require/inputs.ini"
        absolute_script_path = f'{root_dir}/{script_path}'
        print(absolute_script_path,input_file_path,output_file_path)
        try:
            shutil.copyfile(input_file_path,output_file_path)
            shutil.copyfile(input_file_path,output_file_path)
            os.mkdir('{}/MPLANE/LOGS/{}'.format(root_dir, ru_name))
        except Exception as e:
            print(e)
            pass
        if execute == 'yes':
            start_time = time.time()
            if str(arguments) == 'nan':
                process = subprocess.Popen(['{}/CI_CD/binpython'.format(root_dir), '{0}/{1}'.format(absolute_script_path,script_name)])
            else:
                #print(arguments,type(arguments),str(arguments))
                process = subprocess.Popen(['{}/CI_CD/binpython'.format(root_dir), '{0}/{1}'.format(absolute_script_path,script_name),str(arguments)])
            timeout_flag = False
            while process.poll() is None:
                elapsed_time = time.time() - start_time
                if elapsed_time > timeout:
                    process.terminate()
                    append_Timeout_failure_in_xml_file(script_name, plane, "Timeout", elapsed_time)
                    timeout_flag = True
                    break

            if timeout_flag:
                continue

            return_code = process.returncode
            if return_code == 0:
                append_pass_in_xml_file(script_name, plane, "pass", elapsed_time)
                executed_test_case.append([script_name,'Pass'])
                Pass+=1
            else:
                append_fail_in_xml_file(script_name, plane, "fail", elapsed_time, return_code)
                executed_test_case.append([script_name,'Fail'])
                Fail+=1
        else:
            append_skiped_in_xml_file(script_name, plane, "skipped", 0)
            executed_test_case.append([script_name,'Skip'])
            Skip+=1
    return Pass, Fail,Skip
                
if __name__ == "__main__":
    # try:
        Pass,Fail,Skip = 0,0,0
        executed_test_case = []
        if len(sys.argv) > 1:
            ru_name = sys.argv[1]
            Pass,Fail,Skip = read_excel_and_execute(ru_name,Pass,Fail,Skip)
            create_table_and_send_to_space(executed_test_case)
            # notification(f'Total Test cases : {len(executed_test_case)}\nPass Test cases : {Pass}\nFail Test cases : {Fail}\nSkip Test cases : {Skip}')
        else:
            print('Please give one argument {RU_name}\nUse given foramt --> "sudo python read_xls_execute_scripts.py LPRU"')
    # except Exception as e:
    #     print(f'Error : {e}')
    #     print('Use given foramt --> "sudo python read_xls_execute_scripts.py LPRU"')

