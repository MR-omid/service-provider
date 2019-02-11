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

robot = Hrobot(gui=False)
local = QUrl.fromLocalFile(QDir.currentPath() + '/../../../test/js_parser/index.html')
remote = QUrl('https://divar.ir/tehran/%D8%AA%D9%87%D8%B1%D8%A7%D9%86/browse/')
remote2 = QUrl('http://www.mybabyname.com/')
truecaller_url = "https://www.truecaller.com"
if robot.go_to(truecaller_url):
    sign_in = robot.find_by_css('a.TopNav__Link.TopNav__SignIn') #app > div.TopNav > div > div.TopNav__StickyMenu > a.TopNav__Link.TopNav__SignIn
    sign_in.click()

    gmail = robot.wait_until_css("div.sign-in-dialog-provider")
    gmail.click()
    email_value = "raminfawork@gmail.com"
    password_value = 'DPE12345678'

    email = robot.wait_until_xpath('//input[@id="identifierId"]')
    email.set_value(email_value)

    next = robot.find_by_css('div.ZFr60d.CeoRYc')
    if next:
        next.click()

    # passss = robot.find_all_by_xpath('')
    passwords = robot.wait_until_css('div#password')

    password = passwords.find_by_css('input')
    # password = robot.wait_until_xpath('//input[@name="password"]')
    # # password = robot.wait_until_xpath('/html/body/div[1]/div[1]/div[2]/div[2]/div/div/div[2]/div/div[1]/div/form/content/section/div/content/div[1]/div/div[1]/div/div[1]/input')
    #
    print('pass', password.get_tag_name(), password.get_attribute('type'), password.is_visible())
    # print(password)
    #
    password.set_value(password_value)

    next = robot.find_by_css('div.ZFr60d.CeoRYc')

    if next:
        next.click()


#     sign_in = robot.find_by_xpath("/html/body/div[1]/div[2]/div/div[4]/a[2]")
#     # sign_in.focus()
#     # sign_in.focus()
#     sign_in.click()
#     sign_in.click()
#     # print(sign_in.eval_script('node.text'))
#     # sign_in.click()
#     robot.save_as_pdf('popup.pdf')
#     a = robot.find_by_xpath("/html/body/div[1]/div[2]/div/div/div[1]/div/div[2]")
#     # print(a.get_text())
#     a.click()
#     # print()
#     # print(robot.get_body())
#     # print()
#     # print()
#     # robot.save_as_pdf('test.pdf')
#     #
#     email_value = "donramin1994@gmail.com"
#     password_value = '0017042887'
#     # sleep(5)
#     # print(email_value)
#     # inputs = robot.find_all_by_css('input')
#     # print(inputs[0].get_text())
#     # print(robot.find_by_xpath('/html/body/div[1]/div[1]/div[2]/div[2]/div/div/div[2]/div/div[1]/div'))
#     # sleep(3)
#     # print(robot.find_by_xpath('/html/body/div[1]/div[1]/div[2]/div[2]/div/div/div[2]/div/div[1]/div'))
#     # email = robot.find_by_xpath('//*[@id="identifierId"]')
#     print(robot.eval_script('document.readyState'))
#     print('before email')
#     email = robot.wait_until_xpath('//*[@id="identifierId"]')
#     print('email: ', email)
#     # print(email)
#     # # sleep(3)
#     # print(robot.save_as_pdf('test.pdf'))
#     email.set_value(email_value)
#     # robot.save_as_pdf('email.pdf')
#     next = robot.find_by_xpath('/html/body/div[1]/div[1]/div[2]/div[2]/div/div/div[2]/div/div[2]/div/div[1]/div/content/span')
#     next.click()
#     robot.save_as_pdf('pass.pdf')
#     # password = robot.find_by_xpath('/html/body/div[1]/div[1]/div[2]/div[2]/div/div/div[2]/div/div[1]/div/form/content/section/div/content/div[1]/div/div[1]/div/div[1]/input')
#     password = robot.wait_until_xpath('//input[@type="password"]')
#     print('pass: ', password.is_visible(), password.is_attached(), password.is_disabled())
#     password.set_value(password_value)
#     # Utils.wait(100000)
#     #
#     submit = robot.find_by_xpath('/html/body/div[1]/div[1]/div[2]/div[2]/div/div/div[2]/div/div[2]/div/div[1]/div/content/span')
#     print('next: ', submit.get_text())
#     submit.click()
#     robot.save_as_pdf('final.pdf')
#
    region = robot.wait_until_xpath("/html/body/div[1]/div[4]/div[1]/div/div[2]/div[1]/div/select")
    region_options = robot.find_all_by_css('option')
    for o in region_options:
        if o.get_value() == 'ir':
            o.select_option()

#
    num = '9127062377'
    input_number = robot.find_by_xpath("/html/body/div[1]/div[4]/div[1]/div/div[2]/div[1]/input")
    input_number.set_value(num)
#     print(input_number.get_value())
#     print('set number')
    input_number.enter()
    robot.save_as_pdf('test.pdf')
#     robot.save_as_pdf('result.pdf')
#     # # sleep(3)
#     # a = robot.find_by_xpath("""//*[@id="app"]/div[4]/div[1]/div/div[2]/div[1]/button[2]""")
#     # # # print(a.get_center_position())
#     # a.click()
#     # sleep(2)
#     # b = robot.find_by_xpath("""//*[@id="app"]/div[2]/div/div/div[1]/div""")
#     # print(b.get_center_position())
#     # b.click()
#
#     # print(a.get_center_position())
#     # region.set_value()
#     # print('is private', robot.is_private())
#     # print('tesssssssssssssssssssst: ', robot.eval_script('1+2'))
#     # print('find all')
#     # single_node = robot.wait_until_css('a',5)
#     # print(single_node.is_attached())
#     # single_a = robot.find_by_contain_text('a', '2')
#     # print(single_node, single_node.get_xpath())
#     # single_node.focus()
#     # div = robot.find_by_css('#scope')
#     # for a in div.find_all_by_css('a'):
#     #     print(a.get_text())
#     #
#     # img = robot.find_by_css('img')
#     # img.save_image('test.png')
#     # QTimer.singleShot(2000, lambda: img.save_image('test.png'))
#
#     # alist = robot.find_all_by_css('a')
#     # for a in alist:
#     #     print(a.get_text())
#     #     if a.get_text() in 'text 2':
#     #         print('a for click: ', a)
#     #         a.click()
#     #         break
#     #     sleep(5)
#     #     print('go back')
#     #     robot.go_back()
#     #     break
#     # print('reccccccct: ', b[0].get_position())
#     # robot.save_as_png(1)
#     # print('scroll: ',robot.scroll_to_end(True))
#     # print('after scroll')
#     # alist = robot.find_all_by_css('a')
#     # for a in alist:
#     #     t = a.get_text()
#     #     print(t)
#     #     if t and '2' in t:
#     #         a.click()
# # {'y': 0, 'bottom': 478, 'x': 0, 'height': 478, 'right': 1905, 'left': 0, 'width': 1905, 'top': 0}
# # print('tttttttt',alist[0].get_text())
# # alist[1].left_click()
# # print('pdf started.')
# # robot.to_pdf('click.pdf')
# # alist[1].


    print('end.')
else:
    print('failed to load!')
app.exec()
