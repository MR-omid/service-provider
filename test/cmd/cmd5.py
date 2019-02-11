import tempfile
import time
import os

from PIL import Image

from components.utils import ApiLogging
from extensions.hrobot.v_1_0.Hrobot import Hrobot
from test.cmd.captcha2upload import CaptchaUpload

email = 'ali_sev@yahoo.com'
password = '123456dzz'
current_milli_time = lambda: int(round(time.time() * 1000))
unique_time = current_milli_time()
cookie_path = os.path.dirname(__file__)
robot = Hrobot(cookie_path,"http://cmd5.org")



def log(txt):
    f = open("result.txt", "a")
    f.write("%s\n" % txt)
    f.close()


def is_logeed_in():
    global unique_time
    unique_time = current_milli_time()
    if robot.find_by_xpath('//a[@href="exit.aspx"]') is not None:
        robot.save_cookies_to_file(robot.get_cookies())
        return True
    else:
        set_cookie()
        if robot.find_by_xpath('//a[@href="exit.aspx"]') is not None:
            robot.save_cookies_to_file(robot.get_cookies())
            return True
    return False


def set_cookie():
    for cookie in robot.load_cookies_from_file():
        robot.set_cookie(cookie)
    robot.set_timeout(30)
    robot.go_to('/')


def login():
    if is_logeed_in():
        ApiLogging.info('cookie login')
        return True
    else:
        ApiLogging.info ('captcha login')
        robot.go_to('/login.aspx')
        email_field = robot.find_by_css('#ctl00_ContentPlaceHolder1_TextBoxCmd5_E')
        password_field = robot.find_by_css('#ctl00_ContentPlaceHolder1_TextBoxCmd5_P')
        email_field.set_value(email)
        password_field.set_value(password)
        fill_captcha_if_needed()
        submit_button = robot.find_by_css("#ctl00_ContentPlaceHolder1_Button1")
        submit_button.click()
        robot.save_cookies_to_file(robot.get_cookies())
        if is_logeed_in():
            ApiLogging.info ('logged in')
            return True
    return False


def decode(hash_type,hash_code):
    if login():
        hash_field = robot.find_by_css('#ctl00_ContentPlaceHolder1_TextBoxInput')
        if hash_field is not None:
            type_field = robot.find_by_css('#ctl00_ContentPlaceHolder1_InputHashType')
            ApiLogging.info('hash: ' + str(hash) +' type: ' + str(type) + ' hashcode: '+ hash_code )
            return None
            hash_field.set_value(hash)
            type_field.set_value(type)
            fill_captcha_if_needed()
            submit_button = robot.find_by_css("#ctl00_ContentPlaceHolder1_Button1")
            submit_button.click()
            result = robot.find_by_css('#ctl00_ContentPlaceHolder1_LabelAnswer')
            ApiLogging.info ("result: %s"%result.get_text().split('\n')[0])
            if result.get_text() == 'Verify code error!':
                decode(hash_type,hash_code)
            elif 'payment' in result.get_text():
                pr = robot.find_by_contain_text('a', 'Purchase')
                if pr:
                    pr.click()
                    result = robot.find_by_css('#ctl00_ContentPlaceHolder1_LabelAnswer')
                    ApiLogging.info("result: %s" % result.get_text().split('\n')[0])
            elif 'Not Found' in result.get_text():
                ApiLogging.warning('Not Found')
            else:
                log(result.get_text().split('\n')[0])
    else:
        ApiLogging.warning ('login fail')


def fill_captcha_if_needed():
    captcha_field = robot.find_by_css('#ctl00_ContentPlaceHolder1_TextBoxCode')
    if captcha_field is not None:
        ApiLogging.info ('captcha needed')
        robot.set_viewport_size(1280,800)
        img = robot.find_by_css("#Image1")
        rect = img.get_position()
        box = (int(rect['left']), int(rect['top']), int(rect['right']), int(rect['bottom']))
        filename = tempfile.mktemp('.png')
        robot.save_as_png(filename, 1280, 800)
        image = Image.open(filename)
        os.unlink(filename)
        captcha_image = image.crop(box)
        captcha_image.save('%s.png' % unique_time, 'png')
        captcha_field.set_value(resolve_captcha('%s.png' % unique_time))
        os.remove('%s.png' % unique_time)


def resolve_captcha(file):
    api_key = "2632143214b9b24e9dc7590396f1dd22"
    captcha_object = CaptchaUpload(key=api_key,waittime=3)
    captcha = captcha_object.solve(file)
    ApiLogging.info('finded capcha: '+ str(captcha))
    return captcha


hash_list100=[{'type':'md5(md5($pass))','hash':'e10adc3949ba59abbe56e057f20f883e'},{'type':'md5','hash':'e2fc714c4727ee9395f324cd2e7f331f'},{'type':'md5','hash':'116e055b63d8698142614628d179f5f9'},{'type':'md5','hash':'5a90d2dde2355447e668cdc722cad314'},{'type':'md5','hash':'63ed0a956627c5d924dcf69add4866f4'},{'type':'md5','hash':'b5393216a1be4f2cbe09926b4baf5554'},{'type':'md5','hash':'aea4fa2f74b681d4327cfc178d6cbcaa'},{'type':'md5(md5($pass))','hash':'e10adc3949ba59abbe56e057f20f883e'},{'type':'md5','hash':'e2fc714c4727ee9395f324cd2e7f331f'},{'type':'md5','hash':'116e055b63d8698142614628d179f5f9'},{'type':'md5','hash':'5a90d2dde2355447e668cdc722cad314'},{'type':'md5','hash':'63ed0a956627c5d924dcf69add4866f4'},{'type':'md5','hash':'b5393216a1be4f2cbe09926b4baf5554'},{'type':'md5','hash':'aea4fa2f74b681d4327cfc178d6cbcaa'},{'type':'md5(md5($pass))','hash':'e10adc3949ba59abbe56e057f20f883e'},{'type':'md5','hash':'e2fc714c4727ee9395f324cd2e7f331f'},{'type':'md5','hash':'116e055b63d8698142614628d179f5f9'},{'type':'md5','hash':'5a90d2dde2355447e668cdc722cad314'},{'type':'md5','hash':'63ed0a956627c5d924dcf69add4866f4'},{'type':'md5','hash':'b5393216a1be4f2cbe09926b4baf5554'},{'type':'md5','hash':'aea4fa2f74b681d4327cfc178d6cbcaa'},{'type':'md5(md5($pass))','hash':'e10adc3949ba59abbe56e057f20f883e'},{'type':'md5','hash':'e2fc714c4727ee9395f324cd2e7f331f'},{'type':'md5','hash':'116e055b63d8698142614628d179f5f9'},{'type':'md5','hash':'5a90d2dde2355447e668cdc722cad314'},{'type':'md5','hash':'63ed0a956627c5d924dcf69add4866f4'},{'type':'md5','hash':'b5393216a1be4f2cbe09926b4baf5554'},{'type':'md5','hash':'aea4fa2f74b681d4327cfc178d6cbcaa'},{'type':'md5(md5($pass))','hash':'e10adc3949ba59abbe56e057f20f883e'},{'type':'md5','hash':'e2fc714c4727ee9395f324cd2e7f331f'},{'type':'md5','hash':'116e055b63d8698142614628d179f5f9'},{'type':'md5','hash':'5a90d2dde2355447e668cdc722cad314'},{'type':'md5','hash':'63ed0a956627c5d924dcf69add4866f4'},{'type':'md5','hash':'b5393216a1be4f2cbe09926b4baf5554'},{'type':'md5','hash':'aea4fa2f74b681d4327cfc178d6cbcaa'},{'type':'md5(md5($pass))','hash':'e10adc3949ba59abbe56e057f20f883e'},{'type':'md5','hash':'e2fc714c4727ee9395f324cd2e7f331f'},{'type':'md5','hash':'116e055b63d8698142614628d179f5f9'},{'type':'md5','hash':'5a90d2dde2355447e668cdc722cad314'},{'type':'md5','hash':'63ed0a956627c5d924dcf69add4866f4'},{'type':'md5','hash':'b5393216a1be4f2cbe09926b4baf5554'},{'type':'md5','hash':'aea4fa2f74b681d4327cfc178d6cbcaa'},{'type':'md5(md5($pass))','hash':'e10adc3949ba59abbe56e057f20f883e'},{'type':'md5','hash':'e2fc714c4727ee9395f324cd2e7f331f'},{'type':'md5','hash':'116e055b63d8698142614628d179f5f9'},{'type':'md5','hash':'5a90d2dde2355447e668cdc722cad314'},{'type':'md5','hash':'63ed0a956627c5d924dcf69add4866f4'},{'type':'md5','hash':'b5393216a1be4f2cbe09926b4baf5554'},{'type':'md5','hash':'aea4fa2f74b681d4327cfc178d6cbcaa'},{'type':'md5(md5($pass))','hash':'e10adc3949ba59abbe56e057f20f883e'},{'type':'md5','hash':'e2fc714c4727ee9395f324cd2e7f331f'},{'type':'md5','hash':'116e055b63d8698142614628d179f5f9'},{'type':'md5','hash':'5a90d2dde2355447e668cdc722cad314'},{'type':'md5','hash':'63ed0a956627c5d924dcf69add4866f4'},{'type':'md5','hash':'b5393216a1be4f2cbe09926b4baf5554'},{'type':'md5','hash':'aea4fa2f74b681d4327cfc178d6cbcaa'},{'type':'md5(md5($pass))','hash':'e10adc3949ba59abbe56e057f20f883e'},{'type':'md5','hash':'e2fc714c4727ee9395f324cd2e7f331f'},{'type':'md5','hash':'116e055b63d8698142614628d179f5f9'},{'type':'md5','hash':'5a90d2dde2355447e668cdc722cad314'},{'type':'md5','hash':'63ed0a956627c5d924dcf69add4866f4'},{'type':'md5','hash':'b5393216a1be4f2cbe09926b4baf5554'},{'type':'md5','hash':'aea4fa2f74b681d4327cfc178d6cbcaa'},{'type':'md5(md5($pass))','hash':'e10adc3949ba59abbe56e057f20f883e'},{'type':'md5','hash':'e2fc714c4727ee9395f324cd2e7f331f'},{'type':'md5','hash':'116e055b63d8698142614628d179f5f9'},{'type':'md5','hash':'5a90d2dde2355447e668cdc722cad314'},{'type':'md5','hash':'63ed0a956627c5d924dcf69add4866f4'},{'type':'md5','hash':'b5393216a1be4f2cbe09926b4baf5554'},{'type':'md5','hash':'aea4fa2f74b681d4327cfc178d6cbcaa'},{'type':'md5(md5($pass))','hash':'e10adc3949ba59abbe56e057f20f883e'},{'type':'md5','hash':'e2fc714c4727ee9395f324cd2e7f331f'},{'type':'md5','hash':'116e055b63d8698142614628d179f5f9'},{'type':'md5','hash':'5a90d2dde2355447e668cdc722cad314'},{'type':'md5','hash':'63ed0a956627c5d924dcf69add4866f4'},{'type':'md5','hash':'b5393216a1be4f2cbe09926b4baf5554'},{'type':'md5','hash':'aea4fa2f74b681d4327cfc178d6cbcaa'},{'type':'md5(md5($pass))','hash':'e10adc3949ba59abbe56e057f20f883e'},{'type':'md5','hash':'e2fc714c4727ee9395f324cd2e7f331f'},{'type':'md5','hash':'116e055b63d8698142614628d179f5f9'},{'type':'md5','hash':'5a90d2dde2355447e668cdc722cad314'},{'type':'md5','hash':'63ed0a956627c5d924dcf69add4866f4'},{'type':'md5','hash':'b5393216a1be4f2cbe09926b4baf5554'},{'type':'md5','hash':'aea4fa2f74b681d4327cfc178d6cbcaa'},{'type':'md5(md5($pass))','hash':'e10adc3949ba59abbe56e057f20f883e'},{'type':'md5','hash':'e2fc714c4727ee9395f324cd2e7f331f'},{'type':'md5','hash':'116e055b63d8698142614628d179f5f9'},{'type':'md5','hash':'5a90d2dde2355447e668cdc722cad314'},{'type':'md5','hash':'63ed0a956627c5d924dcf69add4866f4'},{'type':'md5','hash':'b5393216a1be4f2cbe09926b4baf5554'},{'type':'md5','hash':'aea4fa2f74b681d4327cfc178d6cbcaa'},{'type':'md5(md5($pass))','hash':'e10adc3949ba59abbe56e057f20f883e'},{'type':'md5','hash':'e2fc714c4727ee9395f324cd2e7f331f'},{'type':'md5','hash':'116e055b63d8698142614628d179f5f9'},{'type':'md5','hash':'5a90d2dde2355447e668cdc722cad314'},{'type':'md5','hash':'63ed0a956627c5d924dcf69add4866f4'},{'type':'md5','hash':'b5393216a1be4f2cbe09926b4baf5554'},{'type':'md5','hash':'aea4fa2f74b681d4327cfc178d6cbcaa'},{'type':'md5(md5($pass))','hash':'e10adc3949ba59abbe56e057f20f883e'},{'type':'md5','hash':'e2fc714c4727ee9395f324cd2e7f331f'}]
hash_list1=[{'type':'md5(md5($pass))','hash':'59082e1e76ad7ce1152f7c4892192a20'}]
log("---------------START---------------")
log(time.strftime("%H:%M:%S"))
for hash in hash_list1:
    decode(hash.get('type'),hash.get('hash'))
log(time.strftime("%H:%M:%S"))
log("---------------END---------------")
