import base64
from time import sleep

from PyQt5.QtCore import QT_VERSION_STR, QUrl, QDir, QObject, pyqtSlot, QJsonValue
from PyQt5.Qt import PYQT_VERSION_STR
from sip import SIP_VERSION_STR

from PyQt5.QtWebChannel import QWebChannel

print("Qt version:", QT_VERSION_STR) # Qt version: 5.11.2
print("SIP version:", SIP_VERSION_STR) # SIP version: 4.19.13
print("PyQt version:", PYQT_VERSION_STR) # PyQt version: 5.11.3
from PyQt5.QtWebEngineWidgets import QWebEnginePage, QWebEngineView
from PyQt5.QtWidgets import QApplication

app = QApplication([])


Page = QWebEnginePage()
view = QWebEngineView()
Page.setView(view)


class jscall(QObject):
    def __init__(self):
        super().__init__()

        self.result = 'default'

    @pyqtSlot(str)
    def callme(self, arg: str):
        # b = a.toObject()
        print(arg)


js_call = jscall()

channel = QWebChannel(Page)
channel.registerObject("webobj", js_call)
Page.setWebChannel(channel)
def _status(status):
    print('load status: ', status)
    # Page.runJavaScript('window.d487 = document.getElementsByTagName("img")', _js)
    # Page.runJavaScript('d487[1].src',_js)
    # Page.runJavaScript('Qt.ev("document.getElementsByTagName(\'a\')")[1].click()', _js)
    Page.runJavaScript('Qt.register()', _js)


def _js(result):
    print('js result: ', result)


Page.loadFinished.connect(_status)

Page.load(QUrl.fromLocalFile(QDir.currentPath()+'/index.html'))
view.show()

app.exec()
