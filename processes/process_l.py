import os, sys
ps = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ps)
from components.utils import ApiLogging
from PyQt5.QtCore import QCoreApplication
from processes.base_process import BaseProcess


class ProcessL(BaseProcess):

    def __init__(self):
        super().__init__('LQueue', 30)


if __name__ == "__main__":
    if sys.argv.pop(-1) != "0X105040":
        try:
            ApiLogging.info(type(sys.argv.pop(-1)))
        except IndexError:
            ApiLogging.critical('missing token parameter')
            sys.exit(0)
        ApiLogging.critical('wrong token parameter')
        sys.exit(0)

    app = QCoreApplication(sys.argv)
    p = ProcessL()
    p.run()
    sys.exit(app.exec_())
