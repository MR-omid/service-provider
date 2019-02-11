from extensions.hrobot.v_1_0.Hrobot import Hrobot
from vendor.custom_exception import NetworkError, InternalModuleError
from extensions.hrobot.v_1_0.webkit_server import InvalidResponseError


class BingSearch:
    def __init__(self, parent=None):
        self.robot = Hrobot(None)
        self.robot.set_skip_image_loading(True)
        self.page = 3
        self.parent = parent  # type: BaseModule

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
        :param pages: the number of requested page for result of searching term
        :return:list of searching result in form of entity_property
        """
        final_result = []
        return_result = {}
        if pages:
            self.page = pages
        try:
            # open bing.com and set query value
            try:
                self.robot.go_to('https://www.bing.com')
            except InvalidResponseError:
                raise NetworkError('Unable to find the server at www.bing.com')
            query_field = self.robot.find_by_xpath('//*[@id="sb_form_q"]')
            if query_field:
                query_field.set_value(query)
                search_button = self.robot.find_by_xpath('//*[@id="sb_form_go"]')
                search_button.click()
                # iterate on number of excepted result, save one page on each iteration
                for i in range(self.page):
                    self.parent.check_point()
                    result = self.robot.find_by_xpath('/html/body/div[1]')
                    res = result.find_all_by_css('li[class="b_algo"]')
                    final_result.extend(self.parse_result(res))
                    pagination = self.robot.find_by_xpath("//a[@title='Next page']")
                    if pagination:
                        pagination.click()
                    # update progressbar
                    self.update_progressbar(" Pages has been searched: " + str(i + 1),
                                            (100 * (i + 1) / self.page))

                # no result found
                if len(final_result) == 0:
                    return_result["results"] = [
                        {"data": " ", "properties": [{'title': '', 'type': 0}, {'description': '', 'type': 0}],
                         "type": 1}]
                    return return_result
            return_result["results"] = final_result
            return return_result

        finally:
            self.robot.cleanup()

    @staticmethod
    def parse_result(unstructured_data):
        """

        :param unstructured_data:list of result to parse
        :return:list of parsed result
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
                if res.find_by_css('h2 a').get_attr("href"):
                    resul[i].update({'data': res.find_by_css('h2 a').get_attr("href")})
                else:
                    resul[i]['data'] = ""

                # add data properties: description, title, type 0 to result
                if res.find_by_css('h2').get_text():
                    properties.append({'title': res.find_by_css('h2').get_text(), "type": 0})
                else:
                    properties.append({'title': "", "type": 0})
                if res.find_by_css('div p').get_text():
                    properties.append({'description': res.find_by_css('div p').get_text(), "type": 0})
                else:
                    properties.append({'description': "", "type": 0})

                resul[i]["properties"] = properties
                final_result.append(resul[i])
                i = i + 1

            return final_result
        except Exception as e:
            raise InternalModuleError('bad content' + str(e))
