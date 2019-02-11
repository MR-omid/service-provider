from PyQt5.QtCore import QObject, QPoint, QEvent, Qt, QTimer, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QWidget


class QtInvocation(QObject):

    async_js_finished = pyqtSignal()
    js_ready = pyqtSignal()

    def __init__(self, page):
        super().__init__()
        self.page = page

    @pyqtSlot()
    def emit_async_js_finished(self):
        QTimer.singleShot(1000, lambda: self.async_js_finished.emit())
        print('async js finished signal')

    @pyqtSlot()
    def emit_js_ready(self):
        self.js_ready.emit()

    # @pyqtSlot(int, int)
    # def click(self, x, y):
    #     print('invoke click start')
    #     self.mouse.left_click(x, y)
    #     print('invoke click end')
    #     self.emit_async_js_finished()
