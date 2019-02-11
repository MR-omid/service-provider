import time

from extensions.hrobot.v_1_0.Hrobot import Hrobot

robot = Hrobot('.','https://www.linkedin.com')
robot.go_to('/')
# robot.save_as_png('/home/dpe/Desktop/tttt.png')
email =robot.find_by_css("input[id='login-email']")
password =robot.find_by_css("input[id='login-password']")
log_in = robot.find_by_css("input[id='login-submit']")
email.set_value('chelsea.naspnetworks@gmail.com')
password.set_value('thai2$1dfrg5d@Hivai')
if log_in:
    robot.save_as_png('before_login.png')
    password.submit()
    robot.go_to('/feed/')
    #robot.wait(10000)
    robot.go_to('/feed/')
    time.sleep(10)
    print('log in')
    robot.save_as_png('login.png')

print(robot.get_url())

robot.go_to('/in/ramin-fatourehchi-39931a9a')

robot.save_as_png('tttt.png')


print(robot.find_by_contain_text('*', 'dana insurance '))
print(robot.find_by_css('#ember3655 > div:nth-child(2) > h3:nth-child(1)'))
