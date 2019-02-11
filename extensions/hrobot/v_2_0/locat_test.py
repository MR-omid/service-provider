import os
import sys
from time import sleep



ps = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(ps)
from extensions.hrobot.v_2_0.Utils import Utils
from PyQt5.QtCore import QDir, QUrl, QEventLoop, QTimer
from PyQt5.QtWidgets import QApplication
from extensions.hrobot.v_2_0.Hrobot import Hrobot

try:
    os.environ['DISPLAY']
except Exception:
    from vendor.xvfbwrapper import Xvfb

    Xvfb().start()
    print('start xvfb')

app = QApplication([])

robot = Hrobot(gui=True)
local = QUrl.fromLocalFile(QDir.currentPath() + '/../../../test/js_parser/index.html')
if robot.go_to(local):

    print('end.')
else:
    print('failed to load!')
app.exec()
