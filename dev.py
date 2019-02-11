import sys
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtCore import QT_VERSION_STR
from PyQt5.Qt import PYQT_VERSION_STR
from sip import SIP_VERSION_STR

from components.utils import ApiLogging

print("Qt version:", QT_VERSION_STR)
print("SIP version:", SIP_VERSION_STR)
print("PyQt version:", PYQT_VERSION_STR)
from core.api import Server

if sys.argv.pop(-1) != "0X105010":
    try:
        ApiLogging.info(type(sys.argv.pop(-1)))
    except IndexError:
        ApiLogging.critical('missing token parameter')
        sys.exit(0)
    ApiLogging.critical('wrong token parameter')
    sys.exit(0)
app = QCoreApplication(sys.argv)
server = Server()
server.start()
sys.exit(app.exec_())