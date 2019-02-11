import functools
import json

from PyQt5.QtCore import QObject, QEventLoop, QTimer


class Utils(QObject):

    def __init__(self):
        super().__init__()

    @staticmethod
    def wait(msec):
        loop = QEventLoop()
        QTimer.singleShot(msec, loop.quit)
        loop.exec()

    @staticmethod
    def qt_js_prepare(script):
        # return "Qt.wrapResult(eval('{0}'))".format(script)
        return "result = {0}; Qt.wrapResult(result);".format(script)

    @staticmethod
    def normalize_quotes(string):
        return string.replace('"', "'").replace("'", "\\'")
