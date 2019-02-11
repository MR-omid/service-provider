import sys
from time import sleep
from PyQt5.QtCore import QCoreApplication
import signal
import sys

from components.utils import ApiLogging

app = QCoreApplication(sys.argv)

class ttt(object):
    def __init__(self):
        signal.signal(signal.SIGUSR1, self.signal_handler)
        self.name = 'step1'
        self.f = open('r.txt','w+')


    def signal_handler(self, signal, frame):
        ApiLogging.info('You pressed Ctrl+C!')
        self.name = 'step2'
        sleep(5)
        ApiLogging.info('cont')

        # sys.exit(0)

    def run(self):
        for i in range(100):
            sleep(1)
            self.f.write(str(i))
            # print(i, self.name)
            pass



# print('dddd')
t = ttt()
t.run()


sys.exit(app.exec_())
