
from PyQt5 import QtCore, QtGui, QtWidgets
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication , QWidget, QLabel
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QMovie
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtGui import QIcon,QFont
import os
  

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(527, 383)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.widget = QtWidgets.QWidget(self.centralwidget)
        self.widget.setStyleSheet("*{\n"
"border:1px solid}")
        self.widget.setObjectName("widget")
        self.pushButton = QtWidgets.QPushButton(self.widget)
        self.pushButton.setGeometry(QtCore.QRect(60, 50, 89, 25))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.Loading_1)
        self.label = QtWidgets.QLabel(self.widget)
        self.label.setGeometry(QtCore.QRect(30, 190, 281, 131))
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.widget)
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setMaximumSize(QtCore.QSize(0, 16777215))
        self.frame.setStyleSheet("*{\n"
"    border:1px solid}")
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.horizontalLayout.addWidget(self.frame)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton.setText(_translate("MainWindow", "PushButton"))
        self.label.setText(_translate("MainWindow", "hi"))
 

    def check_ping(self,hostname= '172.17.166.37'):
        response = os.system("ping -c 7 " + hostname)
        if response == 0:
            print ('Ping Successful')
            return True
        else:
            print ('Ping Failed')
            return False

    def onclick_modules(self,expand = False):
        # Get current left menu width
        width = self.frame.maximumWidth()

        # If minimized
        if width == 0:
            # Expand menu
            newWidth = self.widget.width()
        # If maximized
        else:
            # Restore menu
            newWidth = 0
        print(width, newWidth)
        # Animate the transition
        self.animation = QtCore.QPropertyAnimation(self.frame, b"maximumWidth")#Animate minimumWidht
        self.animation.setDuration(350)
        self.animation.setStartValue(width)#Start value is the current menu width
        self.animation.setEndValue(newWidth)
        self.animation.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
        self.animation.start()


    def Loading_1(self):
        self.frame.setStyleSheet("#frame{\n"
"    border: 1px solid;\n"
"}\n")
        self.label_ani= QLabel(self.frame)
        self.movie=QMovie("Loading_1.gif")
        self.label_ani.setMovie(self.movie)
        self.horizontalLayout.addWidget(self.label_ani, 0, QtCore.Qt.AlignHCenter)
        self.frame.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.frame.setAttribute(QtCore.Qt.WA_TranslucentBackground,on=True)
        
        self.startani()
        # self.frame.showMaximized()
        self.onclick_modules(expand=True)
        self.timer= QTimer(self.frame)
        # self.timer.singleShot(1000,self.stopAni)
        self.timer.singleShot(5000,self.stopAni)
        # if self.pinging():
        # self.stopAni()

    def startani(self):
        self.movie.start()
        # self.start_process()
        
    def stopAni(self):
        # self.start_process()
        self.check_ping()
        self.movie.stop()
        # self.start_process()
        self.onclick_modules(expand=False)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    demo = Ui_MainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.showMaximized()
    sys.exit(app.exec_())
