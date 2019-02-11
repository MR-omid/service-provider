import tempfile
import time
import os

from PIL import Image

from components.Qhttp import Qhttp
from components.utils import ApiLogging
from extensions.hrobot.v_1_0.Hrobot import Hrobot
from modules.hash.v_1_0.captcha2upload import CaptchaUpload

# email = 'ali_sev@yahoo.com'
# password = '123456dzz'
from vendor.custom_exception import ResultNotFoundError, InvalidInputError, InsufficientCredit, NetworkError

VERIFY = 'verify'
PAYMENT = 'payment'
NOT_FOUND = 'Not Found'


class Hash(object):

    def __init__(self, username, password):
        self.email = username
        self.password = password
        self.current_milli_time = lambda: int(round(time.time() * 1000))
        self.unique_time = self.current_milli_time()
        cookie_path = os.path.dirname(__file__)
        self.robot = Hrobot(cookie_path, "http://cmd5.org")

    def is_logeed_in(self):
        self.unique_time = self.current_milli_time()
        if self.robot.find_by_xpath('//a[@href="exit.aspx"]') is not None:
            self.robot.save_cookies_to_file(self.robot.get_cookies())
            return True
        else:
            self.set_cookie()
            if self.robot.find_by_xpath('//a[@href="exit.aspx"]') is not None:
                self.robot.save_cookies_to_file(self.robot.get_cookies())
                return True
        return False

    def set_cookie(self):
        for cookie in self.robot.load_cookies_from_file():
            self.robot.set_cookie(cookie)
        self.robot.set_timeout(30)
        self.robot.go_to('/')

    def login(self):
        if self.is_logeed_in():
            ApiLogging.info ('cookie login')
            return True
        else:
            ApiLogging.info ('captcha login')
            self.robot.go_to('/login.aspx')
            email_field = self.robot.find_by_css('#ctl00_ContentPlaceHolder1_TextBoxCmd5_E')
            password_field = self.robot.find_by_css('#ctl00_ContentPlaceHolder1_TextBoxCmd5_P')
            email_field.set_value(self.email)
            password_field.set_value(self.password)
            self.fill_captcha_if_needed()
            submit_button = self.robot.find_by_css("#ctl00_ContentPlaceHolder1_Button1")
            submit_button.click()
            self.robot.save_cookies_to_file(self.robot.get_cookies())
            if self.is_logeed_in():
                ApiLogging.info ('logged in')
                return True
        return False

    def decode(self, hash_type, hash_code):
        if self.login():
            hash_field = self.robot.find_by_css('#ctl00_ContentPlaceHolder1_TextBoxInput')
            if hash_field is not None:
                type_field = self.robot.find_by_css('#ctl00_ContentPlaceHolder1_InputHashType')
                hash_field.set_value(hash_code)
                type_field.set_value(hash_type)
                self.fill_captcha_if_needed()
                submit_button = self.robot.find_by_css("#ctl00_ContentPlaceHolder1_Button1")
                submit_button.click()
                result = self.robot.find_by_css('#ctl00_ContentPlaceHolder1_LabelAnswer')
                ApiLogging.info ("result in hash: %s"%result.get_text())
                ApiLogging.info('type: '+ str(hash_type) + ' code: '+ str(hash_code))
                chk_result = self.check_result(result)
                if chk_result == VERIFY:
                    self.decode(hash_type, hash_code)
                elif chk_result == PAYMENT:
                    pr = self.robot.find_by_contain_text('a', 'Purchase')
                    ApiLogging.info('click payment' + str(pr.get_text()))
                    if pr:
                        pr.click()
                    result = self.robot.find_by_css('#ctl00_ContentPlaceHolder1_LabelAnswer')
                    chk_result = self.check_result(result)
                    if chk_result is None:
                        return result.get_text()
                elif chk_result == NOT_FOUND:
                    return None
                else:
                    return result.get_text().split('\n')[0]

        else:
            ApiLogging.warning ('login fail')

    def check_result(self, result):
        if result.get_text() == 'Verify code error!':
            return VERIFY
        elif 'payment' in result.get_text():
            ApiLogging.info('found payment')
            return PAYMENT
        elif 'Not Found' in result.get_text():
            return NOT_FOUND
        else:
            return None

    def fill_captcha_if_needed(self):
        captcha_field = self.robot.find_by_css('#ctl00_ContentPlaceHolder1_TextBoxCode')
        if captcha_field is not None:
            ApiLogging.warning ('captcha needed')
            self.robot.set_viewport_size(1280,800)
            img = self.robot.find_by_css("#Image1")
            rect = img.get_position()
            box = (int(rect['left']), int(rect['top']), int(rect['right']), int(rect['bottom']))
            filename = tempfile.mktemp('.png')
            self.robot.save_as_png(filename, 1280, 800)
            image = Image.open(filename)
            os.unlink(filename)
            captcha_image = image.crop(box)
            captcha_image.save('%s.png' % self.unique_time, 'png')
            captcha_field.set_value(self.resolve_captcha('%s.png' % self.unique_time))
            os.remove('%s.png' % self.unique_time)

    def resolve_captcha(self, file):
        api_key = "2632143214b9b24e9dc7590396f1dd22"
        captcha_object = CaptchaUpload(key=api_key,waittime=3)
        captcha = captcha_object.solve(file)
        ApiLogging.info('finded capcha: ' + str(captcha))
        return captcha

    @staticmethod
    def get_result_by_api(api_key, email, hash_code):
        url = 'https://www.cmd5.org/api.ashx?email='+email+'&key='+api_key+'&hash='+hash_code
        result = Qhttp.get(url)
        if result.status_code == 200:
                if ':' in result.content.decode():
                    error_code = result.content.decode().split(':')[-1]
                    if error_code == '-1':
                        raise InvalidInputError(' invalid input ')
                    if error_code == '-2':
                        raise InsufficientCredit('InsufficientCredit')
                    if error_code == '-3':
                        raise NetworkError('server failed on cmd5.org')
                    if error_code == '-4':
                        raise InvalidInputError('unknown sipher text')
                    if error_code == '-7':
                        raise InvalidInputError('hash type not supported')
                    if error_code == '-999':
                        raise NetworkError('some thing wrong with cmd5.org')
                try:
                    return_result = {'results': result.json()}
                    return return_result
                except Exception:
                    ResultNotFoundError(' unknown result format ')
        else:
            raise NetworkError(result.status_code)

