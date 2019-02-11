import hashlib
import os
import pickle
import sys

import dill
from PyQt5.QtWidgets import QApplication

from core.constants import BASE_APP_PATH
from extensions.hrobot.v_2_0.Utils import Utils

ps = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(ps)

from PyQt5.QtCore import QObject, QThread

from extensions.hrobot.v_2_0.Hrobot import Hrobot
from vendor.custom_exception import NetworkError


class Truecaller(QObject):
    def __init__(self, email, password, proccess_id, parent=None):

        super().__init__()
        try:
            print('TrueCaller: ', int(QThread.currentThreadId()))
            self.email = email
            self.password = password
            self.proccess_id = proccess_id

            # save cookies for preventing repetitive login from one client
            cookies_dir = BASE_APP_PATH + "/modules/truecaller/v_1_0/cookies/"
            cookie_hashname = str(hashlib.md5(self.email.encode('utf-8')).hexdigest()) + str(
                hashlib.md5(self.password.encode('utf-8')).hexdigest()) + '.pkl'
            self.cookie_path = cookies_dir + cookie_hashname
            os.makedirs(cookies_dir, exist_ok=True)

            # profile name
            # profile_name = str(hashlib.md5(self.email.encode('utf-8')).hexdigest()) + str(hashlib.md5(self.password.encode('utf-8')).hexdigest())
            # self.robot = Hrobot(gui=True, private=True, profile_name=profile_name)

            self.robot = Hrobot(gui=True, private=True)
            print('before')

            self.set_cookie(self.cookie_path)

            self.robot.go_to("https://www.truecaller.com")
            print('after ')

        except Exception as e:  # can not go to mbasic.facebook.com
            raise NetworkError(str(e))

    def update_progressbar(self, message, percent):
        """
        :set request progress
        """
        if self.__parent:
            self.__parent.progress = {'state': message, 'percent': percent}

    def check_action(self):
        """
        :check if new action submitted
        """
        if self.__parent:
            self.__parent.check_point()

    def store_cookie(self, path):
        try:
            cookie_file = open(path, 'wb')
            print('before get cookie')
            pickle.dump(self.robot.get_cookies(as_json=True), cookie_file, protocol=pickle.HIGHEST_PROTOCOL)
        except Exception as e:
            print(e)

    def set_cookie(self, path):
        try:
            cookie_file = open(path, 'rb')
            cookies = pickle.load(cookie_file)

            cookies = self.robot.json_to_cookie(cookies)
            print(cookies)
            print('after json to cookie')
            for cookie in cookies:
                self.robot.set_cookie(cookie)

            # self.robot.go_to(self.robot.get_url())  # refresh
        except Exception as e:
            print(e, 'can not set cookie')

    def __check_login(self):

        # check that sign in text is in page or not
        Sign_in = self.robot.find_by_contain_text('a', 'Sign in')
        if Sign_in:  # not login

            # self.set_cookie(self.cookie_path)

            try:
                # self.set_cookie(self.cookie_path)
                Sign_in = self.robot.find_by_contain_text('a', 'Sign in')
                if not Sign_in:
                    print('**is login')
                    return True
                else:
                    print('**not login')
                    return False
            except Exception as e:
                print(e, '**check login')

        else:  # login
            return True

    def __login(self):
        # cookies = pickle.load(open(BASE_APP_PATH + '/yuhjkyuky.pkl','rb'))
        # for cookie in cookies:
        #     # self.robot.set_cookie(cookie)
        #     # c = cookie()
        #     print(cookie.name())
        #
        # return True
        if not self.__check_login():
            print('**start login')
            sign_in = self.robot.find_by_css(
                'a.TopNav__Link.TopNav__SignIn')
            sign_in.click()

            gmail = self.robot.wait_until_css("div.sign-in-dialog-provider")
            gmail.click()

            email = self.robot.wait_until_css('input#identifierId')
            email.set_value(self.email)

            next = self.robot.find_by_contain_text('span', 'Next')
            if next:
                next.click()

            passwords = self.robot.wait_until_css('div#password')

            password = passwords.find_by_css('div div div input')
            password.set_value(self.password)


            next = self.robot.find_by_css('div#passwordNext')


            if next:
                next.click()

            if self.__check_login():
                self.store_cookie(self.cookie_path)
                print('**get cookie')
            print('**end login')
            return True

        else:
            # self.store_cookie(self.cookie_path)
            return True

    def search(self, region_letter, number):
        if self.__login():
            print('**enter number and region')
            region = self.robot.wait_until_xpath("/html/body/div[1]/div[4]/div[1]/div/div[2]/div[1]/div/select")
            region_options = region.find_all_by_css('option')
            for o in region_options:
                if o.get_value() == region_letter:
                    o.select_option()

            #
            input_number = self.robot.find_by_xpath("/html/body/div[1]/div[4]/div[1]/div/div[2]/div[1]/input")
            input_number.set_value(number)
            #     print(input_number.get_value())
            print('set number')
            input_number.enter()
            print('before wait')
            Utils.wait(2001)

            print('8888888888')
            result = {}
            print('before find')
            profilename = self.robot.wait_until_css('div.ProfileName')
            print('after find ', profilename.get_attribute('class'))
            if profilename:
                print('a')
                print('b')
                profilename_box = profilename.find_by_css('div')
                print('cc')
                profilename_text = profilename_box.get_text()
                print('after tex pro')
                print(1111, profilename_text)
                if 'is not yet available' in profilename_text:
                    print('b')
                    result['profileName'] = 'is not yet available'
                else:
                    print('c')
                    result['profileName'] = profilename_text
                    list_info = self.robot.find_by_css('div.ProfileDetails.ProfileContainer')
                    if list_info:
                        number_info = self.robot.find_by_xpath('/div[1]/div/div[2]')
                        if number_info:
                            number = number_info.find_by_xpath('/div[1]')
                            operator = number_info.find_by_xpath('/div[2]')

                            if number:
                                result['number'] = number
                            if operator:
                                result['operator'] = operator

                        location = self.robot.find_by_xpath('/div[2]/a/div[2]/div')
                        if location:
                            result['location'] = location
            else:
                print('fffffff')


            print('***', result)
            with open(BASE_APP_PATH + '/modules/truecaller/v_1_0/storage/' + self.proccess_id + '.pkl', 'wb') as f:
                pickle.dump(result, f)
                f.close()
            Utils.wait(3000)
            print('eeeeeeeeeeeeeeeeeeeeeeeeeeeend')
            sys.exit()


if __name__ == '__main__':
    try:
        os.environ['DISPLAY']
    except Exception:
        from vendor.xvfbwrapper import Xvfb
        Xvfb().start()
    app = QApplication([])
    args = sys.argv

    email = args[1]
    password = args[2]
    region = args[3]
    number = args[4]
    proccess_id = args[5]

    # email = "raminfawork@gmail.com"
    # password = 'DPE12345678'
    # region = 'ir'
    # number = '9369215627'
    # proccess_id = '123456'

    truecaller = Truecaller(email=email, password=password, proccess_id=proccess_id)
    result = truecaller.search(region_letter=region, number=number)
    # sys.exit(app.exec())
