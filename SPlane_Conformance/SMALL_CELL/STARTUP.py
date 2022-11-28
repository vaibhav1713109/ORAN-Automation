from os import name, path
from fpdf import FPDF
import json ,os
from selenium.webdriver.remote.webelement import WebElement
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from calnexRest import calnexInit, calnexSet
from selenium.webdriver.common.action_chains import ActionChains
import time
webdriver_path = '/home/vvdn/Downloads/chromedriver_linux641/chromedriver'
d1 = os.path.dirname(os.path.realpath(__file__))

import pyscreenshot as ImageGrab
f = open(f'{d1}/details.json')
data = json.load(f)
def STORE_DATA(*datas,Format,PDF):
     for data in datas:
        # OUTPUT_LIST.append(*data)
        # print(''.join([*data])
          if Format == True:
               print('='*100)
               print(data)
               print('='*100)
               HEADING(PDF,data)

          elif Format == 'XML':
               print(data)
               XML_FORMAT(PDF,data)

          elif Format == 'CONF':
               print('='*100)
               print(data)
               print('='*100)
               CONFDENTIAL(PDF,data)
          
          elif Format == 'DESC':
               print('='*100)
               print(data)
               print('='*100)
               Test_desc(PDF,data)
          
          elif Format == 'TEST_STEP':
               print('='*100)
               print(data)
               print('='*100)
               Test_Step(PDF,data)
          
          # elif Format == False:
          #      # print('='*100)
          #      print(data)
          #      # print('='*100)
          #      Test_Step(PDF,data)

          else:
               print(data)
               PDF.write(h=5,txt=data)
               PDF.ln()

def CREATE_LOGS(PDF,name):
    # STORE_DATA(OUTPUT_LIST,OUTPUT_LIST)
    PDF.output(f"{path}.pdf")
    PDF.output(f"{path+name}.pdf")




def Test_desc(PDF,data):
     PDF.set_font("Times",style = 'B', size=13)
     PDF.set_text_color(17, 64, 37)
     PDF.write(5, '\n{}\n'.format('='*71))
     PDF.multi_cell(w =180,h = 10,txt='Test Description : {}'.format(data),border=1,align='L')
     PDF.write(5, '\n{}\n'.format('='*71))
     PDF.set_font("Times",style = '',size = 9)
     PDF.set_text_color(0, 0, 0)
     # PDF.ln(80)
     pass

def PDF_CAP(TC):
    d1 = os.path.dirname(os.path.realpath(__file__))
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Times", size=9)
    pdf.image(name=f'{d1}/Front_Page.png', x = None, y = None, w = 180, h = 70, type = '', link = '')
    pdf.ln(30)
    line_height = (pdf.font_size) * 3.5
    col_width = pdf.epw / 2 
    data1 = (
    (f"Test Case","S_CTC_ID_00{0}".format(TC)),
    ("Brief", "MCB1 ORAN CONFORMANCE TEST LOGS FOR S PLANE "),
    ("Author","Ravi Kumar, (ravi.kumar1@vvdntech.in)"),
    ("Software Release for MCB1 ","Beta Release:1.0.3")
)
    for row in data1:
     for datum in row:
          pdf.multi_cell(col_width, line_height, datum, border=1,
                    new_x="RIGHT", new_y="TOP", max_line_height=pdf.font_size)
     pdf.ln(line_height)
    pdf.add_page()
    return pdf




def HEADING(PDF,data,*args):
    PDF.set_font("Times",style = 'B', size=9)
    PDF.write(5, '\n{}\n'.format('='*75))
    PDF.write(5,data)
    PDF.write(5, '\n{}\n'.format('='*75))
    PDF.set_font("Times",style = '',size = 9)



def XML_FORMAT(PDF,data):
    PDF.set_text_color(0,0,0)
    PDF.write(4,data)
    PDF.set_text_color(0, 0, 0)

def CONFDENTIAL(PDF,data):
     PDF.set_font("Times",style = 'B', size=15)
     PDF.set_text_color(10, 32, 71)
     PDF.write(5, '\n{}\n'.format('='*62))
     PDF.multi_cell(w =180,txt=data,border=1,align='L',h = 5)
     PDF.write(5, '\n{}\n'.format('='*62))
     PDF.set_font("Times",style = '',size = 9)
     PDF.set_text_color(0, 0, 0)
     PDF.ln(30)
     pass

def Test_Step(PDF,data):
    PDF.set_font("Times",style = 'B', size=11)
    PDF.set_text_color(125, 93, 65)
    PDF.write(5, '\n{}\n'.format('='*80))
    PDF.write(5,data)
    PDF.write(5, '\n{}\n'.format('='*80))
    PDF.set_font("Times",style = '',size = 9)
    PDF.set_text_color(0,0,0)

# pdf = PDF_CAP()
# CONF = ADD_CONFIDENTIAL('10',SW_R='4.0.9')
# STORE_DATA(CONF,Heading='CONF',PDF=pdf)
# Test_Desc = 'This scenario validates that the O-RU NETCONF Server properly executes a get command with a filter applied.'
# STORE_DATA(Test_Desc,Heading='DESC',PswSlot2:VALID:false:false:STL O-RU:VN:90f0b6c:Beta Release:5.0.2:BOOT0002                                                                    
#                </user>
#           </users>
#           </filter>
#                 '''
# STORE_DATA(u_name,Heading='XML',PDF=pdf)
# STORE_DATA('\t\t***********step 1 and 2 Retrival of ru information with filter **********',Heading=True,PDF=pdf)
# CREATE_LOGS(pdf)



def Open_window():
    calnexInit(data["Paragon_IP"])
    global driver
    # driver = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver_linux641/chromedriver')
    driver = webdriver.Chrome(webdriver_path)
    driver.get("http://" + data["Paragon_IP"])
    time.sleep(8)
    driver.maximize_window()

 


def PTP_OFF():
    d1 = os.path.dirname(os.path.realpath(__file__))
    f = open(f'{d1}/details.json')
    data = json.load(f)
    calnexInit(data["Paragon_IP"])
    global driver
    # pdf = FPDF()

    driver = webdriver.Chrome(webdriver_path)
    driver.get("http://" + f"{data['Paragon_IP']}")
    driver.maximize_window()
    calnexSet("app/mse/master/Master1/stop")
    time.sleep(5)
    im =ImageGrab.grab(bbox=(250, 210, 980, 480))
    im.save(f"{d1}"+'/PTP_OFF.png')
    # pdf.image(name='PTP_OFF.png', x = None, y = None, w = 180, h = 70, type = '', link = '')
    # pdf.ln(5)
    time.sleep(5)


#### # # FOR MASTER 1  
def clock_class_6():
    Open_window()
    pdf = FPDF()
    calnexSet("app/mse/master/Master1/clockclass", "ClockClass", 6)
    calnexSet("app/mse/applypending")
    time.sleep(2)

    calnexSet("app/mse/master/Master1/start")
    time.sleep(5)
    im =ImageGrab.grab(bbox=(250, 210, 980, 480))
    im.save(f'{d1}'+'/PTP_ON.png')
    # pdf.image(name='PTP_ON.png', x = None, y = None, w = 180, h = 70, type = '', link = '')
    # pdf.ln(5)
    element = driver.find_element("xpath", "//*[@id='trackContainerTracksNode']/track-master-slave-emulation/div/div[2]/div[2]/div/div[3]/div[2]/div[9]").click()
    time.sleep(2)
    element = driver.find_element("xpath", "//*[@id='trackContainerTracksNode']/track-master-slave-emulation/div/div[2]/div[3]/div/div[2]/div/div[3]/div/cal-tab-group/div/div[1]/ul/li[6]/a").click()
    time.sleep(2)
    element = driver.find_element("xpath", "//*[@id='trackContainerTracksNode']/track-all-pkt-capture/div/div[2]/div[1]/div[2]/div[3]/div/h6")
    actions = ActionChains(driver)
    actions.move_to_element(element)
    # ## actions.click();
    actions.perform()
    time.sleep(2)

    im =ImageGrab.grab(bbox=(270, 210, 1140, 600))
    im.save(f'{d1}'+'/clock_class_6.png')
    # pdf.image(name='clock_class_6.png', x = None, y = None, w = 180, h = 70, type = '', link = '')
    # pdf.ln(5)
    driver.close()

def SYNCE_NONE():
    # pdf = FPDF()
    calnexSet("app/generation/synce/esmc/Port1/ssm", "SsmValue", 'QL-PRC')
    calnexSet("app/generation/synce/esmc/Port1/stop")
    # element = driver.find_element("xpath","//*[@id='wander_gen_track_container']/div[2]/div[2]/div/div[3]/div/div/div/cal-tab-group/div/div[2]/div[1]/div/div/div[2]/div[10]/div[4]")
    element = driver.find_element("xpath", "//*[@id='wander_gen_track_container']/div[2]/div[2]/div/div[3]/div/div/div/cal-tab-group/div/div[2]/div[1]/div/div/div[2]/div[10]/div[4]")

    actions = ActionChains(driver)
    actions.move_to_element(element)
    actions.perform()
    time.sleep(5)
    # driver.close()

    im =ImageGrab.grab(bbox=(250, 240, 1155, 595))
    im.save(f'{d1}'+'/SYNCE_NONE.png')
    # pdf.image(name='SYNCE_NONE.png', x = None, y = None, w = 180, h = 70, type = '', link = '')
    # pdf.ln(5)
    driver.minimize_window()
    time.sleep(2)



def SYNCE_PRC():
    Open_window()
    pdf = FPDF()
    calnexSet("app/generation/synce/esmc/Port1/ssm", "SsmValue", 'QL-PRC')
    calnexSet("app/generation/synce/esmc/Port1/start")
    # element = driver.find_element("xpath","//*[@id='wander_gen_track_container']/div[2]/div[2]/div/div[3]/div/div/div/cal-tab-group/div/div[2]/div[1]/div/div/div[2]/div[10]/div[4]")
    element = driver.find_element("xpath", "//*[@id='wander_gen_track_container']/div[2]/div[2]/div/div[3]/div/div/div/cal-tab-group/div/div[2]/div[1]/div/div/div[2]/div[10]/div[4]")
    actions = ActionChains(driver)
    actions.move_to_element(element)
    actions.perform()
    time.sleep(5)

    im =ImageGrab.grab(bbox=(250, 240, 1155, 595))
    im.save(f'{d1}'+'/SYNCE_PRC.png')
    # pdf.image(name='SYNCE_PRC.png', x = None, y = None, w = 180, h = 70, type = '', link = '')
    # pdf.ln(5)
    driver.close()
    time.sleep(2)


def SYNCE_EEC1():
    Open_window()
    pdf = FPDF()
    calnexSet("app/generation/synce/esmc/Port1/ssm", "SsmValue", 'QL-EEC1/SEC')
    calnexSet("app/generation/synce/esmc/Port1/start")
    element = driver.find_element("xpath", "//*[@id='wander_gen_track_container']/div[2]/div[2]/div/div[3]/div/div/div/cal-tab-group/div/div[2]/div[1]/div/div/div[2]/div[10]/div[4]")
    actions = ActionChains(driver)
    actions.move_to_element(element)
    actions.perform()
    time.sleep(5)

    im =ImageGrab.grab(bbox=(250, 240, 1155, 595))
    im.save(f'{d1}'+'/SYNCE_EEC1.png')
    # pdf.image(name='SYNCE_EEC1.png', x = None, y = None, w = 180, h = 70, type = '', link = '')
    # pdf.ln(5)

    driver.close()

def SYNCE_DNU():
    Open_window()
    pdf = FPDF()
    driver.maximize_window()
    calnexSet("app/generation/synce/esmc/Port1/ssm", "SsmValue", 'QL-DNU')
    element = driver.find_element("xpath","//*[@id='wander_gen_track_container']/div[2]/div[2]/div/div[3]/div/div/div/cal-tab-group/div/div[2]/div[1]/div/div/div[2]/div[10]/div[4]")
    actions = ActionChains(driver)
    actions.move_to_element(element)
    actions.perform()
    time.sleep(5)

    im =ImageGrab.grab(bbox=(250, 240, 1155, 595))
    im.save(f'{d1}'+'/SYNCE_DNU.png')
    # pdf.image(name='SYNCE_DNU.png', x = None, y = None, w = 180, h = 70, type = '', link = '')
    # pdf.ln(5)

    driver.close()
    time.sleep(2)


# Credentials
usr = "operator"
pss = "admin123"
file_path = "/home/vvdn/Downloads/B41_2.1.0_revb/Splane"





def clock_class_7():
    Open_window()
    pdf = FPDF()
    driver.maximize_window()
    calnexSet("app/mse/master/Master1/clockclass", "ClockClass", 7)
    calnexSet("app/mse/applypending")
    time.sleep(5)
    element = driver.find_element("xpath", "//*[@id='trackContainerTracksNode']/track-master-slave-emulation/div/div[2]/div[2]/div/div[3]/div[2]/div[9]").click()
    time.sleep(2)
    element6 = driver.find_element("xpath", "//*[@id='trackContainerTracksNode']/track-master-slave-emulation/div/div[2]/div[3]/div/div[2]/div/div[3]/div/cal-tab-group/div/div[1]/ul/li[6]/a").click()
    time.sleep(2)
    element6 = driver.find_element("xpath", "//*[@id='trackContainerTracksNode']/track-all-pkt-capture/div/div[2]/div[1]/div[2]/div[3]/div/h6")
    actions = ActionChains(driver)
    actions.move_to_element(element6)
    # ## actions.click();
    actions.perform()
    time.sleep(2)
    im =ImageGrab.grab(bbox=(270, 210, 1180, 650))
    im.save(f'{d1}'+'/clock_class_7.png')
    # pdf.image(name='clock_class_7.png', x = None, y = None, w = 180, h = 70, type = '', link = '')
    # pdf.ln(5)
    time.sleep(2)
    driver.close
    

def clock_class_135():
    Open_window()
    pdf = FPDF()
    driver.maximize_window()
    calnexSet("app/mse/master/Master1/clockclass", "ClockClass", 135)
    calnexSet("app/mse/applypending")
    time.sleep(5)
    element = driver.find_element("xpath", "//*[@id='trackContainerTracksNode']/track-master-slave-emulation/div/div[2]/div[2]/div/div[3]/div[2]/div[9]").click()
    time.sleep(2)
    element6 = driver.find_element("xpath", "//*[@id='trackContainerTracksNode']/track-master-slave-emulation/div/div[2]/div[3]/div/div[2]/div/div[3]/div/cal-tab-group/div/div[1]/ul/li[6]/a").click()
    time.sleep(2)
    element6 = driver.find_element("xpath", "//*[@id='trackContainerTracksNode']/track-all-pkt-capture/div/div[2]/div[1]/div[2]/div[3]/div/h6")
    actions = ActionChains(driver)
    actions.move_to_element(element6)
    # ## actions.click();
    actions.perform()
    time.sleep(2)
    im =ImageGrab.grab(bbox=(270, 210, 1180, 650))
    im.save(f'{d1}'+'/clock_class_135.png')
    # pdf.image(name='clock_class_135.png', x = None, y = None, w = 180, h = 70, type = '', link = '')
    # pdf.ln(5)
    driver.close()


def clock_class_140():
    Open_window()
    pdf = FPDF()
    driver.maximize_window()
    calnexSet("app/mse/master/Master1/clockclass", "ClockClass", 140)
    calnexSet("app/mse/applypending")
    time.sleep(5)
    element4 = driver.find_element("xpath", "//*[@id='trackContainerTracksNode']/track-master-slave-emulation/div/div[2]/div[2]/div/div[3]/div[2]/div[9]").click()
    time.sleep(2)
    element4 = driver.find_element("xpath", "//*[@id='trackContainerTracksNode']/track-master-slave-emulation/div/div[2]/div[3]/div/div[2]/div/div[3]/div/cal-tab-group/div/div[1]/ul/li[6]/a").click()
    time.sleep(2)
    element4 = driver.find_element("xpath", "//*[@id='trackContainerTracksNode']/track-all-pkt-capture/div/div[2]/div[1]/div[2]/div[3]/div/h6")
    actions = ActionChains(driver)
    actions.move_to_element(element4)
    # ## actions.click();
    actions.perform()
    time.sleep(2)

    im =ImageGrab.grab(bbox=(270, 210, 1140, 600))
    im.save(f'{d1}'+'/clock_class_140.png')
    # pdf.image(name='clock_class_140.png', x = None, y = None, w = 180, h = 70, type = '', link = '')
    # pdf.ln(5)
    time.sleep(2)
    driver.close()

def clock_class_150():
    Open_window()
    pdf = FPDF()
    driver.maximize_window()
    calnexSet("app/mse/master/Master1/clockclass", "ClockClass", 150)
    calnexSet("app/mse/applypending")
    time.sleep(5)
    element5 = driver.find_element("xpath", "//*[@id='trackContainerTracksNode']/track-master-slave-emulation/div/div[2]/div[2]/div/div[3]/div[2]/div[9]").click()
    time.sleep(2)
    element5 = driver.find_element("xpath", "//*[@id='trackContainerTracksNode']/track-master-slave-emulation/div/div[2]/div[3]/div/div[2]/div/div[3]/div/cal-tab-group/div/div[1]/ul/li[6]/a").click()
    time.sleep(2)
    element5 = driver.find_element("xpath", "//*[@id='trackContainerTracksNode']/track-all-pkt-capture/div/div[2]/div[1]/div[2]/div[3]/div/h6")
    actions = ActionChains(driver)
    actions.move_to_element(element5)
    # ## actions.click();
    actions.perform()
    time.sleep(2)

    im =ImageGrab.grab(bbox=(270, 210, 1140, 600))
    im.save(f'{d1}'+'/clock_class_150.png')
    # pdf.image(name='clock_class_150.png', x = None, y = None, w = 180, h = 70, type = '', link = '')
    # pdf.ln(5)
    time.sleep(2)
    driver.close()
    

def clock_class_160():
    Open_window()
    pdf = FPDF()
    driver.maximize_window()
    calnexSet("app/mse/master/Master1/clockclass", "ClockClass", 160)
    calnexSet("app/mse/applypending")
    time.sleep(5)
    element6 = driver.find_element("xpath", "//*[@id='trackContainerTracksNode']/track-master-slave-emulation/div/div[2]/div[2]/div/div[3]/div[2]/div[9]").click()
    time.sleep(2)
    element6 = driver.find_element("xpath", "//*[@id='trackContainerTracksNode']/track-master-slave-emulation/div/div[2]/div[3]/div/div[2]/div/div[3]/div/cal-tab-group/div/div[1]/ul/li[6]/a").click()
    time.sleep(2)
    element6 = driver.find_element("xpath", "//*[@id='trackContainerTracksNode']/track-all-pkt-capture/div/div[2]/div[1]/div[2]/div[3]/div/h6")
    actions = ActionChains(driver)
    actions.move_to_element(element6)
    # ## actions.click();
    actions.perform()
    time.sleep(2)

    im =ImageGrab.grab(bbox=(270, 210, 1140, 600))
    im.save(f'{d1}'+'/clock_class_160.png')
    # pdf.image(name='clock_class_160.png', x = None, y = None, w = 180, h = 70, type = '', link = '')
    # pdf.ln(5)
    time.sleep(2)
    driver.close()

def domain():
    Open_window()
    pdf = FPDF()
    calnexSet("app/mse/master/Master1/domain", "Domain", 25)
    calnexSet("app/mse/applypending")
    time.sleep(5)
    element8 = driver.find_element("xpath", "//*[@id='trackContainerTracksNode']/track-master-slave-emulation/div/div[2]/div[2]/div/div[3]/div[2]/div[9]").click()
    time.sleep(2)
    time.sleep(2 )
    element8 = driver.find_element("xpath","//*[@id='trackContainerTracksNode']/track-master-slave-emulation/div/div[2]/div[3]/div/div[2]/div/div[3]/div/cal-tab-group/div/div[1]/ul/li[5]/a").click()
    time.sleep(2)
    element8 = driver.find_element("xpath", "//*[@id='trackContainerTracksNode']/track-all-pkt-capture/div/div[2]/div[1]/div[2]/div[3]/div/h6")
    actions = ActionChains(driver)
    actions.move_to_element(element8)
    actions.perform()
    time.sleep(2)
    im =ImageGrab.grab(bbox=(250, 255, 1180, 650))
    im.save(f'{d1}'+'/domain.png')
    # pdf.image(name='domain.png', x = None, y = None, w = 180, h = 70, type = '', link = '')
    # pdf.ln(5)
    time.sleep(2)
    driver.close()



if __name__ == '__main__':
    

    PTP_OFF()
    SYNCE_NONE()
    clock_class_6()
    SYNCE_PRC()
    SYNCE_EEC1()
    SYNCE_DNU()
    clock_class_7()
    clock_class_135()
    clock_class_140()
    clock_class_150()
    clock_class_160()
    domain()



















