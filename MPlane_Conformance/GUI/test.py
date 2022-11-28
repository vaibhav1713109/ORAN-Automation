########################################################################
## Vaibhav Dhiman
########################################################################

########################################################################
## IMPORTS
########################################################################
import sys
import os
from PyQt5 import *


########################################################################
# IMPORT GUI FILE
from Home_2 import *
########################################################################


########################################################################
## MAIN WINDOW CLASS
########################################################################

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

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
        self.ui.submitBtn_10.clicked.connect(self.log_mgmt)
        
        ##############################################################################
        ## if clicked on module new side window will open
        ##############################################################################
        ## Module 1
        self.ui.module.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.Module1))

        ## Module 2
        self.ui.module_1.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.Module2))

        ## Module 3
        self.ui.module_2.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.Module3))

        ## Module 4
        self.ui.module_3.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.Module4))

        ## Module 5
        self.ui.module_4.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.Module5))

        ## Module 6
        self.ui.module_5.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.Module6))

        ## Module 7
        self.ui.module_6.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.Module7))

        ## Module 8
        self.ui.module_7.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.Module8))

        ## Module 9
        self.ui.module_8.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.Module9))

        ## Module 10
        self.ui.module_9.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.Module10))

        ##############################################################################
        ## Animation
        ##############################################################################
        # self.ui.stackedWidget.setTransitionDirection(QtCore.Qt.Vertical)
        # self.ui.stackedWidget.setTransitionSpeed(500)
        # self.ui.stackedWidget.setTransitionErasingCurve(QtCore.QEasingCurve.Linear)
        # self.ui.stackedWidget.setSlideTransition(False)
        self.ui.menu.clicked.connect(lambda: self.slideLeftMenu())
        self.show()

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
    # get data from each widget
    ########################################################################
    def transport_handshake(self):
        print(self.input.text())
        print(self.input1.text())
        data = {'SUDO_USER' : self.input1.text(), 'SUDO_PASS' : self.input.text()}
        WriteData(data,'{}/Conformance/inputs.ini'.format(dir_path))

    def subscription(self):
        print(self.username_2.text())
        print(self.password_2.text())
        print(self.paragon_ip.text())
        print(self.ptpSyncE.text())
        data = {'SUDO_USER' : self.username_2.text(), 'SUDO_PASS' : self.password_2.text(), 
            'paragon_ip' : self.paragon_ip.text(),'ptpSyncEport' : self.ptpSyncE.text()}
        WriteData(data,'{}/Conformance/inputs.ini'.format(dir_path))

    def supervision(self):
        print(self.username.text())
        print(self.password.text())
        data = {'SUDO_USER' : self.username.text(), 'SUDO_PASS' : self.password.text()}
        WriteData(data,'{}/Conformance/inputs.ini'.format(dir_path))

    def ru_info(self):
        print(self.username_4.text())
        print(self.password_4.text())
        data = {'SUDO_USER' : self.username_4.text(), 'SUDO_PASS' : self.password_4.text()}
        WriteData(data,'{}/Conformance/inputs.ini'.format(dir_path))

    def fault_mgmt(self):
        print(self.username_5.text())
        print(self.password_5.text())
        print(self.p_neoIP.text())
        print(self.ptpPort.text())
        data = {'SUDO_USER' : self.username_5.text(), 'SUDO_PASS' : self.password_5.text(), 
            'paragon_ip' : self.p_neoIP.text(),'ptpSyncEport' : self.ptpPort.text()}
        WriteData(data,'{}/Conformance/inputs.ini'.format(dir_path))

    def sw_mgmt(self):
        print(self.username_6.text())
        print(self.password_6.text())
        print(self.du_pswrd.text())
        print(self.sw_file.text())
        print(self.currupt_file.text())
        data = {'SUDO_USER' : self.username_6.text(), 'SUDO_PASS' : self.password_6.text(),
                'DU_PASS' : self.du_pswrd.text(), 'SW_PATH' : self.sw_file.text(),
                'Currupt_Path' : self.currupt_file.text()}
        WriteData(data,'{}/Conformance/inputs.ini'.format(dir_path))

    def access_control(self):
        print(self.sudouser.text())
        print(self.sudopswrd.text())
        print(self.nmsuser.text())
        print(self.nmspswrd.text())
        print(self.fmpmuser.text())
        print(self.fmpmpswrd.text())
        data = {'SUDO_USER' : self.sudouser.text(), 'SUDO_PASS' : self.sudopswrd.text(),
                'NMS_USER' : self.nmsuser.text(), 'NMS_PASS' : self.nmspswrd.text(),
                'FMPM_USER' : self.fmpmuser.text(), 'FMPM_PASS' : self.fmpmpswrd.text()}
        WriteData(data,'{}/Conformance/inputs.ini'.format(dir_path))

    def ru_configure(self):
        print(self.sudouser_8.text())
        print(self.sudopswrd_8.text())
        print(self.fronhaulInterface.text())
        data = {'SUDO_USER' : self.sudouser_8.text(), 'SUDO_PASS' : self.sudopswrd_8.text(),
                'FH_Interface' : self.fronhaulInterface.text()}
        WriteData(data,'{}/Conformance/inputs.ini'.format(dir_path))

    def log_mgmt(self):
        print(self.username_10.text())
        print(self.password_10.text())
        data = {'SUDO_USER' : self.username_10.text(), 'SUDO_PASS' : self.password_10.text()}
        WriteData(data,'{}/Conformance/inputs.ini'.format(dir_path))


########################################################################
## EXECUTE APP
########################################################################
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())