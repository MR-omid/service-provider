from PyQt5.QtCore import QObject, QPoint, Qt, QEvent, QCoreApplication, pyqtSlot, QTimer, QEventLoop
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QWidget


class Mouse(QObject):

    def __init__(self, page):
        super().__init__()
        self.page = page

    def __get_widget(self):
        for child in self.page.view().children():
            if child.__class__ is QWidget:
                return child

    def __press(self, pos: QPoint, modifier=Qt.NoModifier):
        press = QMouseEvent(QEvent.MouseButtonPress, pos, Qt.LeftButton, Qt.LeftButton, modifier)
        QCoreApplication.postEvent(self.__get_widget(), press)

    def __release(self, pos: QPoint, modifier=Qt.NoModifier):
        release = QMouseEvent(QEvent.MouseButtonRelease, pos, Qt.LeftButton, Qt.NoButton, modifier)
        QCoreApplication.postEvent(self.__get_widget(), release)

    def left_click(self, x, y):
        print('start click event loop')
        loop = QEventLoop()
        pos = QPoint(x, y)
        self.__press(pos)
        QTimer.singleShot(300, lambda: self.__release(pos))
        QTimer.singleShot(800, loop.quit)
        loop.exec()
        print('end click event loop')
