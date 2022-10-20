from PyQt5 import QtWidgets, uic, QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import QMovie
import traceback, sys
class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        `tuple` (exctype, value, traceback.format_exc() )

    result
        `object` data returned from processing, anything

    progress
        `int` indicating % progress

    '''
    finished = pyqtSignal ()
    error = pyqtSignal (tuple)
    result = pyqtSignal (object)
    progress = pyqtSignal (int)



class Worker (QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    '''

    def __init__(self, fn, *args, **kwargs):
        super (Worker, self).__init__ ()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals ()

        # Add the callback to our kwargs
        self.kwargs['progress_callback'] = self.signals.progress

    @pyqtSlot ()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn (*self.args, **self.kwargs)
        except:
            traceback.print_exc ()
            exctype, value = sys.exc_info ()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc ()))
        else:
            self.signals.result.emit (result)  # Return the result of the processing
        finally:
            self.signals.finished.emit ()  # Done


class Ui(QtWidgets.QMainWindow):
    def __init__(self):

        super(Ui, self).__init__()
        # uic.loadUi('Ui/MyAppUI.Ui', self)
        # === We display the UI ==========
        self.show()
        # === THis will handle the MULTITHREAD PART ===================
        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

        self.StartPreparingMyApp() #<======== This method doesn't work!!!!

        # === Associate methods to the buttons of the UI ==============        
        self.button_Report.clicked.connect (self.ButtonStartMyAppReport)        
        self.button_Run.clicked.connect (self.ButtonStartMyApp)

	# def StartMyAppReport(self, progress_callback):
	# 	print('StartMyAppReport')
	# 	#do some stuff

    # def StartMyApp(self, progress_callback):
	# 	pass
        # do some stuff

    def ButtonStartMyApp(self): #<=== This method works perfectly by showing the loading gif.
        # Pass the function to execute
        # === We need to block the Button Run and change its color
        self.button_Run.setEnabled (False)
        self.button_Run.setText ('Running...')
        self.button_Run.setStyleSheet ("background-color: #ffcc00;")
        self.label_logo.setHidden (True)
        self.label_running.setHidden (False)

        # === Play animated gif ================
        self.gif = QMovie ('ui/animated_gif_logo_UI_.gif')
        self.label_running.setMovie (self.gif)
        self.gif.start ()

        self.EditTextFieldUi (self.label_HeaderMsg1, '#ff8a00',
                              "MyApp is running the tasks... You can press the button 'Report' to see what MyApp has done.")
        self.EditTextFieldUi (self.label_HeaderMsg2, '#ff8a00',
                              "Press 'button 'Quit' to stop and turn off MyApp.")

        worker = Worker (self.StartMyApp)  # Any other args, kwargs are passed to the run function
        worker.signals.result.connect (self.print_output)
        worker.signals.finished.connect (self.thread_complete)
        worker.signals.progress.connect (self.progress_fn)

        # Execute
        self.threadpool.start (worker)

    def PreparingMyApp(self, progress_callback):
        #do some stuff
        return "Done"

    def ButtonStartMyAppReport(self):
        # Pass the function to execute
        worker = Worker (self.StartMyAppReport)  # Any other args, kwargs are passed to the run function
        worker.signals.result.connect (self.print_output)
        worker.signals.finished.connect (self.thread_complete)
        worker.signals.progress.connect (self.progress_fn)

        # Execute
        self.threadpool.start(worker)


    def StartPreparingMyApp(self): #<=== This method doesn't work !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # === Play animated gif ================
        self.label_loading.setHidden (False)
        self.gif_loading = QMovie ('loader.gif')
        self.label_loading.setMovie (self.gif_loading)
        self.gif_loading.start ()

        # Pass the function to execute
        worker = Worker (self.PreparingMyApp)  # Any other args, kwargs are passed to the run function
        worker.signals.result.connect (self.print_output)
        worker.signals.finished.connect (self.thread_complete)
        worker.signals.progress.connect (self.progress_fn)

        # Execute
        self.threadpool.start (worker)

        self.gif_loading.stop ()
        self.label_loading.setHidden (True)


if __name__ == '__main__':    
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    app.exec_()