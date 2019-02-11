import hashlib
import pickle

from vendor.custom_exception import NetworkError, LoginError, InvalidUserId, CaptchaNeededError, ResultNotFoundError, \
    InvalidInputError
from selenium import webdriver
import time
import os
from core.constants import BASE_APP_PATH
import vendor.selenium_utils as utils
from selenium.webdriver.common.keys import Keys
from modules.linkedin.v_1_0.utils import save_image


class Linkedin:
    path = BASE_APP_PATH + '/vendor/chromedriver'

    def __init__(self, username, password, parent=None):

        try:
            self.username = username
            self.password = password
            options = webdriver.ChromeOptions()
            options.add_argument('headless')
            options.add_argument('--no-sandbox')
            self.driver = webdriver.Chrome(self.path, chrome_options=options)
            self.driver.implicitly_wait(10)
            # use storage for saving images
            proccess_id = parent.task_model.process_id
            self.storage = [
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
                '/modules/storage/' + proccess_id]
            # self.driver.get("https://www.linkedin.com")
            utils.go_to(self.driver, "https://www.linkedin.com")
            self.parent = parent
            if self.parent:
                self.process_id = parent.task_model.process_id
            self.check_number = 0
            self.default_number = 10
            cookie_path = BASE_APP_PATH + "/modules/linkedin/v_1_0/cookies/"
            cookie_path_hash = str(hashlib.md5(self.username.encode('utf-8')).hexdigest()) + str(
                hashlib.md5(self.password.encode('utf-8')).hexdigest())
            os.makedirs(cookie_path + cookie_path_hash, exist_ok=True)
            self.cookie = cookie_path + cookie_path_hash + '/cookies.pkl'
            if os.path.exists(self.cookie):
                with open(self.cookie, 'rb') as cookie_file:
                    cookies = pickle.load(cookie_file)
                for cookie in cookies:
                    self.driver.add_cookie(cookie)
                # self.driver.refresh()
                utils.refresh_page(self.driver)
            self.update_progressbar('Go to linkedin page', 5)
            self.check_action()
        except Exception as e:  # can not go to linkedin.com
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
        :return:boolean for status of login to linkedin
        """
        if self.__check_login():

            self.update_progressbar('login successfully', 20)
            self.check_action()
            return True

        else:  # not login yet, try to login
            self.check_action()

            email = self.driver.find_element_by_xpath("""//*[@id="login-email"]""")
            password = self.driver.find_element_by_xpath("""//*[@id="login-password"]""")
            log_in = self.driver.find_element_by_xpath("""//*[@id="login-submit"]""")
            if email and password and log_in:
                email.send_keys(self.username)
                password.send_keys(self.password)
                if log_in:
                    log_in.click()
                    if utils._by_xpath(self.driver, "//*[text()='Let's do a quick security check']"):
                        raise CaptchaNeededError('Captcha is needed')
                    if utils._by_xpath(self.driver, "//*[text()='Forgot password?']"):
                        raise LoginError('can not login with this username and password')
                    self.__get_cookie(self.cookie)
                    self.update_progressbar('login successfully', 20)
                    return True

        self.update_progressbar('login failed', 20)
        return False

    def __get_cookie(self, path):
        if path:
            with open(path, 'wb') as cookie_file:  # with auto close file.
                pickle.dump(self.driver.get_cookies(), cookie_file)
            # pickle.dump(self.driver.get_cookies(), open(path, "wb"))

    # check if this client logged in linkedin
    def __check_login(self):
        if self.driver.find_elements_by_xpath("//*[contains(text(), 'My Network')]"):
            return True

    def profile(self, linkedin_id):
        # choose that linkedin_id belongs to what kind of profile
        """
        :param facebook_id: facebook id or alias name for one page or person
        :return: all profile information related to id or alias name
        """
        result = {'properties': [], 'special_properties': [], 'results': []}
        self.update_progressbar('profile request submit', 10)
        self.check_action()
        if self.__login():
            page_url = 'https://www.linkedin.com/in/' + linkedin_id + '/'
            self.driver.get(page_url + 'detail/contact-info/')

            if utils._by_xpath(self.driver, "//*[text()='This profile is not available']"):
                self.update_progressbar('the profile is not available', 20)
                raise InvalidUserId('invalid linkedin id')
            result['results'].append({'linkedin_id': linkedin_id, 'type': 5})
            contact_info = {}
            temp = utils._by_css_selector(self.driver, '.pv-profile-section__section-info.section-info')
            if temp:
                sections = utils._by_xpath_s(temp, './section')
                for sec in sections:
                    if sec.get_attribute('class') == 'pv-contact-info__contact-type ci-vanity-url':
                        contact_info['profile_url'] = utils._by_xpath(sec, './div/a').get_attribute('href')
                    else:
                        if utils.check_exists_by_xpath(sec, './ul/li/div/a'):
                            contact_info[str(utils._by_xpath(sec, './header').text)] = str(
                                utils._by_xpath(sec, './ul/li/div/a').get_attribute('href'))

                        elif utils.check_exists_by_xpath(sec, './ul/li/a'):
                            contact_info[str(utils._by_xpath(sec, './header').text)] = str(
                                utils._by_xpath(sec, './ul/li/a').get_attribute('href'))

            self.driver.get(page_url)

            self.update_progressbar('start to read the page', 25)
            self.check_action()

            self.driver.execute_script('window.scrollTo({top: document.body.scrollHeight,behavior: "smooth"})')
            time.sleep(1)
            self.driver.execute_script('window.scrollTo({top: 0,behavior: "smooth"})')
            time.sleep(1)

            temp = utils._by_css_selector(self.driver,
                                          '.pv-profile-section.pv-top-card-section.artdeco-container-card.ember-view')
            if utils.check_exists_by_xpath(temp, '*/button'):
                utils.check_click(utils._by_xpath(temp, '*/button'))

            for each in self.driver.find_elements_by_xpath("//*[text()='Show more']"):
                try:
                    if each.is_displayed():
                        utils.check_click(each)
                    else:
                        each.location_once_scrolled_into_view
                        utils.check_click(each)
                except:
                    pass

            for each in self.driver.find_elements_by_xpath("//*[text()='See more']"):
                utils.check_click(each)

            for each in self.driver.find_elements_by_xpath("//*[contains(text(), 'more role')]"):
                try:
                    self.driver.execute_script("arguments[0].click();", each)
                except:
                    pass

            self.update_progressbar('start reading profile section information', 30)
            self.check_action()
            # profile info
            p_infos = utils._by_css_selector(self.driver,
                                             '.pv-profile-section.pv-top-card-section.artdeco-container-card.ember-view')
            if p_infos:
                for i, each in enumerate(p_infos.find_elements_by_xpath(
                        './div[*]')):
                    temp1 = utils._by_css_selector(each,
                                                   '.pv-top-card-section__photo-wrapper.pv-top-card-v2-section__photo-wrapper')
                    if temp1:
                        name = utils._by_xpath(temp1, './div/div[1]')
                        if name:
                            if name.get_attribute('style'):
                                picture_url = name.get_attribute('style').split('"')[1]
                                [img_save_path, thumbnail_save_path, file] = save_image(url=picture_url,
                                                                                        username=self.username,
                                                                                        process_id=self.process_id)
                                result['properties'].append(
                                    {'image_profile': img_save_path, 'type': 13,
                                     'more': {'ref': page_url, 'file_name': file, 'url': picture_url}})
                                result['properties'].append(
                                    {'thumbnail_image_profile': thumbnail_save_path, 'type': 13,
                                     'more': {'ref': page_url, 'file_name': file, 'url': picture_url}})

                    temp2 = utils._by_css_selector(each, '.pv-top-card-v2-section__info.mr5')
                    if temp2:
                        name = utils._by_xpath(temp2, './div/h1')
                        if name:
                            result['properties'].append({'name': name.text, 'type': 11, 'ref': page_url})
                        profile_title = utils._by_xpath(temp2, './h2')
                        if profile_title:
                            result['special_properties'].append(
                                {'profile title': profile_title.text, 'type': 11, 'ref': page_url})

                        Location = utils._by_xpath(temp2, './h3')
                        if Location:
                            result['properties'].append({'location': Location.text, 'type': 8, 'ref': page_url})
                    temp3 = utils._by_css_selector(each, '.pv-top-card-v2-section__links')
                    if temp3:
                        con_numbers = utils._by_xpath(temp3, './div/span[2]')
                        if con_numbers:
                            con_numbers = con_numbers.text.split()
                            result['special_properties'].append(
                                {'connection numbers': con_numbers[0], 'type': 0, 'ref': page_url})
                    if each.get_attribute(
                            'class') == 'pv-top-card-section__summary pv-top-card-section__summary--with-content mt4 ember-view':
                        profile_summary = utils._by_xpath(each, './p')
                        if profile_summary:
                            result['special_properties'].append(
                                {'profile summary': profile_summary.text, 'type': 0, 'ref': page_url})

            # contact = {'title': 'contact info', 'more':[]}
            for k, v in contact_info.items():
                if k.lower() in ['twitter', 'facebook', 'instagram']:
                    type = 5
                elif k.lower() == 'profile_url':
                    continue
                else:
                    type = 1
                result['special_properties'].append({k: v, 'type': type, 'ref': page_url})

            self.update_progressbar('start read experience section information', 40)
            self.check_action()

            # read education and experience section
            for each in utils._by_css_selector(self.driver,
                                               '.pv-profile-section.pv-profile-section--reorder-enabled.background-section.artdeco-container-card.ember-view').find_elements_by_css_selector(
                '.pv-profile-section-pager.ember-view'):
                each = each.find_element_by_tag_name('section')
                if each.get_attribute('id') == 'experience-section':
                    experiences = []
                    if utils.check_exists_by_css_selector(each,
                                                          '.pv-profile-section__section-info.section-info.pv-profile-section__section-info--has-more'):
                        ul = each.find_element_by_css_selector(
                            '.pv-profile-section__section-info.section-info.pv-profile-section__section-info--has-more')

                    elif utils.check_exists_by_css_selector(each,
                                                            '.pv-profile-section__section-info.section-info.pv-profile-section__section-info--has-no-more'):
                        ul = (each.find_element_by_css_selector(
                            '.pv-profile-section__section-info.section-info.pv-profile-section__section-info--has-no-more'))
                    if ul:
                        lis = ul.find_elements_by_css_selector('.pv-entity__position-group-pager.ember-view')
                    for i, li in enumerate(lis):
                        experience = {'title': '', 'Company Name': '', 'more': {}, 'history': []}
                        if utils.check_exists_by_css_selector(li,
                                                              '.pv-entity__position-group.mt2.ember-view') or utils.check_exists_by_css_selector(
                            li, '.pv-entity__position-group.mt2'):
                            # multi position
                            company_summary = utils._by_css_selector(li, '.pv-entity__company-summary-info')
                            if company_summary:
                                # company = li.find_element_by_css_selector('.pv-entity__company-summary-info')
                                cname = utils._by_xpath(company_summary, './h3/span[1]')
                                if cname:
                                    if cname.text == 'Company Name':
                                        experience['Company Name'] = company_summary.find_element_by_xpath(
                                            './h3/span[2]').text
                                Total_duration = utils._by_xpath(company_summary, './h4/span[1]')
                                if Total_duration.text == 'Total Duration':
                                    experience['more']['total duration'] = company_summary.find_element_by_xpath(
                                        './h4/span[2]').text

                            if utils.check_exists_by_css_selector(li, '.pv-entity__position-group.mt2.ember-view'):
                                infos = utils._by_css_selector(li,
                                                               '.pv-entity__position-group.mt2.ember-view').find_elements_by_css_selector(
                                    '.pv-entity__position-group-role-item.sortable-item.ember-view')

                                for info in infos:
                                    position = {}
                                    info1 = utils._by_css_selector(info,
                                                                   '.pv-entity__summary-info-v2.pv-entity__summary-info--v2.pv-entity__summary-info-margin-top')
                                    if not info1:
                                        info1 = utils._by_css_selector(info,
                                                                       '.pv-entity__summary-info-v2.pv-entity__summary-info--background-section.pv-entity__summary-info-margin-top')
                                    if info1:
                                        info = info1
                                        title = utils._by_xpath(info, './h3/span[1]')
                                        if title:
                                            if title.text == 'Title':
                                                position['Title'] = info.find_element_by_xpath('./h3/span[2]').text
                                        date = utils._by_xpath(info, './div/h4[1]/span[1]')
                                        if date:
                                            if date.text == 'Dates Employed':
                                                position['Dates Employed'] = info.find_element_by_xpath(
                                                    './div/h4[1]/span[2]').text
                                        duration = utils._by_xpath(info, './div/h4[2]/span[1]')
                                        if duration:
                                            if duration.text == 'Employment Duration':
                                                position['Employment Duration'] = info.find_element_by_xpath(
                                                    './div/h4[2]/span[2]').text
                                        location = utils._by_xpath(info, './h4/span[1]')
                                        if location:
                                            if location.text == 'Location':
                                                position['Location'] = info.find_element_by_xpath('./h4/span[2]').text

                                    experience['history'].append(position)

                            elif utils.check_exists_by_css_selector(li, '.pv-entity__position-group.mt2'):
                                # positions = []
                                li = li.find_element_by_css_selector('.pv-entity__position-group.mt2')
                                infos = utils._by_css_selector_s(li,
                                                                 '.pv-entity__position-group-role-item-fading-timeline')
                                if infos:

                                    for info in infos:
                                        position = {}
                                        info = utils._by_css_selector(info,
                                                                      '.pv-entity__summary-info-v2.pv-entity__summary-info--background-section.pv-entity__summary-info-margin-top')

                                        title = utils._by_xpath(info, './h3/span[1]')
                                        if title:
                                            if title.text == 'Title':
                                                position['Title'] = info.find_element_by_xpath('./h3/span[2]').text
                                        dates = utils._by_xpath(info, './div/h4[1]/span[1]')
                                        if dates:
                                            if dates.text == 'Dates Employed':
                                                position['Dates Employed'] = info.find_element_by_xpath(
                                                    './div/h4[1]/span[2]').text
                                        if duration:
                                            duration = utils._by_xpath(info, './div/h4[2]/span[1]')
                                            if duration.text == 'Employment Duration':
                                                position['Employment Duration'] = info.find_element_by_xpath(
                                                    './div/h4[2]/span[2]').text
                                        location = utils._by_xpath(info, './h4/span[1]')
                                        if location:
                                            if location.text == 'Location':
                                                position['Location'] = info.find_element_by_xpath('./h4/span[2]').text
                                        experience['history'].append(position)

                                elif utils.check_exists_by_css_selector(li,
                                                                        '.pv-entity__position-group-role-item.sortable-item.ember-view') or utils.check_exists_by_css_selector(
                                    li, '.pv-entity__position-group-role-item'):
                                    # positions = []
                                    infos = utils._by_css_selector_s(li,
                                                                     '.pv-entity__position-group-role-item.sortable-item.ember-view')
                                    if not infos:
                                        infos = utils._by_css_selector_s(li,
                                                                         '.pv-entity__position-group-role-item')
                                    # TODO: add if infos
                                    if infos:
                                        for info in infos:
                                            position = {}
                                            info1 = utils._by_css_selector(info,
                                                                           '.pv-entity__summary-info-v2.pv-entity__summary-info--background-section.pv-entity__summary-info-margin-top')
                                            if not info1:
                                                info1 = utils._by_css_selector(info,
                                                                               '.pv-entity__summary-info-v2.pv-entity__summary-info--v2.pv-entity__summary-info-margin-top')
                                            if info1:
                                                info = info1

                                            title = utils._by_xpath(info, './h3/span[1]')
                                            if title:
                                                if title.text == 'Title':
                                                    position['Title'] = info.find_element_by_xpath('./h3/span[2]').text
                                            date = utils._by_xpath(info, './div/h4[1]/span[1]')
                                            if date:
                                                if date.text == 'Dates Employed':
                                                    position['Dates Employed'] = info.find_element_by_xpath(
                                                        './div/h4[1]/span[2]').text
                                            duration = utils._by_xpath(info, './div/h4[2]/span[1]')
                                            if duration:
                                                if duration.text == 'Employment Duration':
                                                    position['Employment Duration'] = info.find_element_by_xpath(
                                                        './div/h4[2]/span[2]').text
                                            location = utils._by_xpath(info, './h4/span[1]')
                                            if location:
                                                if location.text == 'Location':
                                                    position['Location'] = info.find_element_by_xpath(
                                                        './h4/span[2]').text
                                            experience['history'].append(position)

                            experiences.append(experience)
                            # experience['type'] = 11
                            # experience['ref'] = page_url
                            # result['results'].append(experience)

                        elif utils.check_exists_by_css_selector(li,
                                                                '.pv-entity__summary-info.pv-entity__summary-info--background-section.mb2'):
                            info = utils._by_css_selector(li,
                                                          '.pv-entity__summary-info.pv-entity__summary-info--background-section.mb2')
                            title = utils._by_xpath(info, './h3')
                            if title:
                                experience['title'] = title.text
                            cname = utils._by_xpath(info, './h4/span[1]')
                            if cname:
                                if cname.text == 'Company Name':
                                    experience['Company Name'] = info.find_element_by_xpath('./h4/span[2]').text
                            date = utils._by_xpath(info, './div/h4[1]/span[1]')
                            if date:
                                if date.text == 'Dates Employed':
                                    experience['more']['Dates Employed'] = info.find_element_by_xpath(
                                        './div/h4[1]/span[2]').text
                            duration = utils._by_xpath(info, './div/h4[2]/span[1]')
                            if duration:
                                if duration.text == 'Employment Duration':
                                    experience['more']['total duration'] = info.find_element_by_xpath(
                                        './div/h4[2]/span[2]').text
                            experiences.append(experience)
                            # experience['type'] = 11
                            # experience['ref'] = page_url
                            # result['results'].append(experience)

                        elif utils.check_exists_by_css_selector(li,
                                                                '.pv-entity__summary-info.pv-entity__summary-info--background-section'):
                            info = utils._by_css_selector(li,
                                                          '.pv-entity__summary-info.pv-entity__summary-info--background-section')
                            title = utils._by_xpath(info, './h3')
                            if title:
                                experience['title'] = title.text
                            cname = utils._by_xpath(info, './h4/span[1]')
                            if cname:
                                if cname.text == 'Company Name':
                                    experience['Company Name'] = info.find_element_by_xpath('./h4/span[2]').text
                            date = utils._by_xpath(info, './div/h4[1]/span[1]')
                            if date:
                                if date.text == 'Dates Employed':
                                    experience['more']['Dates Employed'] = info.find_element_by_xpath(
                                        './div/h4[1]/span[2]').text
                            duration = utils._by_xpath(info, './div/h4[2]/span[1]')
                            if duration:
                                if duration.text == 'Employment Duration':
                                    experience['more']['total duration'] = info.find_element_by_xpath(
                                        './div/h4[2]/span[2]').text

                            experiences.append(experience)
                            # experience['type'] = 11
                            # experience['ref'] = page_url
                            # result['results'].append(experience)

                        elif utils.check_exists_by_css_selector(li,
                                                                '.pv-entity__summary-info.pv-entity__summary-info--v2'):
                            # one position
                            info = utils._by_css_selector(li, '.pv-entity__summary-info.pv-entity__summary-info--v2')
                            title = utils._by_xpath(info, './h3')
                            if title:
                                experience['title'] = title.text
                            cname = utils._by_xpath(info, './h4/span[1]')
                            if cname:
                                if cname.text == 'Company Name':
                                    experience['Company Name'] = info.find_element_by_xpath('./h4/span[2]').text

                            date = utils._by_xpath(info, './div/h4[1]/span[1]')
                            if date:
                                if date.text == 'Dates Employed':
                                    experience['more']['Dates Employed'] = info.find_element_by_xpath(
                                        './div/h4[1]/span[2]').text

                            duration = utils._by_xpath(info, './div/h4[2]/span[1]')
                            if duration:
                                if duration.text == 'Employment Duration':
                                    experience['more']['total duration'] = info.find_element_by_xpath(
                                        './div/h4[2]/span[2]').text

                            experiences.append(experience)
                            # experience['type'] = 11
                            # experience['ref'] = page_url
                            # result['results'].append(experience)

                    result['properties'].append({'experiences': experiences, 'type': 11, 'ref': page_url})
                elif each.get_attribute('id') == 'education-section':
                    self.check_action()
                    self.update_progressbar('start read education section information', 45)
                    educations = []
                    ul1 = utils._by_css_selector(each,
                                                 '.pv-profile-section__section-info.section-info.pv-profile-section__section-info--has-more')
                    if not ul1:
                        ul1 = utils._by_css_selector(each,
                                                     '.pv-profile-section__section-info.section-info.pv-profile-section__section-info--has-no-more')

                    if ul1:
                        ul = ul1
                        lis = utils._by_css_selector_s(ul,
                                                       '.pv-profile-section__sortable-card-item.pv-education-entity.pv-profile-section__card-item.ember-view')
                        if not lis:
                            lis = utils._by_css_selector_s(ul,
                                                           '.pv-education-entity.pv-profile-section__card-item.ember-view')

                    if lis:
                        for i, li in enumerate(lis):
                            education = {'university': '', 'more': {}}
                            info = utils._by_css_selector(li, '.pv-entity__summary-info')

                            university = utils._by_xpath(info, './div/h3')
                            if university:
                                education['university'] = university.text

                            dname = utils._by_xpath(info, './div/p[1]/span[1]')
                            if dname:
                                if dname.text == 'Degree Name':
                                    education['more']['Degree Name'] = utils._by_xpath(info, './div/p[1]/span[2]').text

                            field = utils._by_xpath(info, './div/p[2]/span[1]')
                            if field:
                                if field.text == 'Field Of Study':
                                    education['more']['Field Of Study'] = utils._by_xpath(info,
                                                                                          './div/p[2]/span[2]').text

                            grade = utils._by_xpath(info, './div/p[3]/span[1]')
                            if grade:
                                if grade.text == 'Grade':
                                    education['more']['Grade'] = utils._by_xpath(info, './div/p[3]/span[2]').text

                            dates = utils._by_xpath(info, './p/span[1]')
                            if dates:
                                if dates.text == 'Dates attended or expected graduation':
                                    education['more']['Dates attended or expected graduation'] = utils._by_xpath(info,
                                                                                                                 './p/span[2]').text

                            educations.append(education)
                            # education['type'] = 11
                            # education['ref'] = page_url
                            # result['results'].append(education)
                        result['properties'].append({'educations': educations, 'type': 11, 'ref': page_url})

            self.driver.execute_script('window.scrollTo({top: document.body.scrollHeight,behavior: "smooth"})')
            self.driver.execute_script('window.scrollTo({top: 0,behavior: "smooth"})')

            # read interests section
            self.update_progressbar('start reading interests section information', 50)
            self.check_action()
            interests = utils._by_css_selector(self.driver,
                                               '.pv-profile-section.pv-interests-section.artdeco-container-card.ember-view')
            if interests:
                interest_objs = []
                for interest in utils._by_css_selector_s(interests,
                                                         '.pv-interest-entity.pv-profile-section__card-item.ember-view'):
                    interest_obj = {'interest': '', 'more': []}
                    interest = utils._by_css_selector(interest, '.pv-entity__summary-info.ember-view')
                    h3 = utils._by_xpath(interest, './h3/span[1]')
                    if h3:
                        if h3.text:
                            interest_obj['interest'] = h3.text
                    p1 = utils._by_xpath(interest, './p[1]')
                    if p1:
                        if p1.text:
                            interest_obj['more'].append({'position': p1.text})

                    p2 = utils._by_xpath(interest, './p[2]')
                    if p2:
                        if p2.text:
                            interest_obj['more'].append({'followers': p2.text})
                    interest_objs.append(interest_obj)
                    interest_obj['type'] = 11
                    interest_obj['ref'] = page_url
                result['properties'].append({'interests': interest_objs, 'type': 11, 'ref': page_url})

            # read skill section
            self.update_progressbar('start reading skill section information', 70)
            self.check_action()
            skill_section = utils._by_css_selector(self.driver, '.pv-skill-categories-section__expanded')
            if skill_section:
                skills = []
                for each in skill_section.find_elements_by_css_selector(
                        '.pv-skill-category-list.pv-profile-section__section-info.mb6.ember-view'):
                    skill = {'title': '', 'more': []}
                    title = utils._by_xpath(each, './h3')
                    if title:
                        if str(title.text).startswith('Other Skills'):
                            skill['title'] = str(title.text).split('\n')[0]
                        else:
                            skill['title'] = title.text

                    each = utils._by_xpath(each, './ol')
                    if each:
                        if utils._by_xpath(each, './li'):
                            for li in each.find_elements_by_xpath('./li'):
                                skill['more'].append(utils._by_xpath(li, './div/p').text)
                    skills.append(skill)
                    # skill['type'] = 11
                    # skill['ref'] = page_url
                    # result['results'].append(skill)

                result['properties'].append({'skills': skills, 'type': 11, 'ref': page_url})

            # read accomplishments section
            self.update_progressbar('start reading accomplishments section information', 80)
            self.check_action()
            temp = utils._by_css_selector(self.driver,
                                          '.pv-profile-section.pv-accomplishments-section.artdeco-container-card.ember-view')
            if temp:
                accomplishments = []
                divs = utils._by_xpath_s(temp, './div')
                if divs:
                    for each in divs:
                        accomplishment = {'title': '', 'type': 11, 'ref': page_url}
                        title = utils._by_xpath(each, './section/div/h3')
                        if title:
                            accomplishment['title'] = title.text

                        lis = []
                        for li in each.find_element_by_xpath('./section/div/div').find_elements_by_css_selector(
                                '.pv-accomplishments-block__summary-list-item'):
                            lis.append(li.text)
                        accomplishment['more'] = lis
                        accomplishments.append(accomplishment)
                        # accomplishment['type'] = 11
                        # accomplishment['ref'] = page_url
                        # result['results'].append(accomplishment)

                    result['properties'].append({'accomplishments': accomplishments, 'type': 11, 'ref': page_url})


                elif utils.check_exists_by_css_selector(temp, '.ember-view'):
                    accomplishments = []
                    for each in temp.find_elements_by_xpath(
                            './div'):
                        accomplishment = {'title': '', 'type': 11, 'ref': page_url}
                        title = utils._by_xpath(each, './section/div/h3')
                        if title:
                            accomplishment['title'] = title.text
                        lis = []
                        for li in each.find_element_by_xpath('./section/div/div').find_elements_by_css_selector(
                                '.pv-accomplishments-block__summary-list-item'):
                            lis.append(li.text)
                        accomplishment['more'] = lis
                        accomplishments.append(accomplishment)
                        # accomplishment['type'] = 11
                        # accomplishment['ref'] = page_url
                        # result['results'].append(accomplishment)

                    result['properties'].append({'accomplishments': accomplishments, 'type': 11, 'ref': page_url})

            self.update_progressbar('whole page is read', 100)
            self.check_action()
        return result

    def search(self, query, number=None):
        self.update_progressbar('search request submit', 10)
        self.check_action()
        if self.__login():
            result = {'results': []}
            if number == 0:
                raise InvalidInputError('number of results must be greater that zero')
            elif number == None:
                number = self.default_number

            self.__search_query(self.driver, query)

            self.driver.execute_script('window.scrollTo({top: document.body.scrollHeight,behavior: "smooth"})')
            self.driver.execute_script('window.scrollTo({top: 0,behavior: "smooth"})')

            self.check_action()
            page1 = self.__exatract_results(self.driver, number)
            result['results'] += page1
            if number:
                if self.check_number >= number:
                    self.update_progressbar('all result retrieved', 100)
                    self.check_action()
                    return result
            flag = True
            while flag:
                next = self.__click_next(self.driver)
                if next:
                    time.sleep(3)
                    self.driver.execute_script('window.scrollTo({top: document.body.scrollHeight,behavior: "smooth"})')
                    self.driver.execute_script('window.scrollTo({top: 0,behavior: "smooth"})')
                    page = self.__exatract_results(self.driver, number)
                    result['results'] += page
                    if number:
                        if self.check_number >= number:
                            self.update_progressbar('all result retrieved', 100)
                            self.check_action()
                            return result
                    if self.check_number % 20 == 0:
                        self.check_action()
                else:
                    flag = False

            return result

    def __search_query(self, driver, search_value):
        search_bar = utils._by_xpath(driver,
                                     '/html/body/nav/div/form/div/div/div/artdeco-typeahead-deprecated/artdeco-typeahead-deprecated-input/input')
        if search_bar:
            search_bar.send_keys(Keys.CONTROL, "a")
            search_bar.send_keys(search_value)
            search_click = utils._by_xpath(driver, '/html/body/nav/div/form/div/div/div/div/button')
            if search_click:
                search_click.click()
                self.update_progressbar('search query is entered', 40)
            if utils._by_xpath(self.driver, "//*[text()='No results found.']"):
                self.update_progressbar('no result found', 30)
                raise ResultNotFoundError('no result found')

    def __exatract_results(self, driver, number=None):
        result = []
        div_result = utils._by_css_selector(driver, '.blended-srp-results-js.pt0.pb4.ph0.container-with-shadow')
        if div_result:
            ul_result = utils._by_css_selector(div_result, '.search-results__list.list-style-none.mt2')
            if ul_result:
                li_results = utils._by_xpath_s(ul_result, './li')
                for li in li_results:
                    person = {'data': '', 'type': 5, 'properties': [],
                              'special_properties': [{'type': 0, 'sub_type': 4}]}
                    div = utils._by_xpath(li, './div/div/div[2]')
                    if div:
                        a = utils._by_xpath(div, './a')
                        if a:
                            # TODO: remove ref from search method
                            # account_id = a.get_attribute('href')
                            # person['properties'].append({'ref': account_id})
                            name = utils._by_xpath(a, './h3/span/span[1]/span[1]')
                            if name:
                                person['data'] = name.text
                            else:
                                person['data'] = 'LinkedIn Member'
                        title = utils._by_xpath(div, './p[1]/span')
                        if title:
                            person['properties'].append({'title': title.text, 'type': 11})
                        location = utils._by_xpath(div, './p[2]/span')
                        if location:
                            person['properties'].append({'location': location.text, 'type': 8})
                    if number:
                        if self.check_number < number:
                            result.append(person)
                            self.check_number += 1
                        else:
                            break
                    else:
                        result.append(person)
        return result

    def __click_next(self, driver):
        div_results = utils._by_css_selector(driver, '.blended-srp-results-js.pt0.pb4.ph0.container-with-shadow')
        if div_results:
            div = utils._by_xpath(div_results, './div[1]')
            if div:
                temp = utils._by_tag_name(div, 'artdeco-pagination')
                if temp:
                    next_button = utils._by_xpath(temp, './button[2]')
                    if next_button:
                        if next_button.get_attribute('disabled'):
                            return False
                        else:
                            driver.execute_script("arguments[0].click();", next_button)
                            return True
