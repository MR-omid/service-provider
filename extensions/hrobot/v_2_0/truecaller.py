import os
import sys
from time import sleep

ps = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(ps)

from PyQt5.QtCore import QDir, QUrl, QEventLoop, QTimer
from PyQt5.QtWidgets import QApplication
from extensions.hrobot.v_2_0.Hrobot import Hrobot

try:
    os.environ['DISPLAY']
except Exception:
    from extensions.hrobot.v_2_0.xvfbwrapper import Xvfb

    Xvfb().start()

app = QApplication([])

robot = Hrobot(gui=True)
local = QUrl.fromLocalFile(QDir.currentPath() + '/../../../test/js_parser/index.html')
remote = QUrl('https://divar.ir/tehran/%D8%AA%D9%87%D8%B1%D8%A7%D9%86/browse/')
remote2 = QUrl('http://www.mybabyname.com/')
truecaller_url = "https://www.google.com"
if robot.go_to(truecaller_url):
    input = robot.find_by_xpath('//*[@id="tsf"]/div[2]/div/div[1]/div/div[1]/input')
    print('input' , input.get_tag_name())
    input.set_value('varzesh3')
    robot.find_by_xpath('//*[@id="tsf"]/div[2]/div/div[3]/center/input[1]').click()
    robot.find_by_xpath('//*[@id="rso"]/div[1]/div/div/div/div/div[1]/a[1]/h3/span').click()
    robot.find_by_xpath('/html/body/header/div[4]/div/nav/ul/li[8]/a').click()
else:
    print('failed to load!')
app.exec()