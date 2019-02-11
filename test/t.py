import sys
import time
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *

class MyBrowser(QWebPage):
    ''' Settings for the browser.'''

    def userAgentForUrl(self, url):
        ''' Returns a User Agent that will be seen by the website. '''
        return "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1"


class Screenshot(QWebView):
    def __init__(self):
        self.app = QApplication(sys.argv)
        QWebView.__init__(self)
        self.setPage(MyBrowser())
        self._loaded = False
        self.loadFinished.connect(self._loadFinished)
        self.show()

    def capture(self, url, output_file):
        self.load(QUrl(url))
        self.wait_load()
        # set to webpage size

        t = time.time()+100000
        while time.time() < t:
            self.app.processEvents()
            pass
        print('after timer')
        frame = self.page().mainFrame()
        print(frame.contentsSize())
        self.page().setViewportSize(frame.contentsSize())

        # render image
        print('1')
        image = QImage(self.page().viewportSize(), QImage.Format_ARGB32)
        painter = QPainter(image)
        print('2')
        frame.render(painter)
        painter.end()
        print('3')
        print ('saving', output_file)
        image.save(output_file)
        time.sleep(10000)

    def wait_load(self, delay=0):
        # process app events until page loaded
        while not self._loaded:
            self.app.processEvents()
            time.sleep(delay)
        self._loaded = False

    def _loadFinished(self, result):
        self._loaded = True

s = Screenshot()
s.capture('https://www.truecaller.com', 'truecaller.png')
