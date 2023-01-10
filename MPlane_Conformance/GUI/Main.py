########################################################################
## IMPORTS
########################################################################
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication , QWidget, QLabel
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QMovie
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtGui import QIcon,QFont
import sys, time
import os
from PyQt5 import QtWidgets, QtCore, QtGui
import ipaddress, subprocess
from configparser import ConfigParser


########################################################################
# IMPORT GUI FILE
########################################################################

dir_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(dir_path)
sys.path.append(dir_path)
from GUI.Home_2 import Ui_MainWindow
from GUI.run_all import Ui_Run_ALL
from require.Write_Data import WriteData
########################################################################

###############################################################################
## For reading data from .ini file
###############################################################################
configur = ConfigParser()
try:
    configur.read('{}/Conformance/inputs.ini'.format(dir_path))
except Exception as e:
    print(e)
########################################################################
## MAIN WINDOW CLASS
########################################################################

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self,dir_name):
        QtWidgets.QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.window = QtWidgets.QMainWindow()
        self.testCaseUI = Ui_Run_ALL()
        self.window.setWindowFlag(QtCore.Qt.WindowMinMaxButtonsHint, False)
        self.testCaseUI.setupUi(self.window)
        self.clicked_module = ''
        self.directory = dir_name
        ##############################################################################
        ## Check boxes module wise
        ##############################################################################
        self.checkboxs_1 = [self.ui.TC_001, self.ui.TC_002, self.ui.TC_003]
        self.checkboxs_3 = [self.ui.TC_008, self.ui.TC_009]
        self.checkboxs_4 = [self.ui.TC_010, self.ui.TC_011]
        self.checkboxs_5 = [self.ui.TC_012, self.ui.TC_013]
        self.checkboxs_6 = [self.ui.TC_014, self.ui.TC_015, self.ui.TC_016, self.ui.TC_017,]
        self.checkboxs_7 = [self.ui.TC_018, self.ui.TC_019, self.ui.TC_020, self.ui.TC_021, self.ui.TC_022, self.ui.TC_023]
        self.checkboxs_8 = [self.ui.TC_026, self.ui.TC_027]

        ##############################################################################
        ## if clicked on submit button on each module widget
        ##############################################################################
        self.ui.submitBtn.clicked.connect(self.transport_handshake)
        self.ui.submitBtn_2.clicked.connect(self.subscription)
        self.ui.submitBtn_3.clicked.connect(self.supervision)
        self.ui.submitBtn_4.clicked.connect(self.ru_info)
        self.ui.submitBtn_5.clicked.connect(self.fault_mgmt)
        self.ui.submitBtn_6.clicked.connect(self.sw_mgmt)
        self.ui.submitBtn_7.clicked.connect(self.access_control)
        self.ui.submitBtn_8.clicked.connect(self.ru_configure)
        # self.ui.submitBtn_10.clicked.connect(self.log_mgmt)
        self.testCaseUI.submitBtn.clicked.connect(lambda : self.get_all_data_and_run(self.testCaseUI.consoleEdit))
        self.testCaseUI.runBtn.clicked.connect(lambda : self.Loading_2('Test_Suit',self.testCaseUI.consoleEdit))


        ##############################################################################
        ## if clicked on run button on each module widget
        ##############################################################################
        self.ui.runButton.clicked.connect(lambda: self.Loading(self.checkboxs_1,self.ui.consoleEdit,self.transport_handshake))
        self.ui.runButton_2.clicked.connect(lambda: self.Loading(['M_CTC_ID_007'],self.ui.consoleEdit_2,self.subscription))
        # self.ui.runButton_2.clicked.connect(lambda: self.Loading_1())        
        self.ui.runButton_3.clicked.connect(lambda: self.Loading(self.checkboxs_3,self.ui.consoleEdit_3,self.supervision))
        self.ui.runButton_4.clicked.connect(lambda: self.Loading(self.checkboxs_4,self.ui.consoleEdit_4,self.ru_info))
        self.ui.runButton_5.clicked.connect(lambda: self.Loading(self.checkboxs_5,self.ui.consoleEdit_5,self.fault_mgmt))
        self.ui.runButton_6.clicked.connect(lambda: self.Loading(self.checkboxs_6,self.ui.consoleEdit_6,self.sw_mgmt))
        self.ui.runButton_7.clicked.connect(lambda: self.Loading(self.checkboxs_7,self.ui.consoleEdit_7,self.access_control))
        self.ui.runButton_8.clicked.connect(lambda: self.Loading(self.checkboxs_8,self.ui.consoleEdit_8,self.ru_configure))
        self.ui.runBtn.clicked.connect(lambda: self.Loading(['M_CTC_ID_034'],self.ui.consoleEdit_10,self.log_mgmt))

        ##############################################################################
        ## if clicked on run all button on each module widget
        ##############################################################################
        self.ui.run_89.clicked.connect(lambda: self.Loading_1(['/Module/module_3'],self.ui.consoleEdit_3,self.supervision))
        self.ui.run_10_11.clicked.connect(lambda: self.Loading_1(['/Module/module_4'],self.ui.consoleEdit_4,self.ru_info))
        self.ui.run_12_13.clicked.connect(lambda: self.Loading_1(['/Module/module_5'],self.ui.consoleEdit_5,self.fault_mgmt))
        self.ui.run_14_17.clicked.connect(lambda: self.Loading_1(['/Module/module_6'],self.ui.consoleEdit_6,self.sw_mgmt))
        self.ui.run_18_23.clicked.connect(lambda: self.Loading_1(['/Module/module_7'],self.ui.consoleEdit_7,self.access_control))
        self.ui.run_26_27.clicked.connect(lambda: self.Loading_1(['/Module/module_8'],self.ui.consoleEdit_8,self.ru_configure))
        self.ui.run_all.clicked.connect(self.window.showMaximized)
            
        ##############################################################################
        ## Restart DHCP server
        ##############################################################################
        self.ui.dhcp_restart.clicked.connect(lambda: self.dhcp_restarted(Flag = False))
        self.ui.dhcp_restart_base.clicked.connect(lambda: self.dhcp_restarted(Flag = True))

        ##############################################################################
        ## Restart DHCP server
        ##############################################################################
        
        self.ui.report.clicked.connect(lambda : self.show_report())
        
        

        ##############################################################################
        ## if clicked on module new side window will open
        ##############################################################################
        ## Module 1
        self.ui.module.clicked.connect(lambda: self.onclick_modules(self.ui.module,self.ui.Module1))
        ## Module 2
        self.ui.module_1.clicked.connect(lambda: self.onclick_modules(self.ui.module_1,self.ui.Module2))
        ## Module 3
        self.ui.module_2.clicked.connect(lambda: self.onclick_modules(self.ui.module_2,self.ui.Module3))
        ## Module 4
        self.ui.module_3.clicked.connect(lambda: self.onclick_modules(self.ui.module_3,self.ui.Module4))
        ## Module 5
        self.ui.module_4.clicked.connect(lambda: self.onclick_modules(self.ui.module_4,self.ui.Module5))
        ## Module 6
        self.ui.module_5.clicked.connect(lambda: self.onclick_modules(self.ui.module_5,self.ui.Module6))
        ## Module 7
        self.ui.module_6.clicked.connect(lambda: self.onclick_modules(self.ui.module_6,self.ui.Module7))
        ## Module 8
        self.ui.module_7.clicked.connect(lambda: self.onclick_modules(self.ui.module_7,self.ui.Module8))
        ## Module 9
        self.ui.module_8.clicked.connect(lambda: self.onclick_modules(self.ui.module_8,self.ui.Module9))
        ## Module 10
        self.ui.module_9.clicked.connect(lambda: self.onclick_modules(self.ui.module_9,self.ui.Module10))

        self.ui.menu.clicked.connect(lambda: self.slideLeftMenu())
        self.showMaximized()


    def show_report(self):
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle('PopUp')
        msg.resize(600,100)
        msg.setWindowTitle('PopUp')
        msg.setText('Logs are saved at {}.'.format(self.directory))
        msg.exec_()

    def dhcp_restarted(self, Flag):
        self.msg = QtWidgets.QMessageBox()
        self.msg.setWindowTitle('PopUp')
        self.msg.resize(1133,100)
        self.Flag = Flag
        if Flag:
            self.result = os.popen("python {}/require/{}.py".format(dir_path,'DHCP_CONF_BASE')).read()
            print(self.result)
            self.dhcp_handle_stdout()
            self.dhcp_process_finished()
        else:
            self.dhcp_process_finished()
        return True

    def dhcp_process_finished(self):
            if not self.Flag:
                os.system('sudo /etc/init.d/isc-dhcp-server restart')
            st = subprocess.getoutput('sudo /etc/init.d/isc-dhcp-server status')
            self.msg.setText('{}'.format(st))
            self.msg.exec_()
            time.sleep(2)
            if 'running' in st:
                self.msg.setText('Please reboot RU once..')
                self.msg.exec_()


    def dhcp_handle_stdout(self):
        print('Base Conf are done.')
        self.msg.setText(self.result)
        self.msg.exec_()
        # print(self.result)
        self.link_detect = True
        if 'SFP is not Connected' in self.result:
            self.link_detect = False
            return False
        else:
            return True


    ########################################################################
    # Slide left menu function
    ########################################################################
    def slideLeftMenu(self):
        # Get current left menu width
        width = self.ui.sideMenu_Frame.width()
        
        # If minimized
        if width == 0:
            # Expand menu
            newWidth = 200
            self.ui.menu.setIcon(QtGui.QIcon(u":/icons/icons/chevron-right.svg"))
        # If maximized
        else:
            # Restore menu
            newWidth = 0
            self.ui.menu.setIcon(QtGui.QIcon(u":/icons/icons/align-right.svg"))

        # Animate the transition
        self.animation = QtCore.QPropertyAnimation(self.ui.sideMenu_Frame, b"maximumWidth")#Animate minimumWidht
        self.animation.setDuration(250)
        self.animation.setStartValue(width)#Start value is the current menu width
        self.animation.setEndValue(newWidth)#end value is the new menu width
        self.animation.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
        self.animation.start()

    ########################################################################
    # Execution Frame
    ########################################################################
    def onclick_modules(self, module, model):
        # Get current left menu width
        width = self.ui.stackedWidget.maximumWidth()

        # If minimized
        print(model, self.clicked_module)
        if model == self.clicked_module:
            if width == 0:
                # Expand module
                newWidth = self.ui.centerScreen_frame.width()
                # module.setIcon(QtGui.QIcon(u":/icons/icons/chevron-right.svg"))
                self.ui.stackedWidget.setCurrentWidget(model)
            # If maximized
            else:
                # Restore module
                newWidth = 0
                module.setIcon(QtGui.QIcon(u""))
        
        else:
            self.clicked_module = model
            newWidth = self.ui.centerScreen_frame.width()
            # module.setIcon(QtGui.QIcon(u":/icons/icons/chevron-right.svg"))
            self.ui.stackedWidget.setCurrentWidget(model)

        # Animate the transition
        self.animation = QtCore.QPropertyAnimation(self.ui.stackedWidget, b"maximumWidth")#Animate minimumWidht
        self.animation.setDuration(350)
        self.animation.setStartValue(width)#Start value is the current menu width
        self.animation.setEndValue(newWidth)#end value is the new menu width
        self.animation.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
        self.animation.start()

    def Loading_2(self,test_cases,console):
        self.main_win = QWidget()
        self.verticalLayout = QtWidgets.QVBoxLayout(self.main_win)
        
        self.main_win.setFixedSize(200,200)
        self.label_ani= QLabel(self.main_win)
        self.movie=QMovie("{}/GUI/Loading_1.gif".format(dir_path))
        self.label_ani.setMovie(self.movie)
        self.verticalLayout.addWidget(self.label_ani, 0, QtCore.Qt.AlignHCenter)
        self.main_win.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.main_win.setAttribute(QtCore.Qt.WA_TranslucentBackground,on=True)
        self.startani()
        self.main_win.showMaximized()
        self.timer= QTimer(self.main_win)
        # self.timer.singleShot(1000,self.stopAni)
        if self.get_all_data_and_run(console):
            self.timer.singleShot(100,lambda: self.Run_All(test_cases,console))
        else:
            return False

    def Run_All(self,filename, console):
        self.console = console
        self.console.clear()
        self.message("Executing process")
        self.p = QtCore.QProcess()  # Keep a reference to the QProcess (e.g. on self) while it's running.
        if self.p:
            self.console.appendPlainText('+'*100)
            self.p.start("python", ['{}/require/{}.py'.format(dir_path,filename)])
            self.p.readyReadStandardOutput.connect(self.handle_stdout)
            self.p.readyReadStandardError.connect(self.handle_stderr)
            self.p.stateChanged.connect(self.handle_state)
            self.p.finished.connect(self.process_finished)  # Clean up once complete.
        return True

    def checked_mul(self):
        self.data = ''
        for check in self.testCaseUI.checkboxes:
            if check.isChecked():
                self.data+= ' '+ check.text()[-2:]
            else:
                pass

    def get_all_data_and_run(self, console):
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle('PopUp')
        msg.resize(400,100)
        print(self.ui.username_2.text())
        print(self.ui.password_2.text())
        print(self.ui.paragon_ip.text())
        print(self.ui.ptpSyncE.text())
        data = {'SUDO_USER' : self.testCaseUI.input_01.text(), 'SUDO_PASS' : self.testCaseUI.input_02.text(),
            'NMS_USER' : self.testCaseUI.input_03.text(), 'NMS_PASS' : self.testCaseUI.input_04.text(),
            'FMPM_USER' : self.testCaseUI.input_05.text(), 'FMPM_PASS' : self.testCaseUI.input_06.text(), 
            'paragon_ip' : self.testCaseUI.input_07.text(),'ptpSyncEport' : self.testCaseUI.input_08.currentText(),
            'FH_Interface' : self.testCaseUI.input_09.text(),'bandwidth' : self.testCaseUI.input_10.currentText(),
            'tx_arfcn' : self.testCaseUI.input_11.text(),'rx_arfcn' : self.testCaseUI.input_12.text(),
            'tx_center_frequency' : self.testCaseUI.input_13.text(),'rx_center_frequency' : self.testCaseUI.input_14.text(),
            'duplex_scheme' : self.testCaseUI.input_16.currentText(),'scs_value' : self.testCaseUI.input_19.currentText(),
            'DU_PASS' : self.testCaseUI.input_15.text(), 'SW_PATH' : self.testCaseUI.input_17.text(), 'Currupt_Path' : self.testCaseUI.input_18.text()}
        self.checked_mul()
        data['Selected_Test_Case'] = str(self.data)
        for key, val in data.items():
            if val == '':
                msg.setText('Please Enter a valid value of {}'.format(key))
                msg.exec_()
                self.stopAni()
                return False
        else:
            if len(self.data) == 0:
                msg.setText('Please select the test case...')
                msg.exec_()
                self.stopAni()
                return False
            else:
                msg.setText('Success')
                msg.exec_()
        WriteData(data,'{}/Conformance/inputs.ini'.format(dir_path))
        console.clear()
        for key,val in data.items():
            console.appendPlainText('{} : {}'.format(key,val)) 
        msg.setText('Data appended successfully...')
        msg.exec_()
        return True

    ########################################################################
    # get data from each widget
    ########################################################################
    def transport_handshake(self):
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle('PopUp')
        msg.resize(400,100)
        print(self.ui.input.text())
        print(self.ui.input1.text())
        data = {'SUDO_USER' : self.ui.input1.text(), 'SUDO_PASS' : self.ui.input.text()}
        for key, val in data.items():
            if val == '':
                msg.setText('Please Enter a valid value of {}'.format(key))
                msg.exec_()
                try:
                    if self.movie():
                        self.stopAni()
                except Exception as e:
                    print(e)
                return False
        else:
            msg.setText('Success')
            msg.exec_()
        WriteData(data,'{}/Conformance/inputs.ini'.format(dir_path))
        self.ui.consoleEdit.clear()
        self.ui.consoleEdit.appendPlainText('SUDO_USER : {} \nSUDO_PASS :{}'.format(self.ui.input1.text(),self.ui.input.text()))  
        msg.setText('Data appended successfully...')
        msg.exec_()
        return True
        
    def subscription(self):
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle('PopUp')
        msg.resize(400,100)
        print(self.ui.username_2.text())
        print(self.ui.password_2.text())
        print(self.ui.paragon_ip.text())
        print(self.ui.ptpSyncE.text())
        data = {'SUDO_USER' : self.ui.username_2.text(), 'SUDO_PASS' : self.ui.password_2.text(), 
            'paragon_ip' : self.ui.paragon_ip.text(),'ptpSyncEport' : self.ui.ptpSyncE.text()}
        for key, val in data.items():
            if val == '':
                msg.setText('Please Enter a valid value of {}'.format(key))
                msg.exec_()
                return False
        else:
            msg.setText('Success')
            msg.exec_()
        WriteData(data,'{}/Conformance/inputs.ini'.format(dir_path))
        self.ui.consoleEdit_2.clear()
        for key,val in data.items():
            self.ui.consoleEdit_2.appendPlainText('{} : {}'.format(key,val)) 
        msg.setText('Data appended successfully...')
        msg.exec_()
        return True

    def supervision(self):
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle('PopUp')
        msg.resize(400,100)
        print(self.ui.username.text())
        print(self.ui.password.text())
        data = {'SUDO_USER' : self.ui.username.text(), 'SUDO_PASS' : self.ui.password.text()}
        for key, val in data.items():
            if val == '':
                msg.setText('Please Enter a valid value of {}'.format(key))
                msg.exec_()
                self.stopAni()
                return False
        else:
            msg.setText('Success')
            msg.exec_()
        WriteData(data,'{}/Conformance/inputs.ini'.format(dir_path))
        self.ui.consoleEdit_3.clear()
        for key,val in data.items():
            self.ui.consoleEdit_3.appendPlainText('{} : {}'.format(key,val)) 
        msg.setText('Data appended successfully...')
        msg.exec_()
        return True

    def ru_info(self):
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle('PopUp')
        msg.resize(400,100)
        print(self.ui.username_4.text())
        print(self.ui.password_4.text())
        data = {'SUDO_USER' : self.ui.username_4.text(), 'SUDO_PASS' : self.ui.password_4.text()}
        for key, val in data.items():
            if val == '':
                msg.setText('Please Enter a valid value of {}'.format(key))
                msg.exec_()
                self.stopAni()
                return False
        else:
            msg.setText('Success')
            msg.exec_()
        WriteData(data,'{}/Conformance/inputs.ini'.format(dir_path))
        self.ui.consoleEdit_4.clear()
        for key,val in data.items():
            self.ui.consoleEdit_4.appendPlainText('{} : {}'.format(key,val)) 
        msg.setText('Data appended successfully...')
        msg.exec_()
        return True

    def fault_mgmt(self):
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle('PopUp')
        msg.resize(400,100)
        print(self.ui.username_5.text())
        print(self.ui.password_5.text())
        print(self.ui.p_neoIP.text())
        print(self.ui.ptpPort.text())
        data = {'SUDO_USER' : self.ui.username_5.text(), 'SUDO_PASS' : self.ui.password_5.text(), 
            'paragon_ip' : self.ui.p_neoIP.text(),'ptpSyncEport' : self.ui.ptpPort.text()}
        for key, val in data.items():
            if val == '':
                msg.setText('Please Enter a valid value of {}'.format(key))
                msg.exec_()
                self.stopAni()
                return False
        else:
            msg.setText('Success')
            msg.exec_()
        WriteData(data,'{}/Conformance/inputs.ini'.format(dir_path))
        self.ui.consoleEdit_5.clear()
        for key,val in data.items():
            self.ui.consoleEdit_5.appendPlainText('{} : {}'.format(key,val)) 
        msg.setText('Data appended successfully...')
        msg.exec_()
        return True

    def sw_mgmt(self):
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle('PopUp')
        msg.resize(400,100)
        print(self.ui.username_6.text())
        print(self.ui.password_6.text())
        print(self.ui.du_pswrd.text())
        print(self.ui.sw_file.text())
        print(self.ui.currupt_file.text())
        data = {'SUDO_USER' : self.ui.username_6.text(), 'SUDO_PASS' : self.ui.password_6.text(),
                'DU_PASS' : self.ui.du_pswrd.text(), 'SW_PATH' : self.ui.sw_file.text(),
                'Currupt_Path' : self.ui.currupt_file.text()}
        for key, val in data.items():
            if val == '':
                msg.setText('Please Enter a valid value of {}'.format(key))
                msg.exec_()
                return False
        else:
            msg.setText('Success')
            msg.exec_()
        WriteData(data,'{}/Conformance/inputs.ini'.format(dir_path))
        self.ui.consoleEdit_6.clear()
        for key,val in data.items():
            self.ui.consoleEdit_6.appendPlainText('{} : {}'.format(key,val)) 
        msg.setText('Data appended successfully...')
        msg.exec_()
        return True

    def access_control(self):
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle('PopUp')
        msg.resize(400,100)
        print(self.ui.sudouser.text())
        print(self.ui.sudopswrd.text())
        print(self.ui.nmsuser.text())
        print(self.ui.nmspswrd.text())
        print(self.ui.fmpmuser.text())
        print(self.ui.fmpmpswrd.text())
        data = {'SUDO_USER' : self.ui.sudouser.text(), 'SUDO_PASS' : self.ui.sudopswrd.text(),
                'NMS_USER' : self.ui.nmsuser.text(), 'NMS_PASS' : self.ui.nmspswrd.text(),
                'FMPM_USER' : self.ui.fmpmuser.text(), 'FMPM_PASS' : self.ui.fmpmpswrd.text()}
        for key, val in data.items():
            if val == '':
                msg.setText('Please Enter a valid value of {}'.format(key))
                msg.exec_()
                self.stopAni()
                return False
        else:
            msg.setText('Success')
            msg.exec_()
        WriteData(data,'{}/Conformance/inputs.ini'.format(dir_path))
        self.ui.consoleEdit_7.clear()
        for key,val in data.items():
            self.ui.consoleEdit_7.appendPlainText('{} : {}'.format(key,val)) 
        msg.setText('Data appended successfully...')
        msg.exec_()
        return True

    def ru_configure(self):
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle('PopUp')
        msg.resize(400,100)
        # print(self.ui.sudouser_8.text())
        # print(self.ui.sudopswrd_8.text())
        print(self.ui.input8_3.currentText())
        data = {'SUDO_USER' : self.ui.sudouser_8.text(), 'SUDO_PASS' : self.ui.sudopswrd_8.text(),
                'FH_Interface' : self.ui.fronhaulInterface.text(),'bandwidth' : self.ui.input8_3.currentText(),
                'tx_arfcn' : self.ui.input8_1.text(),'rx_arfcn' : self.ui.input8_2.text(),
                'tx_center_frequency' : self.ui.input8_4.text(),'rx_center_frequency' : self.ui.input8_5.text(),
                'duplex_scheme' : self.ui.input8_6.currentText(),'scs_value' : self.ui.comboBox_1.currentText()}
        for key, val in data.items():
            if val == '':
                msg.setText('Please Enter a valid value of {}'.format(key))
                msg.exec_()
                self.stopAni()
                return False
        else:
            msg.setText('Success')
            msg.exec_()
        WriteData(data,'{}/Conformance/inputs.ini'.format(dir_path))
        self.ui.consoleEdit_8.clear()
        for key,val in data.items():
            self.ui.consoleEdit_8.appendPlainText('{} : {}'.format(key,val)) 
        msg.setText('Data appended successfully...')
        msg.exec_()
        # time.sleep(5)
        return True

    def log_mgmt(self):
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle('PopUp')
        msg.resize(400,100)
        print(self.ui.username_10.text())
        print(self.ui.password_10.text())
        print(self.ui.remote_path.text())
        data = {'SUDO_USER' : self.ui.username_10.text(), 'SUDO_PASS' : self.ui.password_10.text(),
                'file_download_path' : self.ui.remote_path.text()}
        for key, val in data.items():
            if val == '':
                msg.setText('Please Enter a valid value of {}'.format(key))
                msg.exec_()
                self.stopAni()
                return False
        else:
            msg.setText('Success')
            msg.exec_()
        WriteData(data,'{}/Conformance/inputs.ini'.format(dir_path))
        self.ui.consoleEdit_10.clear()
        for key,val in data.items():
            self.ui.consoleEdit_10.appendPlainText('{} : {}'.format(key,val)) 
        msg.setText('Data appended successfully...')
        msg.exec_()
        return True

    def checked(self,checkboxes,console,submitbtn):
        # self.ui.InputLabel.clear()
        flag_f = False
        self.data1 = []
        # print(checkboxes)
        try:
            for checkbox in checkboxes:
                if type(checkbox) == str:
                    self.data1.append(checkbox)
                    break
                if checkbox.isChecked() != True:
                    pass
                else:
                    flag_f =  True
                    self.data1.append(checkbox.text())

            if flag_f == False and type(checkbox) != str:
                self.data1.append(checkboxes[0].text())
            print(self.data1)
            # for testcase in self.data1:
                # self.start_process(testcase,console)
            if submitbtn():
                self.start_process(self.data1,console)
        except Exception as e:
            print(e)
            pass

    def message(self, s):
        self.console.appendPlainText(s)
   
    def validate_ip(self,ip_str):  
        try:  
            ip_obj = ipaddress.ip_address(ip_str)  
            print(f"The IP address {ip_obj} is valid")
            return True  
        except ValueError:  
            print(f"The IP address {ip_str} is not valid")
            return False

    def start_process(self,test_cases,console):
        # content = self.comboBox.currentText()
        self.console = console
        self.console.clear()
        self.message("Executing process")
        self.p = QtCore.QProcess()  # Keep a reference to the QProcess (e.g. on self) while it's running.
        self.console.appendPlainText('+'*100)
        for test_case in test_cases:
            self.p.start("python", ['{}/Conformance/{}.py'.format(dir_path,test_case)])
            self.p.readyReadStandardOutput.connect(self.handle_stdout)
            self.p.readyReadStandardError.connect(self.handle_stderr)
        self.p.stateChanged.connect(self.handle_state)
        self.p.finished.connect(self.process_finished)  # Clean up once complete.
    
    def run_module(self,test_cases,console,submitbtn):
        if submitbtn():
        # content = self.comboBox.currentText()
            self.console = console
            self.console.clear()
            self.message("Executing process")
            self.p = QtCore.QProcess()  # Keep a reference to the QProcess (e.g. on self) while it's running.
            self.console.appendPlainText('+'*100)
            for test_case in test_cases:
                self.p.start("python", ['{}/Conformance/{}.py'.format(dir_path,test_case)])
                self.p.readyReadStandardOutput.connect(self.handle_stdout)
                self.p.readyReadStandardError.connect(self.handle_stderr)
            self.p.stateChanged.connect(self.handle_state)
            self.p.finished.connect(self.process_finished)  # Clean up once complete.
            return True
        else:
            return False
            
    def handle_stderr(self):
        data = self.p.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        self.message(stderr)

    def handle_stdout(self):
        data = self.p.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        self.message(stdout)

    def handle_state(self, state):
        states = {
            QtCore.QProcess.NotRunning: 'Not running',
            QtCore.QProcess.Starting: 'Starting',
            QtCore.QProcess.Running: 'Running',
        }
        print(state,'state')
        state_name = states[state]
        self.message(f"State changed: {state_name}")

    def process_finished(self):
        self.message("Process finished.")
        self.stopAni()
        self.p = None
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle('PopUp')
        msg.resize(400,100)
        msg.setText('Logs are saved at {}.'.format(self.directory))
        msg.exec_()

    def Loading(self,checkboxes,console,submitbtn):
        self.main_win = QWidget()
        self.verticalLayout = QtWidgets.QVBoxLayout(self.main_win)
        
        self.main_win.setFixedSize(200,200)
        self.label_ani= QLabel(self.main_win)
        self.movie=QMovie("{}/GUI/Loading_1.gif".format(dir_path))
        self.label_ani.setMovie(self.movie)
        self.verticalLayout.addWidget(self.label_ani, 0, QtCore.Qt.AlignHCenter)
        self.main_win.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.main_win.setAttribute(QtCore.Qt.WA_TranslucentBackground,on=True)
        self.startani()
        self.main_win.showMaximized()
        self.timer= QTimer(self.main_win)
        # self.timer.singleShot(1000,self.stopAni)
        self.timer.singleShot(100,lambda: self.checked(checkboxes,console,submitbtn))

    
    def Loading_1(self,test_cases,console,submitbtn):
        self.main_win = QWidget()
        self.verticalLayout = QtWidgets.QVBoxLayout(self.main_win)
        
        self.main_win.setFixedSize(200,200)
        self.label_ani= QLabel(self.main_win)
        self.movie=QMovie("{}/GUI/Loading_1.gif".format(dir_path))
        self.label_ani.setMovie(self.movie)
        self.verticalLayout.addWidget(self.label_ani, 0, QtCore.Qt.AlignHCenter)
        self.main_win.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.main_win.setAttribute(QtCore.Qt.WA_TranslucentBackground,on=True)
        self.startani()
        self.main_win.showMaximized()
        self.timer= QTimer(self.main_win)
        # self.timer.singleShot(1000,self.stopAni)
        self.timer.singleShot(100,lambda: self.run_module(test_cases,console,submitbtn))

    def startani(self):
        self.movie.start()
        # self.start_process()
        
    def stopAni(self):
        self.movie.stop()
        self.main_win.close()


########################################################################
## EXECUTE APP
########################################################################
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
