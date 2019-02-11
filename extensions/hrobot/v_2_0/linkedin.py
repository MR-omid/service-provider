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

email_value = 'chelsea.naspnetworks@gmail.com'
password_value = 'thai2$1dfrg5d@Hivai'

linkedin_id = 'shruthi-adimurthy-831b02129'
robot = Hrobot(gui=True)
truecaller_url = "https://www.linkedin.com"
if robot.go_to(truecaller_url):
    email = robot.find_by_xpath('//*[@id="login-email"]')
    email.set_value(email_value)
    password = robot.find_by_xpath('//*[@id="login-password"]')
    password.set_value(password_value)
    log_in = robot.find_by_xpath('//*[@id="login-submit"]')
    log_in.click()

    # # get contact info
    # robot.go_to('https://www.linkedin.com/in/' + linkedin_id + '/detail/contact-info/')
    #
    # if robot.find_by_contain_text('h1', 'This profile is not available'):
    #     raise ('invalid linkedin id')
    #
    # contact_info = {}
    # temp = robot.wait_until_css('.pv-profile-section__section-info.section-info')
    # if temp:
    #     sections = temp.find_all_by_css('section')
    #     print('sections', sections)
    #     for sec in sections:
    #         print('sec', sec.find_by_css('div>a').get_attribute('href'), sec.get_attribute('class'))
    #         if sec.get_attribute('class') == 'pv-contact-info__contact-type ci-vanity-url':
    #             contact_info['profile_url'] = sec.find_by_css('div>a').get_attribute('href')
    #         else:
    #             address = sec.find_by_css('ul>li>div>a')
    #             if address:
    #                 contact_info[str(sec.find_by_css('header').get_text())] = str(address.get_attribute('href'))
    #             else:
    #                 address = sec.find_by_css('ul>li>a')
    #                 if address:
    #                     contact_info[str(sec.find_by_css('header').get_text())] = str(address.get_attribute('href'))
    # print(contact_info)

    robot.go_to('https://www.linkedin.com/in/' + linkedin_id)

    # robot.scroll_to_end(lazy_load=True)

    # click show more pro info
    # profile_section = robot.find_by_css('.pv-profile-section.pv-top-card-section.artdeco-container-card.ember-view')
    # print('***', profile_section)
    # if profile_section:
    #     div_Show_more_pro_info = profile_section.find_by_css('.pv-top-card-section__summary.pv-top-card-section__summary--with-content.mt4.ember-view')
    #     if div_Show_more_pro_info:
    #         button_Show_more_pro_info = div_Show_more_pro_info.find_by_css('button')
    #         if button_Show_more_pro_info:
    #             print('**', button_Show_more_pro_info.get_attribute('class'))
    #             button_Show_more_pro_info.click()


    see_all_b = robot.find_all_by_contain_text('button', 'Show')
    for each in see_all_b:
        each.click()
    print('see_all_b', see_all_b)


    see_more = robot.find_all_by_contain_text('a', 'See more')

    for each in see_more:
        each.click()

    # more_roll = robot.find_all_by_contain_text('a', 'more role')
    #
    # for each in more_roll:
    #     each.click()

    b = robot.find_by_css('.pv-profile-section__card-action-bar.pv-skills-section__additional-skills.artdeco-container-card-action-bar')
    print('bbbbbbbbbbbb', b)
    if b:
        b.click()
else:
    print('failed to load!')
app.exec()