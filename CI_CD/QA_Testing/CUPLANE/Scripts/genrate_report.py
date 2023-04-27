from functools import reduce
from fpdf import FPDF
from fpdf.enums import XPos, YPos
import os, csv
from tabulate import tabulate
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# print(root_dir)

dir_name = os.path.dirname(os.path.abspath(__file__))
print(dir_name)

def fetch_crc():
    crc_pass = crc_fail = 0
    with open('{}/CRC_data_CC0Bits.csv'.format(dir_name), mode ='r')as file:
        # reading the CSV file
        csvFile = csv.reader(file)
        # print(type(list(csvFile)))
        data_list = []
        # displaying the contents of the CSV file
        Header = ['Channel', 'Slot', 'CRC Passed', 'Bit Length']
        for lines in csvFile:
            data_list.append([lines[0],lines[1],lines[2],lines[3]])
            if lines[2] == True:
                crc_pass+=1
            else:
                crc_fail+=1
        Data = data_list[1:]
        print(Header)
        ACT_RES = tabulate(Data,Header,tablefmt='fancy_grid')
        print(ACT_RES)
    print('*'*100)
    print(f'CRC Pass = {crc_pass}\nCRC Fail = {crc_fail}')
    print('*'*100)
    return data_list


class PDF(FPDF):
    def header(self):
        # Logo
        self.image('{}/vvdn_logo.png'.format(dir_name), 10, 8, 33)
        self.set_text_color(44, 112, 232)
        self.set_font('Times', 'B', 15)
        # self.set_x(-45)
        # self.set_font('Times', 'B', 12)
        # self.cell(10,10, 'ACLR & POWER', 0, 0, 'C')
        self.set_text_color(0,0,0)
        self.ln(20)

    # Page footer
    def footer(self):
        self.set_y(-15)
        self.set_font('Times', 'I', 8)
        self.set_text_color(0,0,0)
        self.cell(0, 10, 'Page %s' % self.page_no(), XPos.RIGHT, new_y= YPos.NEXT, align ='L')
        self.set_text_color(44, 112, 232)
        self.set_font('Times', 'B', 10)
        self.cell(0, -10, 'Copyright (c) 2016 - 2022 VVDN Technologies Pvt Ltd', XPos.RIGHT, new_y= YPos.NEXT, align='R')
        self.cell(0,10)
        self.set_text_color(0,0,0)

################# Table Heading ################
def HEADING(PDF,data):
    print('='*100)
    print(data)
    print('='*100)
    PDF.set_font("Times",style = 'BU', size=20)
    PDF.ln(5)
    PDF.set_text_color(112, 112, 112)
    PDF.multi_cell(w=PDF.epw,txt=data,border=0,align='C')
    PDF.set_text_color(0,0,0)
    PDF.ln(5)
    PDF.set_font("Times",style = '',size=12)
    pass


################# Add Front Page ################
def PDF_CAP():
    pdf = PDF()
    pdf.add_page(format=(350,250))
    pdf.set_font("Times", size=9)
    y = int(pdf.epw)
    pdf.image(name='{}/Front_Page.png'.format(dir_name), x = None, y = None, w = y, h = 0, type = '', link = '')
    # pdf.ln(50)
    # pdf.set_font("Times",style = 'B', size=15)
    # pdf.multi_cell(w =y,txt='BASE TEST CASE',border=1,align='C')
    pdf.set_font("Times",style = '',size = 9)
    return pdf

def Test_HEADING(PDF,data,*args):
    li = data.split('\n')
    print('-'*100)
    print(data)
    print('-'*100)
    PDF.set_font("Times",style = 'B', size=11)
    PDF.write(5,li[0])
    PDF.ln(6)
    PDF.set_font("Times",style = '',size = 11)
    PDF.write(5,li[1])
    PDF.ln(10)

def render_header(PDF,TABLE_Header,line_height,col_width):
    PDF.set_font("Times",style="B")  # enabling bold text
    for col_name in TABLE_Header:
        m_l_h = PDF.font_size
        PDF.multi_cell(w=col_width, h = line_height, txt = col_name, border=1,
                new_x="RIGHT", new_y="TOP", max_line_height=PDF.font_size,align='C')
    PDF.ln(line_height)
    PDF.set_font("Times",style = '',size = 11)

def render_table_data(PDF,TABLE_DATA,line_height,col_width,TABLE_Header):  # repeat data rows
    for row in TABLE_DATA:
        if PDF.will_page_break(line_height):
            PDF.set_font("Times",style="B",size = 15)
            render_header(PDF,TABLE_Header,line_height,col_width)
            PDF.set_font("Times",style="",size = 11)
        for datum in row:
            if datum == 'Pass':
                PDF.set_fill_color(105, 224, 113)
            elif datum =='Fail':
                PDF.set_fill_color(235, 52, 52)
            else:
                PDF.set_fill_color(255,255,255)
            PDF.multi_cell(w=col_width, h = line_height, txt = datum, border=1,
                new_x="RIGHT", new_y="TOP", max_line_height=PDF.font_size,align='C',fill=True)
        PDF.ln(line_height)


def add_ul_image(PDF,Images):
    y = int(PDF.epw)
    i = 0
    PDF.add_page(format=(350,250))
    for key,val in Images.items():
        i+=1
        PDF.set_y(30)
        PDF.set_font("Times",style = 'B', size=15)
        PDF.multi_cell(w=PDF.epw,txt='Channel {}'.format(key),border=0,align='C')
        for img in val:
            PDF.image(img, 20, 40, 300)
            PDF.add_page(format=(350,250)) 
        PDF.set_font("Times",style = '', size=11) 
        pass        
    PDF.set_font("Times",style = '',size = 9)
    pass


def add_image(PDF,Images):
    y = int(PDF.epw)
    i = 0
    PDF.add_page(format=(350,250))
    for key,val in Images.items():
        i+=1
        PDF.set_y(30)
        PDF.set_font("Times",style = 'B', size=15)
        PDF.multi_cell(w=PDF.epw,txt='Channel {}'.format(key),border=0,align='C')
        PDF.image(val, 20, 40, 300)
        if i!=len(Images):
            PDF.add_page(format=(350,250)) 
        PDF.set_font("Times",style = '', size=11) 
        pass
            
        
    PDF.set_font("Times",style = '',size = 9)
    pass


def check_crc_pass_fail(PDF,eaxcid,ResultData,line_height):
    line_height = 5
    crc_pass = crc_fail = 0
    Header = ['Channel', 'Slot', 'CRC Passed', 'Bit Length']
    for lines in ResultData:
            if lines[2] == 'True':
                crc_pass+=1
            elif lines[2] == 'False':
                crc_fail+=1
    PDF.set_y(30)
    PDF.set_font("Times",style = 'B', size=15)
    PDF.multi_cell(w=PDF.epw,txt='Channel {} CRC Table'.format(eaxcid),border=0,align='C')
    PDF.ln(10)
    render_header(PDF, Header, line_height, PDF.epw / len(Header))
    PDF.set_font("Times",style = '', size=11)
    render_table_data(PDF, ResultData[1:], line_height, PDF.epw / len(Header), Header)
    PDF.ln(10)
    PDF.set_font("Times",style = 'B', size=15)
    PDF.multi_cell(w=PDF.epw,txt='CRC PASS : {0} || CRC FAIL : {1}'.format(crc_pass,crc_fail),border=0,align='C')
    PDF.set_font("Times",style = '', size=11)
    pass

def check_ul_crc_pass_fail(PDF,eaxcid,ResultData):
    crc_pass = crc_fail = 0
    PDF.set_y(30)
    PDF.set_font("Times",style = 'B', size=15)
    PDF.multi_cell(w=PDF.epw,txt='Channel {} CRC Table'.format(eaxcid),border=0,align='C')
    PDF.ln(10)
    PDF.set_font("Times",style = '', size=11)
    for val in ResultData:
        PDF.write(h=5,txt=val)
        PDF.ln(5)
        if 'CRC=Fail' in val:
            crc_fail+=1
        elif 'CRC=Pass' in val:
            crc_pass +=1
    PDF.ln(10)
    PDF.set_font("Times",style = 'B', size=15)
    PDF.multi_cell(w=PDF.epw,txt='CRC PASS : {0} || CRC FAIL : {1}'.format(crc_pass,crc_fail),border=0,align='C')
    PDF.set_font("Times",style = '', size=11)

def genrate_report(Result,report_path, crc_data,ul_result,ul_crc_data):
    PDF = PDF_CAP()
    PDF.add_page(format=(350, 250))
    PDF.set_font("Times", size=12)
    PDF.set_font_size(float(10))
    Header_H = PDF.font_size * 2.5
    line_height = PDF.font_size * 3.5
    print(line_height)

    

    ##################################################################################################################
    #                                                   Downlink Data                                                  #
    ##################################################################################################################
    images = {}
    for data in Result:
        file_status = os.path.exists(data[-1])
        if file_status:
            images[data[0]] = data[-1]
        data.pop()
    print('\n\n\n')
    HEADING(PDF, '\n Downlink Report - Test results: \n')
    Header = ['Channel No', 'Channel Frequency [GHz]', 'BS Channel Bandwidth BW [MHz]',
                'Measured EVM (RMS) [%]', 'EVM Limit [%]', 'Output Power [dbm]', 'Limit Low [dBm]', 'High Low [dBm]', 'Verdict']
    Test_HEADING(PDF, '''Test purpose : \nThe test purpose is to verify the DL Test''')
    Test_HEADING(PDF, 'Test environment : \nNormal test conditions.')
    # print(tabulate(Result[2], headers=Header, stralign='left',maxcolwidths=[10, 10, 10, 10, 10, 10, 10], tablefmt='fancy_grid'))
    PDF.set_font("Times",style = '',size = 11)
    render_header(PDF, Header, line_height, PDF.epw / len(Header))
    print(Result)
    render_table_data(PDF, Result, line_height, PDF.epw / len(Header), Header)
    PDF.add_page(format=(350, 250))
    # print('crc_data',crc_data)
    i = 0 
    for key,val in crc_data.items():
        i+=1
        check_crc_pass_fail(PDF,key,val,line_height)
        if i<len(crc_data):
            PDF.add_page(format=(350, 250))
    # CRC_Header = ['Channel', 'Slot', 'CRC Passed', 'Bit Length']
    # crc_data = fetch_crc()
    print(images)
    if len(images)>0: 
        add_image(PDF,images)
    else:
        print('Screenshot didn\'t capture for Measured EVM..')

    ##################################################################################################################
    #                                                   Uplink Data                                                  #
    ##################################################################################################################
    ul_images = {}
    for data in ul_result:
        image_name_1 = f'{data[-1]}/VSA_Screenshot_1'
        image_name_2 = f'{data[-1]}/VSA_Screenshot_2'
        file_status = os.path.exists(image_name_1)
        file_status_2 = os.path.exists(image_name_2)
        if file_status and file_status_2:
            ul_images[data[0]] = [image_name_1,image_name_2]
        data.pop()
    PDF.add_page(format=(350, 250))
    HEADING(PDF, '\n Uplink - Test results: \n')
    UL_Header = ['Channel No', 'Channel Frequency [GHz]', 'BS Channel Bandwidth BW [MHz]',
                'Measured EVM (RMS) [%]', 'EVM Limit [%]','Verdict']
    Test_HEADING(PDF, '''Test purpose : \nThe test purpose is to verify the UL Test''')
    Test_HEADING(PDF, 'Test environment : \nNormal test conditions.')
    # print(tabulate(Result[2], headers=Header, stralign='left',maxcolwidths=[10, 10, 10, 10, 10, 10, 10], tablefmt='fancy_grid'))
    render_header(PDF, UL_Header, line_height, PDF.epw / len(UL_Header))
    print(Result)
    render_table_data(PDF, ul_result, line_height, PDF.epw / len(UL_Header), UL_Header)
    PDF.add_page(format=(350, 250))
    # print('ul_crc_data',ul_crc_data)
    i = 0
    for key,val in ul_crc_data.items():
        i+=1
        check_ul_crc_pass_fail(PDF,key,val)
        if i<len(crc_data):
            PDF.add_page(format=(350, 250))

    print(ul_images)
    if len(ul_images)>0: 
        add_ul_image(PDF,ul_images)
    else:
        print('Screenshot didn\'t capture for UL Measured EVM..')
    PDF.output(f"{report_path}")



if __name__ == "__main__":
    report_path = '/home/vvdn/DL_report.pdf'
    # Result = ({'1': ['1', '3.700005', '100', '2.01', '2.5', '22.42', '21.5', '25', '/home/vvdn/Videos/AUTOMATION/ORAN-Automation/CI_CD/QA_Testing/CUPLANE/TDD/Results/Base_DL_UL/EAXCID1/VXT_capture.png']}, 
    #           {'1': ['1', '3.700005', '100', '1.9514238834381104', '2.5','/home/vvdn/Videos/AUTOMATION/ORAN-Automation/CI_CD/QA_Testing/CUPLANE/TDD/Results/Base_DL_UL/EAXCID1']}, 
    #           {'1': [['#6317395Channel', 'Slot', 'CRC Passed', 'Bit Length'], ['PDSCH 1', '0', 'True', '84240'], ['PDSCH 1', '1', 'True', '84240'], ['PDSCH 1', '2', 'True', '84240'], ['PDSCH 1', '3', 'True', '84240'], ['PDSCH 1', '4', 'True', '84240'], ['PDSCH 1', '5', 'True', '84240'], ['PDSCH 1', '6', 'True', '84240'], ['PDSCH 1', '10', 'True', '84240'], ['PDSCH 1', '11', 'True', '84240'], ['PDSCH 1', '12', 'True', '84240'], ['PDSCH 1', '13', 'True', '84240'], ['PDSCH 1', '14', 'True', '84240'], ['PDSCH 1', '15', 'True', '84240'], ['PDSCH 1', '16', 'True', '84240'], ['PDSCH 2', '0', 'True', '792'], ['PDSCH 2', '1', 'True', '792'], ['PDSCH 2', '2', 'True', '792'], ['PDSCH 2', '3', 'True', '792'], ['PDSCH 2', '4', 'True', '792'], ['PDSCH 2', '5', 'True', '792'], ['PDSCH 2', '6', 'True', '792'], ['PDSCH 2', '10', 'True', '792'], ['PDSCH 2', '11', 'True', '792'], ['PDSCH 2', '12', 'True', '792'], ['PDSCH 2', '13', 'True', '792'], ['PDSCH 2', '14', 'True', '792'], ['PDSCH 2', '15', 'True', '792'], ['PDSCH 2', '16', 'True', '792'], ['PDSCH 3', '7', 'True', '35640'], ['PDSCH 3', '17', 'True', '35640'], ['PDSCH 4', '7', 'True', '252'], ['PDSCH 4', '17', 'True', '252'], ['PDCCH 1', '0', 'True', '108'], ['PDCCH 1', '1', 'True', '108'], ['PDCCH 1', '2', 'True', '108'], ['PDCCH 1', '3', 'True', '108'], ['PDCCH 1', '4', 'True', '108'], ['PDCCH 1', '5', 'True', '108'], ['PDCCH 1', '6', 'True', '108'], ['PDCCH 1', '7', 'True', '108'], ['PDCCH 1', '10', 'True', '108'], ['PDCCH 1', '11', 'True', '108'], ['PDCCH 1', '12', 'True', '108'], ['PDCCH 1', '13', 'True', '108'], ['PDCCH 1', '14', 'True', '108'], ['PDCCH 1', '15', 'True', '108'], ['PDCCH 1', '16', 'True', '108'], ['PDCCH 1', '17', 'True', '108']]}, 
    #           {'1': ['PUCCH Decoder : Off', 'PUSCH Decoder : On', 'PUSCH_0_IE : PUSCH Index=0, CarrierIndex=0, BWPIndex=0', 'PUSCH_F0_IE : Codeword=0, SlotIndex=08, RV Index=0, EffectiveCodeRate=0.6616, CRC=Pass , Number Of Code Blocks: 2', 'PUSCH_F1_IE : Codeword=0, SlotIndex=09, RV Index=0, EffectiveCodeRate=0.6616, CRC=Pass , Number Of Code Blocks: 2', 'PUSCH_F2_IE : Codeword=0, SlotIndex=18, RV Index=0, EffectiveCodeRate=0.6616, CRC=Pass , Number Of Code Blocks: 2', 'PUSCH_F3_IE : Codeword=0, SlotIndex=19, RV Index=0, EffectiveCodeRate=0.6616, CRC=Pass , Number Of Code Blocks: 2', 'PUSCH_1_IE : PUSCH Index=1, CarrierIndex=0, BWPIndex=0', 'PUSCH_F4_IE : Codeword=0, SlotIndex=07, RV Index=0, EffectiveCodeRate=0.6776, CRC=Pass , Number Of Code Blocks: 1', 'PUSCH_F5_IE : Codeword=0, SlotIndex=17, RV Index=0, EffectiveCodeRate=0.6776, CRC=Pass , Number Of Code Blocks: 1']})
    Result = ({'1': ['1', '3.700005', '100', '2.20', '2.5', '7.79', '21.5', '25', 'Pass', '/home/vvdn/Videos/AUTOMATION/ORAN-Automation/CI_CD/QA_Testing/CUPLANE/TDD/Results/Base_DL_UL/EAXCID1/VXT_capture.png'], 
               '2': ['2', '3.700005', '100', '2.05', '2.5', '8.02', '21.5', '25', 'Pass', '/home/vvdn/Videos/AUTOMATION/ORAN-Automation/CI_CD/QA_Testing/CUPLANE/TDD/Results/Base_DL_UL/EAXCID2/VXT_capture.png']}, 
              {'1': ['1', '3.700005', '100', '1.9527125358581543', '2.5', 'Pass', '/home/vvdn/Videos/AUTOMATION/ORAN-Automation/CI_CD/QA_Testing/CUPLANE/TDD/Results/Base_DL_UL/EAXCID1'], 
               '2': ['2', '3.700005', '100', '1.9527125358581543', '2.5', 'Pass', '/home/vvdn/Videos/AUTOMATION/ORAN-Automation/CI_CD/QA_Testing/CUPLANE/TDD/Results/Base_DL_UL/EAXCID2']}, 
              {'1': [['#6317395Channel', 'Slot', 'CRC Passed', 'Bit Length'], ['PDSCH 1', '0', 'True', '84240'], ['PDSCH 1', '1', 'True', '84240'], ['PDSCH 1', '2', 'True', '84240'], ['PDSCH 1', '3', 'True', '84240'], ['PDSCH 1', '4', 'True', '84240'], ['PDSCH 1', '5', 'True', '84240'], ['PDSCH 1', '6', 'True', '84240'], ['PDSCH 1', '10', 'True', '84240'], ['PDSCH 1', '11', 'True', '84240'], ['PDSCH 1', '12', 'True', '84240'], ['PDSCH 1', '13', 'True', '84240'], ['PDSCH 1', '14', 'True', '84240'], ['PDSCH 1', '15', 'True', '84240'], ['PDSCH 1', '16', 'True', '84240'], ['PDSCH 2', '0', 'True', '792'], ['PDSCH 2', '1', 'True', '792'], ['PDSCH 2', '2', 'True', '792'], ['PDSCH 2', '3', 'True', '792'], ['PDSCH 2', '4', 'True', '792'], ['PDSCH 2', '5', 'True', '792'], ['PDSCH 2', '6', 'True', '792'], ['PDSCH 2', '10', 'True', '792'], ['PDSCH 2', '11', 'True', '792'], ['PDSCH 2', '12', 'True', '792'], ['PDSCH 2', '13', 'True', '792'], ['PDSCH 2', '14', 'True', '792'], ['PDSCH 2', '15', 'True', '792'], ['PDSCH 2', '16', 'True', '792'], ['PDSCH 3', '7', 'True', '35640'], ['PDSCH 3', '17', 'True', '35640'], ['PDSCH 4', '7', 'True', '252'], ['PDSCH 4', '17', 'True', '252'], ['PDCCH 1', '0', 'True', '108'], ['PDCCH 1', '1', 'True', '108'], ['PDCCH 1', '2', 'True', '108'], ['PDCCH 1', '3', 'True', '108'], ['PDCCH 1', '4', 'True', '108'], ['PDCCH 1', '5', 'True', '108'], ['PDCCH 1', '6', 'True', '108'], ['PDCCH 1', '7', 'True', '108'], ['PDCCH 1', '10', 'True', '108'], ['PDCCH 1', '11', 'True', '108'], ['PDCCH 1', '12', 'True', '108'], ['PDCCH 1', '13', 'True', '108'], ['PDCCH 1', '14', 'True', '108'], ['PDCCH 1', '15', 'True', '108'], ['PDCCH 1', '16', 'True', '108'], ['PDCCH 1', '17', 'True', '108']], 
               '2': [['#6317395Channel', 'Slot', 'CRC Passed', 'Bit Length'], ['PDSCH 1', '0', 'True', '84240'], ['PDSCH 1', '1', 'True', '84240'], ['PDSCH 1', '2', 'True', '84240'], ['PDSCH 1', '3', 'True', '84240'], ['PDSCH 1', '4', 'True', '84240'], ['PDSCH 1', '5', 'True', '84240'], ['PDSCH 1', '6', 'True', '84240'], ['PDSCH 1', '10', 'True', '84240'], ['PDSCH 1', '11', 'True', '84240'], ['PDSCH 1', '12', 'True', '84240'], ['PDSCH 1', '13', 'True', '84240'], ['PDSCH 1', '14', 'True', '84240'], ['PDSCH 1', '15', 'True', '84240'], ['PDSCH 1', '16', 'True', '84240'], ['PDSCH 2', '0', 'True', '792'], ['PDSCH 2', '1', 'True', '792'], ['PDSCH 2', '2', 'True', '792'], ['PDSCH 2', '3', 'True', '792'], ['PDSCH 2', '4', 'True', '792'], ['PDSCH 2', '5', 'True', '792'], ['PDSCH 2', '6', 'True', '792'], ['PDSCH 2', '10', 'True', '792'], ['PDSCH 2', '11', 'True', '792'], ['PDSCH 2', '12', 'True', '792'], ['PDSCH 2', '13', 'True', '792'], ['PDSCH 2', '14', 'True', '792'], ['PDSCH 2', '15', 'True', '792'], ['PDSCH 2', '16', 'True', '792'], ['PDSCH 3', '7', 'True', '35640'], ['PDSCH 3', '17', 'True', '35640'], ['PDSCH 4', '7', 'True', '252'], ['PDSCH 4', '17', 'True', '252'], ['PDCCH 1', '0', 'True', '108'], ['PDCCH 1', '1', 'True', '108'], ['PDCCH 1', '2', 'True', '108'], ['PDCCH 1', '3', 'True', '108'], ['PDCCH 1', '4', 'True', '108'], ['PDCCH 1', '5', 'True', '108'], ['PDCCH 1', '6', 'True', '108'], ['PDCCH 1', '7', 'True', '108'], ['PDCCH 1', '10', 'True', '108'], ['PDCCH 1', '11', 'True', '108'], ['PDCCH 1', '12', 'True', '108'], ['PDCCH 1', '13', 'True', '108'], ['PDCCH 1', '14', 'True', '108'], ['PDCCH 1', '15', 'True', '108'], ['PDCCH 1', '16', 'True', '108'], ['PDCCH 1', '17', 'True', '108']]}, 
              {'1': ['PUCCH Decoder : Off', 'PUSCH Decoder : On', 'PUSCH_0_IE : PUSCH Index=0, CarrierIndex=0, BWPIndex=0', 'PUSCH_F0_IE : Codeword=0, SlotIndex=08, RV Index=0, EffectiveCodeRate=0.6616, CRC=Pass , Number Of Code Blocks: 2', 'PUSCH_F1_IE : Codeword=0, SlotIndex=09, RV Index=0, EffectiveCodeRate=0.6616, CRC=Pass , Number Of Code Blocks: 2', 'PUSCH_F2_IE : Codeword=0, SlotIndex=18, RV Index=0, EffectiveCodeRate=0.6616, CRC=Pass , Number Of Code Blocks: 2', 'PUSCH_F3_IE : Codeword=0, SlotIndex=19, RV Index=0, EffectiveCodeRate=0.6616, CRC=Pass , Number Of Code Blocks: 2', 'PUSCH_1_IE : PUSCH Index=1, CarrierIndex=0, BWPIndex=0', 'PUSCH_F4_IE : Codeword=0, SlotIndex=07, RV Index=0, EffectiveCodeRate=0.6776, CRC=Pass , Number Of Code Blocks: 1', 'PUSCH_F5_IE : Codeword=0, SlotIndex=17, RV Index=0, EffectiveCodeRate=0.6776, CRC=Pass , Number Of Code Blocks: 1'], 
               '2': ['PUCCH Decoder : Off', 'PUSCH Decoder : On', 'PUSCH_0_IE : PUSCH Index=0,CarrierIndex=0, BWPIndex=0', 'PUSCH_F0_IE : Codeword=0, SlotIndex=08, RV Index=0, EffectiveCodeRate=0.6616, CRC=Pass , Number Of Code Blocks: 2', 'PUSCH_F1_IE : Codeword=0, SlotIndex=09, RV Index=0, EffectiveCodeRate=0.6616, CRC=Pass , Number Of Code Blocks: 2', 'PUSCH_F2_IE : Codeword=0, SlotIndex=18, RV Index=0, EffectiveCodeRate=0.6616, CRC=Pass , Number Of Code Blocks: 2', 'PUSCH_F3_IE : Codeword=0, SlotIndex=19, RV Index=0, EffectiveCodeRate=0.6616, CRC=Pass , Number Of Code Blocks: 2', 'PUSCH_1_IE : PUSCH Index=1, CarrierIndex=0, BWPIndex=0', 'PUSCH_F4_IE : Codeword=0, SlotIndex=07, RV Index=0, EffectiveCodeRate=0.6776, CRC=Pass , Number Of Code Blocks: 1', 'PUSCH_F5_IE : Codeword=0, SlotIndex=17, RV Index=0, EffectiveCodeRate=0.6776, CRC=Pass , Number Of Code Blocks: 1']})
    
    ({'1': ['1', '3.700005', '100', '2.43', '2.5', '23.08', '21.5', '25', 'PASS', 'C:\\ORAN_AUTOMATION\\CUPLANE\\TDD\\Results\\Base_DL_UL\\EAXCID1\\VXT_capture.png'], 
        '2': ['2', '3.700005', '100', '2.01', '2.5', '23.31', '21.5', '25', 'PASS', 'C:\\ORAN_AUTOMATION\\CUPLANE\\TDD\\Results\\Base_DL_UL\\EAXCID2\\VXT_capture.png']}, 
        {'1': ['1', '3.700005', '100', 0, '2.5', 'Fail', 'C:\\ORAN_AUTOMATION\\CUPLANE\\TDD\\Results\\{0}\\EAXCID{1}'], 
        '2': ['2', '3.700005', '100', 0, '2.5', 'Fail', 'C:\\ORAN_AUTOMATION\\CUPLANE\\TDD\\Results\\{0}\\EAXCID{1}']}, 
        {'1': [['#6317395Channel', 'Slot', 'CRC Passed', 'Bit Length'], ['PDSCH 1', '0', 'True', '84240'], ['PDSCH 1', '1', 'True', '84240'], ['PDSCH 1', '2', 'True', '84240'], ['PDSCH 1', '3', 'True', '84240'], ['PDSCH 1', '4', 'True', '84240'], ['PDSCH 1', '5', 'True', '84240'], ['PDSCH 1', '6', 'True', '84240'], ['PDSCH 1', '10', 'True', '84240'], ['PDSCH 1', '11', 'True', '84240'], ['PDSCH 1', '12', 'True', '84240'], ['PDSCH 1', '13', 'True', '84240'], ['PDSCH 1', '14', 'True', '84240'], ['PDSCH 1', '15', 'True', '84240'], ['PDSCH 1', '16', 'True', '84240'], ['PDSCH 2', '0', 'True', '792'], ['PDSCH 2', '1', 'True', '792'], ['PDSCH 2', '2', 'True', '792'], ['PDSCH 2', '3', 'True', '792'], ['PDSCH 2', '4', 'True', '792'], ['PDSCH 2', '5', 'True', '792'], ['PDSCH 2', '6', 'True', '792'], ['PDSCH 2', '10', 'True', '792'], ['PDSCH 2', '11', 'True', '792'], ['PDSCH 2', '12', 'True', '792'], ['PDSCH 2', '13', 'True', '792'], ['PDSCH 2', '14', 'True', '792'], ['PDSCH 2', '15', 'True', '792'], ['PDSCH 2', '16', 'True', '792'], ['PDSCH 3', '7', 'True', '35640'], ['PDSCH 3', '17', 'True', '35640'], ['PDSCH 4', '7', 'True', '252'], ['PDSCH 4', '17', 'True', '252'], ['PDCCH 1', '0', 'True', '108'], ['PDCCH 1', '1', 'True', '108'], ['PDCCH 1', '2', 'True', '108'], ['PDCCH 1', '3', 'True', '108'], ['PDCCH 1', '4', 'True', '108'], ['PDCCH 1', '5', 'True', '108'], ['PDCCH 1', '6', 'True', '108'], ['PDCCH 1', '7', 'True', '108'], ['PDCCH 1', '10', 'True', '108'], ['PDCCH 1', '11', 'True', '108'], ['PDCCH 1', '12', 'True', '108'], ['PDCCH 1', '13', 'True', '108'], ['PDCCH 1', '14', 'True', '108'], ['PDCCH 1', '15', 'True', '108'], ['PDCCH 1', '16', 'True', '108'], ['PDCCH 1', '17', 'True', '108']], 
        '2': [['#6317395Channel', 'Slot', 'CRC Passed', 'Bit Length'], ['PDSCH 1', '0', 'True', '84240'], ['PDSCH 1', '1', 'True', '84240'], ['PDSCH 1', '2', 'True', '84240'], ['PDSCH 1', '3', 'True', '84240'], ['PDSCH 1', '4', 'True', '84240'], ['PDSCH 1', '5', 'True', '84240'], ['PDSCH 1', '6', 'True', '84240'], ['PDSCH 1', '10', 'True', '84240'], ['PDSCH 1', '11', 'True', '84240'], ['PDSCH 1', '12', 'True', '84240'], ['PDSCH 1', '13', 'True', '84240'], ['PDSCH 1', '14', 'True', '84240'], ['PDSCH 1', '15', 'True', '84240'], ['PDSCH 1', '16', 'True', '84240'], ['PDSCH 2', '0', 'True', '792'], ['PDSCH 2', '1', 'True', '792'], ['PDSCH 2', '2', 'True', '792'], ['PDSCH 2', '3', 'True', '792'], ['PDSCH 2', '4', 'True', '792'], ['PDSCH 2', '5', 'True', '792'], ['PDSCH 2', '6', 'True', '792'], ['PDSCH 2', '10', 'True', '792'], ['PDSCH 2', '11', 'True', '792'], ['PDSCH 2', '12', 'True', '792'], ['PDSCH 2', '13', 'True', '792'], ['PDSCH 2', '14', 'True', '792'], ['PDSCH 2', '15', 'True', '792'], ['PDSCH 2', '16', 'True', '792'], ['PDSCH 3', '7', 'True', '35640'], ['PDSCH 3', '17', 'True', '35640'], ['PDSCH 4', '7', 'True', '252'], ['PDSCH 4', '17', 'True', '252'], ['PDCCH 1', '0', 'True', '108'], ['PDCCH 1', '1', 'True', '108'], ['PDCCH 1', '2', 'True', '108'], ['PDCCH 1', '3', 'True', '108'], ['PDCCH 1', '4', 'True', '108'], ['PDCCH 1', '5', 'True', '108'], ['PDCCH 1', '6', 'True', '108'], ['PDCCH 1', '7', 'True', '108'], ['PDCCH 1', '10', 'True', '108'], ['PDCCH 1', '11', 'True', '108'], ['PDCCH 1', '12', 'True', '108'], ['PDCCH 1', '13', 'True', '108'], ['PDCCH 1', '14', 'True', '108'], ['PDCCH 1', '15', 'True', '108'], ['PDCCH 1', '16', 'True', '108'], ['PDCCH 1', '17', 'True', '108']]}, 
        {'1': ['PUCCH Decoder : Off', 'PUSCH Decoder : On', 'PUSCH_0_IE : PUSCH Index=0, CarrierIndex=0, BWPIndex=0', 'PUSCH_F0_IE : Codeword=0, SlotIndex=08, RV Index=0, EffectiveCodeRate=0.6616, CRC=Pass , Number Of Code Blocks: 2', 'PUSCH_F1_IE : Codeword=0, SlotIndex=09, RV Index=0, EffectiveCodeRate=0.6616, CRC=Pass , Number Of Code Blocks: 2', 'PUSCH_F2_IE : Codeword=0, SlotIndex=18, RV Index=0, EffectiveCodeRate=0.6616, CRC=Pass , Number Of Code Blocks: 2', 'PUSCH_F3_IE : Codeword=0, SlotIndex=19, RV Index=0, EffectiveCodeRate=0.6616, CRC=Pass , Number Of Code Blocks: 2', 'PUSCH_1_IE : PUSCH Index=1, CarrierIndex=0, BWPIndex=0', 'PUSCH_F4_IE : Codeword=0, SlotIndex=07, RV Index=0, EffectiveCodeRate=0.6776, CRC=Pass , Number Of Code Blocks: 1', 'PUSCH_F5_IE : Codeword=0, SlotIndex=17, RV Index=0, EffectiveCodeRate=0.6776, CRC=Pass , Number Of Code Blocks: 1'], 
        '2': ['PUCCH Decoder : Off', 'PUSCH Decoder : On']})
    genrate_report(list(Result[0].values()),report_path,Result[2],list(Result[1].values()),Result[3])