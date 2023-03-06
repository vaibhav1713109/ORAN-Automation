import pandas as pd
import subprocess
import xml.etree.ElementTree as ET
import time
import os,sys, random

###############################################################################
## Directory Path
###############################################################################
dir_name = os.path.dirname(os.path.abspath(__file__))
parent = os.path.dirname(dir_name)
print(dir_name)
sys.path.append(parent)



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

def read_excel_and_execute():
    df = pd.read_excel('{}/test_case.xlsx'.format(dir_name))
    create_xml_file()

    for i, row in df.iterrows():
        execute = row['Execute']
        script_name = row['Script Name']
        script_path = row['Script Path']
        arguments = row['Arguments']
        timeout = row['Timeout']
        plane = row['Plane']

        if execute == 'yes':
            # print('='*100)
            # print(f'Test Case {script_name} Started || Status : Running') 
            # print('='*100)
            start_time = time.time()
            process = subprocess.Popen(['/home/sebu.mathew/QA_CICD/CI_CD/bin/python', '{0}/{1}'.format(script_path,script_name), str(arguments)])
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
            else:
                append_fail_in_xml_file(script_name, plane, "fail", elapsed_time, return_code)
        else:
            append_skiped_in_xml_file(script_name, plane, "Skipped", 0)
        
                
if __name__ == "__main__":
    read_excel_and_execute()
    # script_name, plane,elapsed_time = 'uplane_config.py','M_Plane',118
    # create_xml_file()
    # append_pass_in_xml_file(script_name, plane, "pass", elapsed_time)
    # append_fail_in_xml_file(script_name, plane, "fail", elapsed_time,1)
    # append_skiped_in_xml_file(script_name, plane, "Skipped", 0)               

