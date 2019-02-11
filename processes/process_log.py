import os, sys

ps = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ps)
from core.constants import BASE_APP_PATH, DEFAULT_SIZE_LOG, REMOVE_LINES_LOG

# from PyQt5.QtCore import QCoreApplication
from components.utils import ApiLogging
import time


class ProcessLog(object):

    def run(self, file, default_size, remove_lines):
        size = default_size * 1000
        if os.path.isfile(file):
            if os.path.getsize(file) >= size:
                with open(file, 'r') as f:
                    lines = f.readlines()
                if len(lines) < remove_lines:
                    ApiLogging.critical(
                        "the specific number of lines is greater than number of desired {0} file lines".format(file))
                with open(file, 'w') as f:
                    f.writelines(lines[remove_lines:])
        else:
            ApiLogging.critical("the {0} is not existed".format(file))


if __name__ == '__main__':
    if sys.argv.pop(-1) != "0X105070":
        try:
            ApiLogging.info(type(sys.argv.pop(-1)))
        except IndexError:
            ApiLogging.critical('missing token parameter')
            sys.exit(0)
        ApiLogging.critical('wrong token parameter')
        sys.exit(0)
    # app = QCoreApplication(sys.argv)
    while True:
        time.sleep(30)
        for file in os.listdir(BASE_APP_PATH + '/logs'):
            p = ProcessLog()
            p.run(BASE_APP_PATH + '/logs/' + file, default_size=DEFAULT_SIZE_LOG, remove_lines=REMOVE_LINES_LOG)
    # sys.exit(app.exec_())
