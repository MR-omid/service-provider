import hashlib
import os
import re
import time

from PIL import Image

from components.Qhttp import Qhttp
from core.constants import BASE_APP_PATH
from extensions.hrobot.v_1_0.Hrobot import Hrobot
from vendor.custom_exception import NetworkError, LoginError, ResultNotFoundError, BadRequest, FacebookAccountLocked, \
    FacebookSecurityNeededSolved


class Facebook:
    def __init__(self, username, password, parent=None):

        try:
            self.username = username
            self.password = password
            self.temp_robot = Hrobot()
            # use storage for saving images
            proccess_id = parent.task_model.process_id
            self.storage = [
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
                '/modules/storage/' + proccess_id]
            # save cookies for preventing repetitive login from one client
            cookie_path = BASE_APP_PATH + "/modules/facebook/v_1_0/cookies/"
            cookie_path_hash = str(hashlib.md5(self.username.encode('utf-8')).hexdigest()) + str(
                hashlib.md5(self.password.encode('utf-8')).hexdigest())
            os.makedirs(cookie_path + cookie_path_hash, exist_ok=True)
            self.robot = Hrobot(cookie_path + cookie_path_hash, "https://mbasic.facebook.com")
            self.robot.set_timeout(30)
            self.robot.block_url("googleads.g.doubleclick.net")
            self.robot.go_to("/")
            self.default_number = 20
            self.check_number = 0
            self.parent = parent
        except Exception as e:  # can not go to mbasic.facebook.com
            raise NetworkError(str(e))

    def update_progressbar(self, message, percent):
        """
        :set request progress
        """
        if self.parent:
            self.parent.progress = {'state': message, 'percent': percent}

    def check_action(self):
        """
        :check if new action submitted
        """
        if self.parent:
            self.parent.check_point()

    def __login(self):
        """
        :return:boolean for status of login to facebook
        """
        if self.__check_login():
            if self.robot.find_by_css("*[name='login']"):
                pass
            else:
                self.update_progressbar('login successfully',
                                        30)
                return True

        else:  # not login yet, try to login
            email = self.robot.find_by_css("input[name='email']")
            password = self.robot.find_by_css("input[name='pass']")
            log_in = self.robot.find_by_css("*[name='login']")
            if email and password and log_in:
                email.set_value(self.username)
                password.set_value(self.password)
                if log_in:
                    log_in.click()
                if self.robot.find_by_contain_text('*', 'Your Account Is Temporarily Locked'):
                    raise FacebookAccountLocked('your account has been locked by facebook')
                if self.robot.find_by_contain_text('*', 'Upload A Photo Of Yourself'):  # faces facebook captcha
                    raise FacebookSecurityNeededSolved('need to solved security procedure')

                elif self.robot.find_by_contain_text('*', 'We want to make sure your account is secure'):
                    raise FacebookSecurityNeededSolved('need to solved security procedure')
                elif self.robot.find_by_css("*[name='login']"):  # redirected to login page again
                    pass
                else:
                    self.robot.go_to("/")
                    self.robot.save_cookies_to_file(self.robot.get_cookies())
                    if self.robot.find_by_css("*[name='login']"):
                        pass
                    elif self.__check_login():
                        self.update_progressbar('login successfully',
                                                30)
                        return True
            else:  # try another way, redirect to login page again
                self.robot.go_to('https://mbasic.facebook.com/login/?ref=dbl&fl&refid=8')
                email = self.robot.find_by_css("input[name='email']")
                password = self.robot.find_by_css("input[name='pass']")
                log_in = self.robot.find_by_css("*[name='login']")
                if email and password and log_in:
                    email.set_value(self.username)
                    password.set_value(self.password)
                    if log_in:
                        log_in.click()
                    if self.robot.find_by_contain_text('*', 'Your Account Is Temporarily Locked'):
                        raise FacebookAccountLocked('your account has been locked by facebook')
                    if self.robot.find_by_contain_text('*', 'Upload A Photo Of Yourself'):
                        raise FacebookSecurityNeededSolved('need to solved security procedure')
                    elif self.robot.find_by_contain_text('*', 'We want to make sure your account is secure'):
                        raise FacebookSecurityNeededSolved('need to solved security procedure')
                    elif self.robot.find_by_css("*[name='login']"):
                        return False
                    self.robot.go_to("/")
                    self.robot.save_cookies_to_file(self.robot.get_cookies())
                    if self.robot.find_by_css("*[name='login']"):
                        return False
                    elif self.__check_login():
                        self.update_progressbar('login successfully',
                                                30)
                        return True
        if self.robot.find_by_contain_text('*', 'Your Account Is Temporarily Locked'):
            raise FacebookAccountLocked('your account has been locked by facebook')

        if self.robot.find_by_contain_text('*', 'Upload A Photo Of Yourself'):
            raise FacebookSecurityNeededSolved('need to solved security procedure')

        if self.robot.find_by_contain_text('*', 'We want to make sure your account is secure'):
            raise FacebookSecurityNeededSolved('need to solved security procedure')

        self.update_progressbar('login failed', 30)
        return False

    # set cookie on hrobot
    def __set_cookie(self):
        for cookie in self.robot.load_cookies_from_file():
            self.robot.set_cookie(cookie)
        self.robot.set_timeout(30)
        self.robot.go_to("/")
        return True

    # check if this client logged in facebook
    def __check_login(self):
        if self.robot.find_by_contain_text('*', 'Logout'):
            self.robot.save_cookies_to_file(self.robot.get_cookies())
            return True

        else:
            try:  # use cookie and check again
                self.__set_cookie()
                if self.robot.find_by_contain_text('*', 'Logout'):
                    self.robot.save_cookies_to_file(self.robot.get_cookies())
                    return True
            except Exception:
                return False
        return False

    def profile(self, facebook_id):
        # choose that facebook_id belongs to what kind of profile
        """
        :param facebook_id: facebook id or alias name for one page or person
        :return: all profile information related to id or alias name
        """
        if self.__login():
            # decide for on_go link, base on facebook_id receive or alias
            if facebook_id.isdigit():
                self.robot.go_to("/profile.php?v=info&id=%d" % int(facebook_id))
            else:
                self.robot.go_to("/%s" % facebook_id)
            self.check_action()
            # check if page or profile, by position of profile picture
            page = self.robot.find_all_by_xpath(
                '/html/body/div/div/div[2]/div/div[1]/div[1]/div[1]/div[2]/div[1]/div/a/img')
            page_type_2 = self.robot.find_all_by_xpath(
                '/html/body/div/div/div[2]/div/div[1]/div[1]/div[1]/div/div[1]/div/a/img')
            profile = self.robot.find_all_by_xpath(
                '/html/body/div/div/div[2]/div/div[1]/div[1]/div[2]/div/div/div/a/img')
            # calling appropriate method
            if page or page_type_2:
                return self.check_page(facebook_id)
            elif profile:
                return self.check_profile(facebook_id)
            else:  # page not found or automatically generate by facebook, so can not extract info
                raise ResultNotFoundError('can not extract info from this facebook_id')
        else:
            raise LoginError('can not login')

    def check_page(self, facebook_id):
        # this function get all page information
        """
        :param facebook_id: facebook id or alias name for one page
        :return: all page information related to id or alias name
        """
        self.update_progressbar('request submitted successfully, check profile ',
                                20)
        if self.__login():

            # decide for on_go link, base on facebook_id receive or alias, save refrence and redirected link
            if facebook_id.isdigit():
                self.robot.go_to("/profile.php?v=info&id=%d" % int(facebook_id))
                redirected = self.robot.get_url()
            else:
                self.robot.go_to("/%s" % facebook_id)
                redirected = self.robot.get_url()
            ref = 'mbasic.facebook.com/' + str(facebook_id)
            self.check_action()
            # defining dict for output
            image_profile = {'image_profile': '', 'type': 13, 'more': {'ref': ref, 'url': ''}}
            image_profile_thumbnail = {'image_profile_thumbnail': '', 'type': 13, 'more': {'ref': ref, 'url': ''}}

            cover_photo = {'cover_photo': '', 'type': 13, 'more': {'ref': ref, 'url': ''}}
            cover_photo_thumbnail = {'cover_photo_thumbnail': '', 'type': 13, 'more': {'ref': ref, 'url': ''}}

            is_verified = {'is_verified': False, 'type': 0}
            redirecred_to = {'redirected_to': redirected, 'type': 0}
            name = {'name': '', 'type': 11}
            alias = {'alias': '', 'type': 0}
            redirecred_from = {'redirecred_from': ref, 'type': 1}
            phone = {'phone_number': '', 'type': 4}
            address = {'address': '', 'type': 8}
            about = {'type': 0, 'about': []}
            result = {'properties': [],
                      'special_properties': [{'sub_type': 1, 'type': 0}, {'is_page': True, 'type': 0}],
                      'results': [], 'has_media': True}

            # *** extracting page profile picture ***
            page_profile = self.robot.find_all_by_xpath(
                '/html/body/div/div/div[2]/div/div[1]/div[1]/div[1]/div[2]/div[1]/div/a')
            if not page_profile:
                page_profile = self.robot.find_all_by_xpath(
                    '/html/body/div/div/div[2]/div/div[1]/div[1]/div[1]/div/div[1]/div/a')
            if page_profile:
                try:  # go to profile picture page and save high quality picture
                    page_profile_pic_herf = page_profile[-1].get_attr('href')
                    self.robot.go_to('https://mbasic.facebook.com/' + str(page_profile_pic_herf))
                    try:
                        page_profile_pic = self.robot.find_all_by_xpath(
                            '/html/body/div/div/div[2]/div/div[1]/div/div/div[3]/div[1]/div[2]/span/div/span/a[1]')
                        if page_profile_pic:
                            img_pro_list = self.__save_image(page_profile_pic[-1].get_attr('href'), alias['alias'])
                            image_profile['image_profile'] = img_pro_list[0]
                            image_profile['more']['url'] = page_profile_pic[-1].get_attr('href')
                            image_profile['more']['file_name'] = img_pro_list[2]

                            image_profile_thumbnail['image_profile_thumbnail'] = img_pro_list[1]
                            image_profile_thumbnail['more']['url'] = page_profile_pic[-1].get_attr('href')
                            image_profile_thumbnail['more']['file_name'] = img_pro_list[2]
                            result['properties'].append(image_profile)
                            result['properties'].append(image_profile_thumbnail)

                        # set robot in previous link
                        self.robot.go_back()
                    except Exception:
                        self.robot.go_back()
                except Exception:
                    pass  # can not extract link, so return image_profile block empty
            self.check_action()

            # *** extracting page cover picture ***
            page_cover = self.robot.find_all_by_xpath(
                '/html/body/div/div/div[2]/div/div[1]/div[1]/div[1]/div[1]/a[1]')
            if page_cover:
                try:  # go to profile cover page and save high quality picture
                    cover_profile_herf = page_cover[-1].get_attr('href')
                    self.robot.go_to('https://mbasic.facebook.com/' + str(cover_profile_herf))
                    try:
                        page_cover_pic = self.robot.find_all_by_xpath(
                            '/html/body/div/div/div[2]/div/div[1]/div/div/div[3]/div[1]/div[2]/span/div/span/a[1]')
                        if page_cover_pic:
                            cov_pic_list = self.__save_image(page_cover_pic[-1].get_attr('href'),
                                                             alias['alias'])
                            cover_photo['cover_photo'] = cov_pic_list[0]
                            cover_photo['more']['url'] = page_cover_pic[-1].get_attr('href')
                            cover_photo['more']['file_name'] = cov_pic_list[2]

                            cover_photo_thumbnail['cover_photo_thumbnail'] = cov_pic_list[1]
                            cover_photo_thumbnail['more']['url'] = page_cover_pic[-1].get_attr('href')
                            cover_photo_thumbnail['more']['file_name'] = cov_pic_list[2]

                            result['properties'].append(cover_photo)
                            result['properties'].append(cover_photo_thumbnail)
                        # set robot in previous link
                        self.robot.go_back()
                    except Exception:
                        self.robot.go_back()
                except Exception:
                    pass  # can not extract link, so return cover_profile block empty
            self.update_progressbar('extracting cover and profile from page ',
                                    40)
            # *** extracting page profile picture ***
            try:
                verify_list = self.robot.find_all_by_css('div span span span')
                for i in verify_list:
                    if i.get_attr('aria-label') == 'Verified Page':
                        is_verified['is_verified'] = True
            except Exception:
                pass  # can not extract is verify, so return is_verified false block empty

            # *** extracting alias ***
            try:
                alias_name = self.robot.find_all_by_xpath('/ html / body / div / div / div[2] / div / div[1] /'
                                                          ' div[1] / div[1] / div[2] / div[2] / div / a / span')
                if not alias_name:
                    alias_name = self.robot.find_all_by_xpath(
                        '/html/body/div/div/div[2]/div/div[1]/div[1]/div[1]/div/div[2]/div/a/span')
                if alias_name:
                    alias['alias'] = str(alias_name[-1].get_text()).replace('@', '')
                else:
                    alias['alias'] = facebook_id
            except Exception:
                pass  # can not extract name, so return name block with alias value

            # *** extracting name ***
            try:
                name_profile = self.robot.find_all_by_xpath('/html/body/div/div/div[2]/div/'
                                                            'div[1]/div[1]/div[1]/div[2]/div[2]/h1/div/span[1]')
                if not name_profile:
                    name_profile = self.robot.find_all_by_xpath(
                        '/html/body/div/div/div[2]/div/div[1]/div[1]/div[1]/div/div[2]/h1/div/span[1]')
                if name_profile:
                    name['name'] = name_profile[-1].get_text()
                else:
                    name['name'] = alias['alias']
            except Exception:
                name['name'] = alias['alias']  # can not extract name, so return name block with alias value
            self.check_action()
            self.update_progressbar('extracting about from page ',
                                    70)
            # *** extracting about ***
            try:
                about_list = self.robot.find_all_by_xpath('/html/body/div/div/div[2]/div/'
                                                          'div[1]/div[1]/div[2]/div/div[3]')
                if not about_list:
                    about_list = self.robot.find_all_by_css('div.dc:nth-child(3)')
                if about_list:  # created list pf about, and extract phone and address if exist
                    listed_item = about_list[-1].get_text().split('\n')
                    if listed_item:
                        for item in listed_item:
                            if item in ['\t', '', 'About']:
                                listed_item.remove(item)
                        if listed_item:
                            for i in range(0, len(listed_item)):
                                if listed_item[i].startswith('Call'):
                                    phone['phone_number'] = listed_item[i].replace('Call', '')
                                    result['special_properties'].append(phone)

                                if listed_item[i] == 'Get directions':  # last item was address, if current item is GD
                                    try:
                                        address['address'] = listed_item[i - 1]
                                        result['special_properties'].append(address)
                                    except IndexError:
                                        pass
                                if listed_item[i] == '':
                                    continue
                                about['about'].append(listed_item[i])
            except Exception:
                pass  # leave about empty

            result['special_properties'].append(is_verified)
            result['special_properties'].append(redirecred_to)
            result['special_properties'].append(name)
            result['special_properties'].append(alias)
            result['special_properties'].append(redirecred_from)
            result['special_properties'].append(about)

            return result

    # this function get all profile information and use  many other functions with prefix of extract
    def check_profile(self, facebook_id):
        """
        :param facebook_id: facebook id or alias name for one page or person
        :return: all profile information related to id or alias name
        """
        self.update_progressbar('request submitted successfully, check profile ',
                                20)
        # defining dictionary and list to create appropriate output
        results = []
        properties = []
        special_properties = []
        return_result = {}
        temp_result = {}
        sub_type = {'sub_type': 1, 'type': 0}
        image_profile = {'image_profile': '', 'type': 13, 'more': {'url': '', 'ref': ''}}
        image_profile_thumbnail = {'image_profile_thumbnail': '', 'type': 13, 'more': {'url': '', 'ref': ''}}
        cover_photo = {'cover_photo': '', 'type': 13, 'more': {'url': '', 'ref': ''}}
        cover_photo_thumbnail = {'cover_photo_thumbnail': '', 'type': 13, 'more': {'url': '', 'ref': ''}}
        name = {'name': '', 'type': 11}
        about_dic = {'about': '', 'type': 0}
        gender = {'gender': '', 'type': 0}
        language = {'language': '', 'type': 0}
        birthday = {'birthday': '', 'type': 0}
        is_verified = {'is_verified': '', 'type': 0}
        intrested = {'intrested_in': '', 'type': 0}
        information = {'other_info': [], 'type': 0}
        is_page = {'is_page': False, 'type': 0}
        redirected_to = {'redirected': '', 'type': 1}
        redirected_from = {'redirected_from': '', 'type': 1}

        if self.__login():
            try:
                if facebook_id.isdigit():
                    self.robot.go_to("/profile.php?v=info&id=%d" % int(facebook_id))
                    ref = 'https://mbasic.facebook.com/' + facebook_id
                    redirected = self.robot.get_url()
                    redirected_to['redirected'] = redirected
                    redirected_from['redirected_from'] = ref
                else:
                    self.robot.go_to("/%s/about" % facebook_id)
                    ref = 'https://mbasic.facebook.com/' + facebook_id
                    redirected = self.robot.get_url()
                    redirected_to['redirected'] = redirected
                    redirected_from['redirected_from'] = ref
            except Exception:
                raise BadRequest('bad request')

            self.check_action()
            # check if profile exist
            self.check_profile_availability()

            # create family member block in result list
            # extract family node from current page
            family_members = self.robot.find_all_by_css('div[id="family"] div h3 a')
            if family_members:
                self.update_progressbar('getting family member and saving their image',
                                        40)
                try:  # extract family info from node
                    temp_result['family_members'] = (self.__extract_family(family_members))
                    for member in temp_result['family_members']:
                        family_member = {"data": '', 'ref': {'task': 'facebook_profile', 'section': 'kinship',
                                                             'facebook_account': facebook_id}, "type": 5,
                                         "properties": [],
                                         "special_properties": [{"sub_type": 1, "type": 0}]}
                        # set extracted values to result
                        alias = ''
                        if 'link' in member:
                            try:
                                alias = re.search('/(.+?)\?', member['link']).group(1)
                            except AttributeError:
                                alias = member['link'].replace('/', '')
                            if alias == 'profile.php':
                                try:
                                    alias = re.search('id=(.+?)&', member['link']).group(1)
                                except AttributeError:
                                    alias = member['link'].replace('/profile.php?id=', '')
                            family_member['data'] = alias
                        if 'kinship' in member:
                            family_member["special_properties"].append({"kinship": member["kinship"], "type": 0})
                        else:
                            family_member["special_properties"].append({"kinship": '', "type": 0})
                        if 'name' in member:
                            family_member["properties"].append({"name": member["name"], "type": 11})
                        else:
                            family_member["properties"].append({"name": '', "type": 11})
                        if 'image' in member:
                            image_member = self.__save_image(member['image'], alias)

                            family_member["properties"].append(
                                {"image_profile": image_member[0], "type": 13,
                                 'more': {'ref': 'mbasic.facebook.com/' + alias, 'url': member["image"],
                                          'file_name': image_member[2]}})

                            family_member["properties"].append(
                                {"image_profile_thumbnail": image_member[1], "type": 13,
                                 'more': {'ref': 'mbasic.facebook.com/' + alias, 'url': member["image"],
                                          'file_name': image_member[2]}})
                        else:
                            family_member["properties"].append(
                                {"image_profile": '', "type": 13,
                                 'more': {'ref': 'mbasic.facebook.com/' + alias, 'url': ''}})
                        results.append(family_member)
                except Exception:  # if face to an unexpected exception
                    pass

            # create work block in properties list
            # extract work node from current page
            works1 = self.robot.find_all_by_css("div[id='work']")
            works = self.robot.find_all_by_css("div[id='work'] span a")
            if works1:
                try:  # extract info from nodes
                    temp_result['Works'] = (self.__extract_work(works))
                    work = {'works': [], "type": 11}
                    for job in temp_result['Works']:
                        work_main_data = {'data': '', 'type': 11,
                                          'properties': {'profile_id': '', 'date_start': '', 'date_end': ''},
                                          'ref': {'task': 'facebook_profile', 'facebook_account': facebook_id,
                                                  'section': 'work_name'}}
                        single_work = {'title': '', 'more': {'profile_id': '', 'date_start': '', 'date_end': ''}}
                        if 'title' in job:
                            single_work['title'] = job["title"]
                            work_main_data['data'] = job["title"]

                        if 'link' in job:
                            single_work["more"]['profile_id'] = job['link']
                            work_main_data['properties']['profile_id'] = job['link']

                        if 'date' in job:
                            if '-' in job['date']:
                                if len(job['date'].split("-")) == 2:
                                    # case1 : 2017 - present
                                    if job['date'].split("-")[0].replace(' ', '').isdigit():
                                        single_work["more"]['date_start'] = job['date'].split("-")[0]
                                        work_main_data['properties']['date_start'] = job['date'].split("-")[0]
                                        single_work["more"]['date_end'] = job['date'].split("-")[1]
                                        work_main_data['properties']['date_end'] = job['date'].split("-")[1]
                                    # case2 : may, 2017 - present
                                    elif ',' in job['date'].split("-")[0]:
                                        if job['date'].split("-")[0].split(',')[1].replace(' ', '').isdigit():
                                            single_work["more"]['date_start'] = job['date'].split("-")[0]
                                            work_main_data['properties']['date_start'] = job['date'].split("-")[0]
                                            single_work["more"]['date_end'] = job['date'].split("-")[1]
                                            work_main_data['properties']['date_end'] = job['date'].split("-")[1]
                                    # case1 : may 2017 - present
                                    elif ' ' in job['date'].split("-")[0]:
                                        if job['date'].split("-")[0].split(' ')[1].replace(' ', '').isdigit():
                                            single_work["more"]['date_start'] = job['date'].split("-")[0]
                                            work_main_data['properties']['date_start'] = job['date'].split("-")[0]
                                            single_work["more"]['date_end'] = job['date'].split("-")[1]
                                            work_main_data['properties']['date_end'] = job['date'].split("-")[1]

                        work['works'].append(single_work)
                        results.append(work_main_data)
                    properties.append(work)
                except Exception:
                    # if face to an unexpected exception
                    pass

            self.check_action()
            # create about block in properties list
            # extract about node from current page
            about = self.robot.find_all_by_css('div[id="bio"]')
            if about:
                try:  # extracting info from nodes
                    about_dic['about'] = (self.__extarct_about())
                except Exception:
                    pass
            properties.append(about_dic)

            # create name block in properties list
            try:
                name['name'] = self.__get_name()
                results.append({'data': name['name'], 'type': 11,
                                'ref': {'task': 'facebook_profile', 'facebook_account': facebook_id,
                                        'section': 'real_name'}})
            except Exception:
                pass
            properties.append(name)

            # create image_profile block in properties list
            image_profile_list = self.__save_image(self.__image_profile(), name['name'])
            cover_photo_list = self.__save_image(self.__cover_photo(), name['name'])
            image_profile['image_profile'] = image_profile_list[0]
            image_profile['more']['url'] = self.__image_profile()
            image_profile['more']['ref'] = ref
            image_profile['more']['file_name'] = image_profile_list[2]
            properties.append(image_profile)

            image_profile_thumbnail['image_profile_thumbnail'] = image_profile_list[1]
            image_profile_thumbnail['more']['url'] = self.__image_profile()
            image_profile_thumbnail['more']['ref'] = ref
            image_profile_thumbnail['more']['file_name'] = image_profile_list[2]

            properties.append(image_profile_thumbnail)

            # create cover_photo block in properties list
            cover_photo['cover_photo'] = cover_photo_list[0]
            cover_photo['more']['url'] = self.__cover_photo()
            cover_photo['more']['ref'] = ref
            cover_photo['more']['file_name'] = cover_photo_list[2]

            properties.append(cover_photo)

            cover_photo_thumbnail['cover_photo_thumbnail'] = cover_photo_list[1]
            cover_photo_thumbnail['more']['url'] = self.__cover_photo()
            cover_photo_thumbnail['more']['ref'] = ref
            cover_photo_thumbnail['more']['file_name'] = cover_photo_list[2]

            properties.append(cover_photo_thumbnail)

            self.check_action()
            self.update_progressbar('create family member, works, name, image_profile, cover, about blocks', 50)

            # create other_info block in properties list
            temp_result['info'] = self.__get_info()
            if temp_result['info']:
                for inf in temp_result['info']:
                    information['other_info'].append({'info': inf, 'more': {}})
            else:
                information['other_info'].append({'info': '', 'more': {}})
            properties.append(information)
            # create places_lived block in properties list
            living = self.robot.find_by_css('div[id="living"]')
            if living:
                try:  # extract info from nodes
                    temp_result['places_lived'] = (self.__extract_lived_places())
                    living = {'places_lived': [], "type": 11}
                    for place in temp_result['places_lived']:
                        place_main_data = {'data': '', 'type': 8,
                                           'properties': {'profile_id': '', 'type': ''},
                                           'ref': {'task': 'facebook_profile', 'facebook_account': facebook_id,
                                                   'section': 'places_lived'}}
                        single_place = {'title': '', 'more': {}}
                        if 'city_name' in place:
                            single_place['title'] = place["city_name"]
                            place_main_data['data'] = place['city_name']
                        if 'link' in place:
                            single_place["more"]['profile_id'] = place['link']
                            place_main_data['properties']['profile_id'] = place['link']
                        if 'type' in place:
                            single_place["more"]['type'] = place['type']
                            place_main_data['properties']['type'] = place['type']
                        results.append(place_main_data)
                        living['places_lived'].append(single_place)
                    properties.append(living)
                except Exception:  # faces unexpected exception
                    properties.append(
                        {'places_lived': [{'title': '', 'more': {'profile_id': '', 'type': ''}}], "type": 11})
            else:
                properties.append({'places_lived': [{'title': '', 'more': {'profile_id': '', 'type': ''}}], "type": 11})

            # create education block in properties list
            # extract node from current page
            education = self.robot.find_all_by_css('div[id="education"] div span a')
            if education:
                try:  # extract info from nodes
                    temp_result['education'] = (self.__extract_education(education))
                    educations = {'education': [], "type": 11}
                    for educate in temp_result['education']:
                        educate_main_data = {'data': '', 'type': 11,
                                             'properties': {'profile_id': '', 'date_start': '', 'date_end': '',
                                                            'type': ''},
                                             'ref': {'task': 'facebook_profile', 'facebook_account': facebook_id,
                                                     'section': 'college_name'}}
                        single_edu = {'title': '',
                                      'more': {'profile_id': '', 'date_end': '', 'date_start': '', 'type': ''}}
                        if 'title' in educate:
                            single_edu['title'] = educate["title"]
                            educate_main_data['data'] = educate["title"]
                        if 'link' in educate:
                            single_edu["more"]['profile_id'] = educate['link']
                            educate_main_data['properties']['profile_id'] = educate['link']
                        if 'type' in educate:
                            single_edu["more"]['type'] = educate['type']
                            educate_main_data['properties']['type'] = educate['type']

                        # check if date format is correct
                        if 'date' in educate:
                            if '-' in educate['date']:
                                if len(educate['date'].split("-")) == 2:
                                    # case 1  2017 - present
                                    if educate['date'].split("-")[0].replace(' ', '').isdigit():
                                        single_edu["more"]['date_start'] = educate['date'].split("-")[0]
                                        educate_main_data['properties']['date_start'] = educate['date'].split("-")[0]
                                        single_edu["more"]['date_end'] = educate['date'].split("-")[1]
                                        educate_main_data['properties']['date_end'] = educate['date'].split("-")[1]
                                    # case 2  sep, 2005 - present
                                    elif ',' in educate['date'].split("-")[0]:
                                        if educate['date'].split("-")[0].split(',')[1].replace(' ', '').isdigit():
                                            single_edu["more"]['date_start'] = educate['date'].split("-")[0]
                                            educate_main_data['properties']['date_start'] = educate['date'].split("-")[
                                                0]
                                            single_edu["more"]['date_end'] = educate['date'].split("-")[1]
                                            educate_main_data['properties']['date_end'] = educate['date'].split("-")[1]
                                    # case 3  sep 2005- prsent
                                    elif ' ' in educate['date'].split("-")[0]:
                                        if educate['date'].split("-")[0].split(' ')[1].replace(' ', '').isdigit():
                                            single_edu["more"]['date_start'] = educate['date'].split("-")[0]
                                            educate_main_data['properties']['date_start'] = educate['date'].split("-")[
                                                0]
                                            single_edu["more"]['date_end'] = educate['date'].split("-")[1]
                                            educate_main_data['properties']['date_end'] = educate['date'].split("-")[1]
                        results.append(educate_main_data)
                        educations['education'].append(single_edu)
                    properties.append(educations)
                except Exception:  # faces to unexpected exception
                    pass
            else:  # there is no education
                pass
            quote = self.robot.find_by_css('div[id="quote"]')

            # create life_events block in properties list
            self.check_action()
            self.update_progressbar('create family member, works, name, image_profile, about,quote, education blocks',
                                    80)
            # extracting events
            known_event = []
            life_events = {'life_events': [], "type": 0}
            if about:
                a = self.robot.find_by_following_sibling("*[@id='bio']", "div")
                if 'Life Events' in a.get_text():
                    try:
                        temp_result['Life_events'] = self.__extract_life_events(a.get_xpath())

                        for events in temp_result['Life_events']:

                            try:
                                if events['desc'] in known_event:
                                    continue
                                else:
                                    single_event = {'events': '', 'more': {'profile_id': ''}}
                                    if 'desc' in events:
                                        single_event['events'] = events['desc']
                                        known_event.append(events['desc'])  # preventing repetetive event appended
                                    else:
                                        continue
                                    if 'link' in events:
                                        single_event["more"]['profile_id'] = events['link']
                                    if 'type' in events:
                                        single_event["more"]['type'] = events['type']
                                    life_events['life_events'].append(single_event)
                            except Exception:
                                continue
                    except Exception:
                        pass

            if quote:  # extract nodes
                d = self.robot.find_all_by_preceding_sibling("*[@id='quote']", "div")
                try:
                    events = d[-1].get_text()
                except Exception:
                    events = {}
                if 'Life Events' in events:  # extracting info from nodes
                    try:
                        temp_result['Life_events'] = self.__extract_life_events(d[-1].get_xpath())
                        for events in temp_result['Life_events']:
                            try:
                                if events['desc'] in known_event:  # preventing repetetive events appended
                                    continue
                                else:
                                    single_event = {'events': '', 'more': {'link': '', 'type': ''}}
                                    if 'desc' in events:
                                        single_event['events'] = events['desc']
                                        known_event.append(events['desc'])
                                    else:
                                        continue
                                    if 'link' in events:
                                        single_event["more"]['profile_id'] = events['link']
                                    if 'type' in events:
                                        single_event["more"]['type'] = events['type']
                                    life_events['life_events'].append(single_event)
                            except Exception:
                                continue
                    except Exception:
                        pass

            # check if events is not empty
            if len(life_events['life_events']) != 0:
                properties.append(life_events)

            # create special_properties list
            # extractin basic info nodes
            basic_info = self.robot.find_by_css("div[id='basic-info']")
            if basic_info:
                try:  # extracting info from nodes
                    temp_result['basic_info'] = (self.__extract_basic_info())
                    for info in temp_result['basic_info']:
                        if 'type' in info:
                            if info['type'] == 'Gender':
                                gender['gender'] = info['value']
                            elif info['type'] == 'Interested In':
                                intrested['intrested_in'] = info['value']
                            elif info['type'] == 'Languages':
                                language['language'] = info['value']
                            elif info['type'] == 'Birthday':
                                birthday['birthday'] = info['value']
                except Exception:
                    pass
            self.check_action()
            is_verified['is_verified'] = self.__verified()
            special_properties.append(language)
            special_properties.append(gender)
            special_properties.append(birthday)
            special_properties.append(intrested)
            special_properties.append(is_verified)
            special_properties.append(sub_type)
            special_properties.append(is_page)
            special_properties.append(redirected_from)
            special_properties.append(redirected_to)
            self.update_progressbar('done', 100)
        # create final output
        else:
            self.robot.save_as_png('logiiiiiiiiiiin.png')
            raise LoginError('can not login')
        return_result['results'] = results
        return_result['properties'] = properties
        return_result['special_properties'] = special_properties
        return_result['has_media'] = True
        return return_result

    def __extract_life_events(self, xpath):
        """
        :param xpath:xpath for life_events node
        :return:list of information related to life_events
        """
        events_list = []
        events_dic = {'all_information': self.robot.find_by_xpath(xpath).get_text()}
        events_list.append(events_dic)
        c = self.robot.find_elements_descendant(xpath, 'a')
        i = 0
        if c:
            for elem in c:
                event = {'desc': elem.get_text(), 'link': elem.get_attr('href')}
                i += 1
                events_list.append(event)
        return events_list

    def __extract_work(self, works):
        """
        :param works: list of nodes related to information of works
        :return: list of information related to work
        """
        a = self.robot.find_all_by_css('div[id="work"] a img ')
        i = 0
        works_lis = []
        for work in works:
            try:
                work_dic = {'title': work.get_text(), 'link': work.get_attr('href')}
                text_list = a[i].get_parent().get_parent().get_text().split('\n')
                del text_list[0]
                del text_list[-1]
                if len(text_list) == 3:
                    work_dic['date'] = text_list[2]
                elif len(text_list) == 2:
                    work_dic['date'] = text_list[1]
                else:
                    work_dic['date'] = text_list[2]
                works_lis.append(work_dic)
            except Exception:
                continue
            i += 1
        return works_lis

    # this function extract the profile name of id or alias
    def __get_name(self):
        """
        :return: profile name
        """
        if self.robot.find_by_css('span strong'):
            name = self.robot.find_by_css('span strong').get_text()
            return name

    # this function check that profile is verified or not
    def __verified(self):
        """
        :return:boolean for verification status of page
        """
        try:
            if self.robot.find_by_css("span[aria-label='Verified Profile']"):
                return True
            else:
                return False
        except Exception:
            return False

    # this function extract image profile of one id or alias
    def __image_profile(self):
        """
        :return:link of image url for profile
        """
        img_url = self.robot.find_by_xpath('/html/body/div/div/div[2]/div/div[1]/div[1]/div[2]/div/div[1]/div/a/img')
        img_href = self.robot.find_by_xpath('/html/body/div/div/div[2]/div/div[1]/div[1]/div[2]/div/div[1]/div/a')
        if img_url:
            try:
                sub = (img_href.get_attr('href'))
                self.temp_robot.go_to('https://mbasic.facebook.com' + sub)
                if self.temp_robot.find_all_by_css("img")[1]:
                    if 'scontent' in self.temp_robot.find_all_by_css("img")[1].get_attr('src'):
                        url = self.temp_robot.find_all_by_css("img")[1].get_attr('src')
                    else:
                        url = img_url.get_attr('src')
                else:
                    url = img_url.get_attr('src')
            except Exception:
                url = img_url.get_attr('src')
            return url
        else:
            return ""

    def __cover_photo(self):
        """
        :return:link of __cover_photo url for profile
        """
        img_url = self.robot.find_by_xpath('/html/body/div/div/div[2]/div/div[1]/div[1]/div[1]/div/div/a/img')
        img_href = self.robot.find_by_xpath('/html/body/div/div/div[2]/div/div[1]/div[1]/div[1]/div/div/a')
        if img_url:
            try:
                sub = (img_href.get_attr('href'))
                self.temp_robot.go_to('https://mbasic.facebook.com' + sub)
                if self.temp_robot.find_all_by_css("img")[1]:
                    if 'scontent' in self.temp_robot.find_all_by_css("img")[1].get_attr('src'):
                        url = self.temp_robot.find_all_by_css("img")[1].get_attr('src')
                    else:
                        url = img_url.get_attr('src')
                else:
                    url = img_url.get_attr('src')
            except Exception:
                url = img_url.get_attr('src')
            return url
        else:
            return ""

    # this function extract information in the below of profile name
    def __get_info(self):
        """
        :return:list of information below of profile name
        """
        info_lis = []
        try:
            info = self.robot.find_all_by_css("div[role='heading']")
            if info:
                for inf in info:
                    info_lis.append(inf.get_text())
                return info_lis
            else:
                return ''
        except Exception:
            return ''

    # this function extract information related to lived places of one profile
    def __extract_lived_places(self):
        """
        :return:list of information related to lived places
        """
        places = []
        if self.robot.find_by_css('div[title="Current City"]'):
            current_city = {'city_name': self.robot.find_by_css('div[title="Current City"] div a').get_text(),
                            'link': self.robot.find_by_css('div[title="Current City"] div a').get_attr('href'),
                            'type': "Current City"}
            places.append(current_city)
        if self.robot.find_by_css('div[title="Hometown"]'):
            hometown = {'city_name': self.robot.find_by_css('div[title="Hometown"] div a').get_text(),
                        'link': self.robot.find_by_css('div[title="Hometown"] div a').get_attr('href'),
                        'type': "Hometown"}

            self.robot.find_by_css('div[title="Current City"] div a').get_text()
            places.append(hometown)
        return places

    # this function extract information related to relationship of id or alias
    def __extract_relationship(self):
        """
        :return:information related to relationship
        """
        r = self.robot.find_all_by_css('div[id="relationship"] div div div')
        if r:
            try:
                relation = r[2].get_text()
                return relation
            except Exception:
                return None
        else:
            return None

    # this function extract information related to family members of one id or alias
    def __extract_family(self, family_members):
        """
        :param family_members: list of nodes related to family members information
        :return: list of information related to members of family
        """
        members = []
        i = 0
        j = 1
        for mem in family_members:
            family_dic = {'name': mem.get_text(), 'link': mem.get_attr('href')}
            if self.robot.find_all_by_css('div[id="family"] div h3 ')[j]:
                family_dic['kinship'] = self.robot.find_all_by_css('div[id="family"] div h3 ')[j].get_text()
            if self.robot.find_all_by_css('div[id="family"] div a img ')[i]:
                family_dic['image'] = self.robot.find_all_by_css('div[id="family"] div a img ')[i].get_attr('src')
            members.append(family_dic)
            i += 1
            j += 2
        return members

    # this function extract information in the part of About in profile page
    def __extarct_about(self):
        """
        :return:information in the part of About
        """
        bio = self.robot.find_all_by_css('div[id="bio"] div div')
        if bio:
            try:
                return bio[4].get_text()
            except Exception:
                return None
        else:
            return None

    # extract inforamtion related to favorite quotes
    def __extract_quote(self):
        """
        :return quote:
        """
        a = self.robot.find_all_by_css('div[id="quote"] div div')
        if a:
            try:
                quotes = a[3].get_text()
                return quotes
            except Exception:
                return None
        else:
            return None

    # this module extract information related to education
    def __extract_education(self, education):
        """
        :param education: node list of education
        :return: list of information about part of education
        """
        edu = []
        a = self.robot.find_all_by_css('div[id="education"] a img ')
        i = 0
        for ed in education:
            try:
                edu_dic = {'title': ed.get_text(), 'link': ed.get_attr('href')}
                text_list = a[i].get_parent().get_parent().get_text().split('\n')
                del text_list[0]
                del text_list[-1]
                if len(text_list) == 3:
                    edu_dic['type'] = text_list[1]
                    edu_dic['date'] = text_list[2]
                elif len(text_list) == 2:
                    edu_dic['type'] = text_list[1]
            except Exception:
                continue
            edu.append(edu_dic)
            i += 1
        return edu

    # this module extract information related to basic_info part
    def __extract_basic_info(self):
        """
        :return:list of information about part of basic_info
        """
        info = []
        if self.robot.find_by_css('div[title="Birthday"]'):
            birth = {'type': "Birthday",
                     'value': self.robot.find_all_by_css('div[title="Birthday"] td div')[1].get_text()}
            info.append(birth)
        if self.robot.find_by_css('div[title="Gender"]'):
            sex = {'type': "Gender",
                   'value': self.robot.find_all_by_css('div[title="Gender"] td div')[1].get_text()}
            info.append(sex)
        if self.robot.find_by_css('div[title="Languages"]'):
            language = {'type': "Languages",
                        'value': self.robot.find_all_by_css('div[title="Languages"] td div')[1].get_text()}
            info.append(language)
        if self.robot.find_by_css('div[title="Interested In"]'):
            language = {'type': "Interested In",
                        'value': self.robot.find_all_by_css('div[title="Interested In"] td div')[1].get_text()}
            info.append(language)
        return info

    # this module get all fiends of person and use from extract_friends() function
    def get_friends(self, facebook_id, friends_number=None):
        """
        :param facebook_id: facebook id or alias name for one page or person
        :param friends_number: number of result
        :return: list of friends's inforamtion related to profile
        """
        self.update_progressbar('request submitted successfully, get friends',
                                20)
        if friends_number:
            self.default_number = friends_number
        f_result = []
        result_list = []
        return_result = {}
        if self.__login():
            try:
                if facebook_id.isdigit():
                    self.robot.go_to("/profile.php?v=friends&startindex=0&id=%d" % int(facebook_id))
                else:
                    self.robot.go_to("/%s/friends" % facebook_id)
            except Exception:
                raise BadRequest('bad request')
            self.check_profile_availability()
            self.update_progressbar('open friends page',
                                    40)
            self.check_action()

            friends = self.robot.find_all_by_css("table[role='presentation']")
            if friends:
                try:
                    del friends[0]
                    del friends[-1]
                    del friends[-1]
                    f_result.extend(self.__extract_friends(friends))
                except Exception:  # if can not extract info
                    raise ResultNotFoundError('seems the profile doesnt exist')
            self.update_progressbar('extracting friends',
                                    50)
            # extracting more nodes
            while self.robot.find_by_css("#m_more_friends"):
                self.check_action()
                if self.check_number < self.default_number:
                    more = self.robot.find_by_css("#m_more_friends a")
                    if more:
                        more.click()
                    friends = self.robot.find_all_by_css("table[role='presentation']")
                    f_result.extend(self.__extract_friends(friends))
                else:
                    break

            # extracting info from nodes
            self.update_progressbar('saving friends info and downloading photo',
                                    70)
            for friend in f_result:
                self.check_action()
                temp_result = {'data': '', 'type': 5, 'properties': [],
                               'special_properties': [{'sub_type': 1, 'type': 0}]}
                alias = ''
                if 'link' in friend:
                    try:
                        alias = re.search('/(.+?)\?', friend['link']).group(1)
                    except AttributeError:
                        alias = friend['link'].replace('/', '')
                    if alias == 'profile.php':
                        try:
                            alias = re.search('id=(.+?)&', friend['link']).group(1)
                        except AttributeError:
                            alias = friend['link'].replace('/profile.php?id=', '')
                    temp_result['data'] = alias

                if 'profile_image' in friend:
                    image_profile = self.__save_image(friend['profile_image'], alias)
                    temp_result['properties'].append({'image_profile': image_profile[0], 'type': 13,
                                                      'more': {'ref': 'mbasic.facebook.com/' + alias,
                                                               'url': friend['profile_image'],
                                                               'file_name': image_profile[2]}})
                    temp_result['properties'].append({'image_profile_thumbnail': image_profile[1], 'type': 13,
                                                      'more': {'ref': 'mbasic.facebook.com/' + alias,
                                                               'url': friend['profile_image'],
                                                               'file_name': image_profile[2]}})
                else:
                    temp_result['properties'].append({'image_profile': '', 'type': 13,
                                                      'more': {'ref': 'mbasic.facebook.com/' + alias, 'url': ''}})

                if 'name' in friend:
                    temp_result['properties'].append({'name': friend['name'], 'type': 11})
                else:
                    temp_result['properties'].append({'name': '', 'type': 11})

                if 'desc' in friend:
                    temp_result['properties'].append({'desc': friend['desc'], 'type': 11})
                else:
                    temp_result['properties'].append({'desc': '', 'type': 11})
                result_list.append(temp_result)

            self.check_action()
            self.update_progressbar('done', 100)
            if len(result_list) == 0:
                raise ResultNotFoundError('can not find any friends for your profile')

            else:
                return_result['results'] = result_list
                return_result['has_media'] = True
        else:
            raise LoginError('can not login')
        return return_result

    # this module extract friends information
    def __extract_friends(self, friends):
        """
        :param friends: list of friend's node
        :return: list of friend's information
        """
        friends_lis = []
        for friend in friends:
            self.check_number += 1
            if self.check_number <= self.default_number:
                friends_dic = {}
                if friend.find_by_css('td a'):
                    if friend.find_by_css('td a').get_text() == "Create Page" or \
                            friend.find_by_css('td a').get_text() == "friends/hovercard/mbasic/" or \
                            friend.find_by_css('td a').get_text() == "pages/create/" or \
                            friend.find_by_css('td a').get_text() == "Create Page":
                        self.check_number -= 1
                        continue
                    else:
                        friends_dic['name'] = friend.find_by_css('td a').get_text()
                if friend.find_by_css('td a'):
                    friends_dic['link'] = friend.find_by_css('td a').get_attr('href')
                if friend.find_by_css('div img'):
                    if friend.find_by_css('div img').get_attr(
                            'src').startswith('https://static.xx'):
                        self.check_number -= 1
                        continue
                    else:
                        friends_dic['profile_image'] = friend.find_by_css('div img').get_attr('src')
                if friend.find_by_css('div span'):
                    if friend.find_by_css('div span').get_text() == "Add Friend":
                        friends_dic['desc'] = ''
                    else:
                        friends_dic['desc'] = friend.find_by_css('div span').get_text()
                friends_lis.append(friends_dic)
            else:
                break
        return friends_lis

    # this module get list of one profile's followers with  use of extract_followers() module
    def get_followers(self, facebook_id, followers_number=None):
        """
                :param facebook_id: facebook id or alias name for one page or person
                :param followers_number: number of result
                :return: list of follower's inforamtion related to profile
                """

        self.update_progressbar('request submitted successfully, get friends',
                                20)
        if followers_number:
            self.default_number = followers_number
        fo_result = []
        if self.__login():
            try:
                if facebook_id.isdigit():
                    self.robot.go_to("/profile.php?v=followers&startindex=0&id=%d" % int(facebook_id))
                else:
                    self.robot.go_to("/%s?v=followers" % facebook_id)
            except Exception:
                raise BadRequest('bad request')
            self.check_profile_availability()

            return_result = {}
            result_list = []
            followers = self.robot.find_all_by_css("div[id='root']>div:nth-child(2) div a span")
            self.check_action()
            if followers:
                try:
                    fo_result.extend(self.__extract_follow(followers))
                except Exception:
                    raise ResultNotFoundError(' can not extract info from follower')
            self.update_progressbar('extracting follower', 40)
            # for first see more click, it may exist two see more, so specify see more button and table to extract
            if self.robot.find_by_css("div[id='root']>div:nth-child(2)  #m_more_item"):
                if self.check_number < self.default_number:
                    more = self.robot.find_by_css("div[id='root']>div:nth-child(2) #m_more_item a")
                    if more:
                        more.click()
                    followers = self.robot.find_all_by_css("div[id='root'] div a span ")
                    fo_result.extend(self.__extract_follow(followers))
                # after one click on see more, reddirect to all follower page, so there is just one see more and table
                while self.robot.find_by_css("div[id='root'] #m_more_item"):
                    self.check_action()
                    if self.check_number < self.default_number:
                        more = self.robot.find_by_css("div[id='root'] #m_more_item a")
                        if more:
                            more.click()
                        followers = self.robot.find_all_by_css("div[id='root'] div a span ")
                        fo_result.extend(self.__extract_follow(followers))
                    else:
                        break
            # create json file from extract_follower_return list
            self.update_progressbar('saving follower info', 70)
            for follower in fo_result:
                self.check_action()
                temp_result = {'data': '', 'type': 5, 'properties': [],
                               'special_properties': [{'sub_type': 1, 'type': 0}]}
                alias = ''
                if 'link' in follower:
                    try:
                        alias = re.search('/(.+?)\?', follower['link']).group(1)
                    except AttributeError:
                        alias = follower['link'].replace('/', '')
                    if alias == 'profile.php':
                        try:
                            alias = re.search('id=(.+?)&', follower['link']).group(1)
                        except AttributeError:
                            alias = follower['link'].replace('/profile.php?id=', '')
                    temp_result['data'] = alias

                if 'profile_image' in follower:
                    image_profile = self.__save_image(follower['profile_image'], alias)
                    temp_result['properties'].append({'image_profile': image_profile[0], 'type': 13,
                                                      'more': {'ref': 'mbasic.facebook.com/' + alias,
                                                               'url': follower['profile_image'],
                                                               'file_name': image_profile[2]}})
                    temp_result['properties'].append({'image_profile_thumbnail': image_profile[1], 'type': 13,
                                                      'more': {'ref': 'mbasic.facebook.com/' + alias,
                                                               'url': follower['profile_image'],
                                                               'file_name': image_profile[2]}})
                else:
                    temp_result['properties'].append({'image_profile': '', 'type': 13,
                                                      'more': {'ref': 'mbasic.facebook.com/' + alias, 'url': ''}})

                if 'name' in follower:
                    temp_result['properties'].append({'name': follower['name'], 'type': 11})
                else:
                    temp_result['properties'].append({'name': '', 'type': 11})

                if 'desc' in follower:
                    temp_result['properties'].append({'desc': follower['desc'], 'type': 11})
                else:
                    temp_result['properties'].append({'desc': '', 'type': 11})
                result_list.append(temp_result)

            self.update_progressbar('done',
                                    100)
            self.check_action()
        else:
            raise LoginError('can not login')
        if len(result_list) == 0:
            raise ResultNotFoundError('can not find any follower for your profile')
        else:
            return_result['results'] = result_list
            return_result['has_media'] = True
        return return_result

    # this module get list of one profile's followings with  use of extract_following() module
    def get_following(self, facebook_id, following_number=None):
        """

        :param facebook_id: facebook id or alias name for one page or person
        :param following_number: number of result
        :return: list of following's inforamtion related to profile
        """
        self.update_progressbar('request submitted successfully, get friends',
                                20)
        if following_number:
            self.default_number = following_number
        fo_result = []
        if self.__login():
            try:
                if facebook_id.isdigit():
                    self.robot.go_to("/profile.php?v=followers&startindex=0&id=%d" % int(facebook_id))
                else:
                    self.robot.go_to("/%s?v=followers" % facebook_id)
            except Exception:
                raise BadRequest('bad request')

            self.check_profile_availability()
            self.check_action()
            return_result = {}
            result_list = []
            followings = self.robot.find_all_by_css("div[id='root']>div:nth-child(3) div a span")
            if followings:
                try:
                    fo_result.extend(self.__extract_following(followings))  # use following method
                except Exception as e:
                    raise ResultNotFoundError(e)
            self.update_progressbar('extracting following info',
                                    50)
            # in case of first page of following, info of following should extract from third table
            # for first time to click on see more, it may exist two see more, so specify that
            if self.robot.find_all_by_css("div[id='root']>div:nth-child(3) #m_more_item a"):
                if self.check_number < self.default_number:
                    more = self.robot.find_by_css("div[id='root']>div:nth-child(3)  #m_more_item a")
                    if more:
                        more.click()
                    # in case of see more page of following, info of following should extract from first table
                    followings = self.robot.find_all_by_css("div[id='root'] div a span ")
                    # use follow method to extract from nodes (because it's same as follower pages)
                    fo_result.extend(self.__extract_follow(followings))

                # after click on first see more, robot move to page that its all following so click on see more
                while self.robot.find_by_css("div[id='root'] #m_more_item a"):
                    self.check_action()
                    if self.check_number < self.default_number:
                        more = self.robot.find_by_css("div[id='root']  #m_more_item a")
                        if more:
                            more.click()
                        # in case of see more page of following, info of following should extract from first table
                        followings = self.robot.find_all_by_css("div[id='root'] div a span ")
                        # use follow method to extract from nodes (because it's same as follower pages)
                        fo_result.extend(self.__extract_follow(followings))
                    else:
                        break

            self.update_progressbar('downloading photo and saving other info',
                                    50)  # create json file from extract_following_return list
            for following in fo_result:
                self.check_action()
                temp_result = {'data': '', 'type': 5, 'properties': [],
                               'special_properties': [{'sub_type': 1, 'type': 0}]}
                alias = ''
                if 'link' in following:
                    try:
                        alias = re.search('/(.+?)\?', following['link']).group(1)
                    except AttributeError:
                        alias = following['link'].replace('/', '')
                    if alias == 'profile.php':
                        try:
                            alias = re.search('id=(.+?)&', following['link']).group(1)
                        except AttributeError:
                            alias = following['link'].replace('/profile.php?id=', '')
                    temp_result['data'] = alias

                if 'profile_image' in following:
                    image_profile = self.__save_image(following['profile_image'], alias)
                    temp_result['properties'].append({'image_profile': image_profile[0], 'type': 13,
                                                      'more': {'ref': 'mbasic.facebook.com/' + alias,
                                                               'url': following['profile_image'],
                                                               'file_name': image_profile[2]}})
                    temp_result['properties'].append({'image_profile_thumbnail': image_profile[1], 'type': 13,
                                                      'more': {'ref': 'mbasic.facebook.com/' + alias,
                                                               'url': following['profile_image'],
                                                               'file_name': image_profile[2]}})

                else:
                    temp_result['properties'].append({'image_profile': '', 'type': 13,
                                                      'more': {'ref': 'mbasic.facebook.com/' + alias, 'url': ''}})

                if 'name' in following:
                    temp_result['properties'].append({'name': following['name'], 'type': 11})
                else:
                    temp_result['properties'].append({'name': '', 'type': 11})

                if 'desc' in following:
                    temp_result['properties'].append({'desc': following['desc'], 'type': 11})
                else:
                    temp_result['properties'].append({'desc': '', 'type': 11})
                result_list.append(temp_result)

            self.update_progressbar('done',
                                    100)
            self.check_action()
        else:
            raise LoginError('can not login')
        if len(result_list) == 0:
            raise ResultNotFoundError('can not find any following for your profile')
        else:
            return_result['results'] = result_list
            return_result['has_media'] = True
        return return_result

    # this module extract profile's followers/ following information
    def __extract_follow(self, follows):
        """
        :param followers/following : node list of followers/
        following (use for following when click on see more, because after that the page is same as follower)
        :return: list of information related to followers/following
        """
        follow_lis = []
        i = 1
        # in case of that profile has use facebook mobile, i = 2 skip mobile image
        if self.robot.find_all_by_css("div[id='root'] div img"):
            if self.robot.find_all_by_css("div[id='root'] div img")[1].get_attr('src').endswith('.png'):
                i = 2

        for follow in follows:
            self.check_number += 1
            if self.check_number <= self.default_number:
                follow_dic = {'name': follow.get_parent().get_text(), 'link': follow.get_parent().get_attr('href')}
                if follow_dic['name'] == 'See More':
                    self.check_number -= 1
                    continue
                if self.robot.find_all_by_css("div[id='root'] div img"):
                    follow_dic['profile_image'] = self.robot.find_all_by_css("div[id='root'] div img")[i].get_attr(
                        'src')
                    i += 1
                follow_lis.append(follow_dic)
            else:
                break
        return follow_lis

    def __extract_following(self, follows):
        """
        :param follows: node list of following
        :return: list of information related to following, at first page(befroe clicking see more)
        """
        follow_lis = []
        i = 0
        for follow in follows:
            self.check_number += 1
            if self.check_number <= self.default_number:
                follow_dic = {'name': follow.get_parent().get_text(), 'link': follow.get_parent().get_attr('href')}
                try:  # face see more in following
                    if self.robot.find_all_by_css("div[id='root']>div:nth-child(3) div img"):
                        follow_dic['profile_image'] = \
                            self.robot.find_all_by_css("div[id='root']>div:nth-child(3) div img")[
                                i].get_attr(
                                'src')
                        i += 1
                    follow_lis.append(follow_dic)
                except IndexError:
                    self.check_number -= 1
                    pass
            else:
                break
        return follow_lis

    # this part handle searching one term in all information with using extract_search_all() module
    def search_all(self, search_term, searchs_number=None):
        """
        :param search_term:searching term which user want to search
        :param searchs_number: number of result
        :return: list of information related to search
        """
        self.update_progressbar('request submitted successfully, search all',
                                20)
        self.check_action()
        if searchs_number:
            self.default_number = searchs_number

        search_result = []
        result_list = []
        return_result = {}
        if self.__login():
            try:
                self.robot.go_to("/graphsearch/str/%s/keywords_users" % search_term)
            except Exception:
                raise BadRequest('bad request')
            self.update_progressbar('go to  search page',
                                    40)
            search_res = self.robot.find_all_by_css("table[role='presentation']")
            if search_res:
                try:
                    search_result.extend(self.__extract_search_all(search_res))
                except Exception:
                    pass
            self.update_progressbar('extracting search info',
                                    50)
            while self.robot.find_by_css("#see_more_pager"):
                self.check_action()
                if self.check_number < self.default_number:
                    more = self.robot.find_by_css("#see_more_pager a")
                    if more:
                        more.click()
                    results = self.robot.find_all_by_css("table[role='presentation']")

                    search_result.extend(self.__extract_search_all(results))
                else:
                    break
            self.update_progressbar('saving result and their pictures',
                                    70)
            for search in search_result:
                self.check_action()
                temp_result = {'data': '', 'type': 5, 'properties': [],
                               'special_properties': [{'sub_type': 1, 'type': 0}]}
                alias = ''
                if 'link' in search:
                    try:
                        alias = re.search('/(.+?)\?', search['link']).group(1)
                    except AttributeError:
                        alias = search['link'].replace('/', '')
                    if alias == 'profile.php':
                        try:
                            alias = re.search('id=(.+?)&', search['link']).group(1)
                        except AttributeError:
                            alias = search['link'].replace('/profile.php?id=', '')
                    temp_result['data'] = alias

                if 'profile_image' in search:
                    image_profile = self.__save_image(search['profile_image'], alias)
                    temp_result['properties'].append({'image_profile': image_profile[0], 'type': 13,
                                                      'more': {'ref': 'mbasic.facebook.com/' + alias,
                                                               'url': search['profile_image'],
                                                               'file_name': image_profile[2]}})
                    temp_result['properties'].append({'image_profile_thumbnail': image_profile[1], 'type': 13,
                                                      'more': {'ref': 'mbasic.facebook.com/' + alias,
                                                               'url': search['profile_image'],
                                                               'file_name': image_profile[2]}})
                else:
                    temp_result['properties'].append({'image_profile': '', 'type': 13,
                                                      'more': {'ref': 'mbasic.facebook.com/' + alias,
                                                               'url': ''}})

                if 'name' in search:
                    temp_result['properties'].append({'name': search['name'], 'type': 11})
                else:
                    temp_result['properties'].append({'name': '', 'type': 11})

                if 'desc' in search:
                    temp_result['properties'].append({'desc': search['desc'], 'type': 11})
                else:
                    temp_result['properties'].append({'desc': '', 'type': 11})
                result_list.append(temp_result)

            self.update_progressbar('done', 100)
            self.check_action()
        else:
            raise LoginError('Can not login')
        if len(result_list) == 0:
            raise ResultNotFoundError('can not find any search result for your profile')

        else:
            return_result['results'] = result_list
            return_result['has_media'] = True
        return return_result

    def __extract_search_all(self, search_res):
        """
        :param :
        :param search_res:node list related to result of search
        :return: list of extracted information related to term search
        """
        search_lis = []
        del search_res[0]
        del search_res[-1]
        del search_res[-1]
        new_search_res = search_res
        for q in new_search_res:
            self.check_number += 1
            if self.check_number <= self.default_number:
                if q.find_by_css('td a img'):
                    search_dic = {'name': (q.find_by_css('td a img')).get_attr("alt"),
                                  'link': (q.find_by_css('td a img')).get_parent().get_attr("href"),
                                  'profile_image': (q.find_by_css('td a img')).get_attr("src"), 'desc': q.get_text()}
                    search_lis.append(search_dic)
            else:
                break
        return search_lis

    def __save_image(self, url, username):
        """
         :param url:  download content of this url
         :param username:  use for naming files
         :return: the path that can download photos
         """
        if username is None:
            return ''
        base_path = self.storage[0]
        relative_path = self.storage[1]
        img_full_path = base_path + '/' + relative_path + '/'
        thumbnail_full_path = base_path + '/' + relative_path + '/' + 'thumbnail' + '/'
        thumbnail_save_path = ''
        file = str(hashlib.md5(username.encode('utf-8')).hexdigest()) + str(
            hashlib.md5(str(int(round(time.time() * 1000))).encode('utf-8')).hexdigest())
        os.makedirs(img_full_path, exist_ok=True)
        os.makedirs(thumbnail_full_path, exist_ok=True)
        try:  # using Qhttps get request to download
            img_data = Qhttp.get(url, timeout=10).content
            img_save_path = img_full_path + file + '.jpg'
            image = open(img_save_path, 'wb')
            image.write(img_data)
            image.close()
        except Exception:
            return ['', '', '']
        try:
            size = 72, 72
            thumbnail_save_path = thumbnail_full_path + file + '.jpg'
            image = Image.open(img_save_path)
            image.thumbnail(size, Image.ANTIALIAS)
            image.save(thumbnail_save_path, quality=40, optimize=True)
        except Exception:
            pass
        return [img_save_path, thumbnail_save_path, file]

    def check_profile_availability(self):
        """
        check if profile exist
         """
        if self.robot.find_by_css('div span') is None:
            raise ResultNotFoundError('can not extract info from this page')
        else:
            if self.robot.find_by_css('div span').get_text() == "The page you requested was not found." \
                    or self.robot.get_url() == 'https://mbasic.facebook.com/home.php?_rdr' or \
                    self.robot.find_by_css(
                        'div span').get_text() == 'The page you requested cannot be displayed right now.' \
                                                  ' It may be temporarily unavailable,' \
                                                  ' the link you clicked on may be broken or expired,' \
                                                  ' or you may not have permission to view this page.':
                raise ResultNotFoundError('seems the profile doesnt exist')
