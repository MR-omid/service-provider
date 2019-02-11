from PyQt5.QtCore import QUrl, pyqtSignal, QTimer, QEventLoop
from PyQt5.QtWebEngineWidgets import QWebEnginePage


class Page(QWebEnginePage):

    navigationRequested = pyqtSignal()

    def __init__(self, *__args):
        super().__init__(*__args)

    def acceptNavigationRequest(self, url, navigation_type, ok):
        QTimer.singleShot(10, lambda: self.navigationRequested.emit())
        print('navigation started', url)
        return True

    def _js_gap_eventloop(self):
        print('js gap start')
        loop = QEventLoop()
        self.navigationRequested.connect(loop.quit)
        loop.exec()
        print('js gap end')


