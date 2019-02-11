from extensions.hrobot.v_1_0.Hrobot import Hrobot
from extensions.hrobot.v_1_0.webkit_server import InvalidResponseError
from vendor.custom_exception import NetworkError, CaptchaNeededError, InternalModuleError


class GoogleSearch(object):
    def __init__(self, parent=None):
        self.robot = Hrobot(None)
        self.robot.set_skip_image_loading(True)
        self.page = 3
        self.parent = parent  # type: BaseModule
        self.progressbar = {'state': 'initializing', 'percent': 0.0}

    # update progressbar message and percent to suitable value
    def update_progressbar(self, message, percent):
        """
        :param message: message of new state
        :param percent: total percent
        update progressbar value of request
        """
        self.parent.progress = {'state': message, 'percent': percent}

    def search(self, query, pages=None):
        """
        :param query: this parameter show searching term
        :param pages:the number of requested page for result of searching term
        :return: list of searching result in form of entity_property
        """
        result_list = []
        return_result = {}

        if pages:
            self.page = pages
        try:
            self.parent.check_point()
            # open google.com and set query value
            try:
                self.robot.go_to('https://www.google.com/ncr')
            except InvalidResponseError:
                raise NetworkError('Unable to find the server at www.google.com')
            query_field = self.robot.find_by_css("input[name='q']")
            if query_field is not None:
                query_field.set_value(query)
                query_field.get_form().submit()
                # iterate on number of excepted result, save one page on each iteration
                for i in range(self.page):
                    self.parent.check_point()
                    result1 = self.robot.find_by_xpath('//div[@id="search"]')
                    result = result1.find_all_by_css('div[class="g"]')
                    pagination = self.robot.find_by_xpath("//*[contains(text(), 'Next')]")
                    result_list.extend(self.parse_result(result))
                    # update progressbar value
                    self.update_progressbar('Pages has been searched:' + str(i + 1),
                                            (100 * (i + 1) / self.page))
                    if pagination is not None:
                        pagination.click()
                    else:
                        break
            if len(result_list) == 0:
                # if the following condition become true, we are faced captcha in search progress
                captcha_field1 = self.robot.find_by_xpath('/html/body/div[1]/form/input[3]')
                captcha_field2 = self.robot.find_by_css('#ctl00_ContentPlaceHolder1_TextBoxCode')
                if captcha_field1 or captcha_field2:
                    raise CaptchaNeededError("it is needed to resolve  captcha")
                else:
                    # no result found
                        return_result["results"] = [
                            {"data": " ", "properties": [{'title': '', 'type': 0}, {'description': '', 'type': 0}],
                             "type": 1}]
                        return return_result

            return_result['results'] = result_list
            return return_result
        finally:
            self.robot.cleanup()

    @staticmethod
    def parse_result(unstructured_data):
        """

       :param unstructured_data: list of result to parse
       :return: list of parsed result
       """

        i = 0
        final_result = []
        resul = {}
        try:
            # creating data in json format
            for res in unstructured_data:
                properties = []
                resul[i] = {'type': 1}
                # add data key to result
                if res.find_by_css('h3 a'):
                    resul[i].update({'data': res.find_by_css('h3 a').get_attr("href").replace("/url?q=", " ")})
                else:
                    resul[i]['data'] = ''

                # add data properties: description, title, type 0 to result
                if res.find_by_css('h3').get_text():
                    properties.append({'title': res.find_by_css('h3').get_text(), 'type': 0})
                else:
                    properties.append({'title': '', 'type': 0})
                if res.find_by_css('span[class="st"]'):
                    properties.append({'description': res.find_by_css('div [class="st"]').get_text(), 'type': 0})
                else:
                    properties.append({'description': '', 'type': 0})
                resul[i]['properties'] = properties
                final_result.append(resul[i])

                i = i + 1

            return final_result
        except Exception as e :
            raise InternalModuleError('bad content to parse' + e)
