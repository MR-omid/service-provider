#!/usr/bin/env python3
#coding:utf-8
# Author:   --<>
# Purpose:  To demonstrate creation of multiple threads and identify the receipt of thread results
# Created: 19/12/15

import sys


from PyQt4.QtCore import QThread, pyqtSlot, pyqtSignal
from PyQt4.QtGui import QApplication, QLabel, QWidget, QGridLayout

import sys
#!/usr/bin/env python3
#coding:utf-8
# Author:   --<>
# Purpose:
# Created: 19/12/15

import sys
import unittest


from PyQt4.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
import time
import random


class Worker(QObject):
    finished = pyqtSignal(int)
    intReady = pyqtSignal(int,int)

    def __init__(self, i=0):
        '''__init__ is called while the worker is still in the Gui thread. Do not put slow or CPU intensive code in the __init__ method'''

        super(Worker, self).__init__()
        self.idd = i



    @pyqtSlot()
    def procCounter(self): # This slot takes no params
        for j in range(1, 10):
            random_time = random.weibullvariate(1,2)
            time.sleep(random_time)
            self.intReady.emit(j,self.idd)
            print('Worker {0} in thread {1}'.format(self.idd, self.thread().idd))

        self.finished.emit(self.idd)



class Thread(QThread):
    #make new signals to be able to return an id for the thread
    startedx = pyqtSignal(int)
    finishedx = pyqtSignal(int)

    def __init__(self,i,parent=None):
        super(Thread, self).__init__(parent)
        self.idd = i

        self.started.connect(self.starttt)
        self.finished.connect(self.finisheddd)

    @pyqtSlot()
    def starttt(self):
        print('started signal from thread emitted')
        self.startedx.emit(self.idd)

    @pyqtSlot()
    def finisheddd(self):
        print('finished signal from thread emitted')
        self.finishedx.emit(self.idd)

class Form(QWidget):

    def __init__(self):
        super(Form, self).__init__()

        self.initUI()

        self.worker={}
        self.threadx={}
        self.i=0
        i=0

        #Establish the maximum number of threads the machine can optimally handle
        #Generally relates to the number of processors

        self.threadtest = QThread(self)
        self.idealthreadcount = self.threadtest.idealThreadCount()

        print("This machine can handle {} threads optimally".format(self.idealthreadcount))

        while i <self.idealthreadcount:
            self.setupThread(i)
            i+=1

        i=0
        while i<self.idealthreadcount:
            self.startThread(i)
            i+=1

        print("Main Gui running in thread {}.".format(self.thread()))


    def setupThread(self,i):

        self.worker[i]= Worker(i)  # no parent!
        #print("Worker object runningt in thread {} prior to movetothread".format(self.worker[i].thread()) )
        self.threadx[i] = Thread(i,parent=self)  #  if parent isn't specified then need to be careful to destroy thread
        self.threadx[i].setObjectName("python thread{}"+str(i))
        #print("Thread object runningt in thread {} prior to movetothread".format(self.threadx[i].thread()) )
        self.threadx[i].startedx.connect(self.threadStarted)
        self.threadx[i].finishedx.connect(self.threadFinished)

        self.worker[i].finished.connect(self.workerFinished)
        self.worker[i].intReady.connect(self.workerResultReady)

        #The next line is optional, you may want to start the threads again without having to create all the code again.
        self.worker[i].finished.connect(self.threadx[i].quit)

        self.threadx[i].started.connect(self.worker[i].procCounter)

        self.destroyed.connect(self.threadx[i].deleteLater)
        self.destroyed.connect(self.worker[i].deleteLater)

        #This is the key code that actually get the worker code onto another processor or thread.
        self.worker[i].moveToThread(self.threadx[i])

    def startThread(self,i):
        self.threadx[i].start()

    @pyqtSlot(int)
    def threadStarted(self,i):
        print('Thread {}  started'.format(i))
        print("Thread priority is {}".format(self.threadx[i].priority()))


    @pyqtSlot(int)
    def threadFinished(self,i):
        print('Thread {} finished'.format(i))




    @pyqtSlot(int)
    def threadTerminated(self,i):
        print("Thread {} terminated".format(i))

    @pyqtSlot(int,int)
    def workerResultReady(self,j,i):
        print('Worker {} result returned'.format(i))
        if i ==0:
            self.label1.setText("{}".format(j))
        if i ==1:
            self.label2.setText("{}".format(j))
        if i ==2:
            self.label3.setText("{}".format(j))
        if i ==3:
            self.label4.setText("{}".format(j))

        #print('Thread {} has started'.format(self.threadx[i].currentThreadId()))

    @pyqtSlot(int)
    def workerFinished(self,i):
        print('Worker {} finished'.format(i))

    def initUI(self):
        self.label1 = QLabel("0")
        self.label2= QLabel("0")
        self.label3= QLabel("0")
        self.label4 = QLabel("0")
        grid = QGridLayout(self)
        self.setLayout(grid)
        grid.addWidget(self.label1,0,0)
        grid.addWidget(self.label2,0,1)
        grid.addWidget(self.label3,0,2)
        grid.addWidget(self.label4,0,3) #Layout parents the self.labels

        self.move(300, 150)
        self.setGeometry(0,0,300,300)
        #self.size(300,300)
        self.setWindowTitle('thread test')
        self.show()

    def closeEvent(self, event):
        print('Closing')

        #this tells the threads to stop running
        i=0
        while i <self.idealthreadcount:
            self.threadx[i].quit()
            i+=1

         #this ensures window cannot be closed until the threads have finished.
        i=0
        while i <self.idealthreadcount:
            self.threadx[i].wait()
            i+=1


        event.accept()


if __name__=='__main__':
    app = QApplication(sys.argv)
    form = Form()
    sys.exit(app.exec_())