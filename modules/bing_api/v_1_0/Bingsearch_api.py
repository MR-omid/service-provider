import http.client, urllib.parse, json
from vendor.custom_exception import WrongApiKeyError


class BingSearch:
    def __init__(self, api_key, parent=None):
        """
        :param api_key:this parameter show api_key for using bing search_api
        """
        self.api_key = api_key
        self.pages = 4
        self.host = "api.cognitive.microsoft.com"
        self.path = "/bing/v7.0/search"
        self.parent = parent  # type: BaseModule

    def update_progressbar(self, message, percent):
        """
        :param message: message of new state
        :param percent: total percent
        update progressbar value of request
        """
        self.parent.progress = {'state': message, 'percent': percent}

    def __bing_web_search(self, search, page_number=None):
        """

        :param search:this parameter show searching term
        :param page_number: the number of requested page for result of searching term
        :return: return header and response of query to bing api server
        """
        if page_number:
            self.pages = page_number
        count = 10 * self.pages
        if self.pages > 5:
            count = 50
        headers = {'Ocp-Apim-Subscription-Key': self.api_key}
        conn = http.client.HTTPSConnection(self.host)
        self.parent.check_point()
        query = urllib.parse.quote(search)
        self.update_progressbar(" connect to bing and initializing request",
                                10)
        # set request to bing.microsoft
        conn.request("GET", self.path + "?q=" + query + "&count=" + str(count), headers=headers)
        response = conn.getresponse()
        headers = [k + ": " + v for (k, v) in response.getheaders()
                   if k.startswith("BingAPIs-") or k.startswith("X-MSEdge-")]
        self.update_progressbar(" preparing result",
                                70)
        return headers, response.read().decode("utf8")

    def api_searching(self, query, page_number):
        """

        :param page_number: the number of requested page for result of searching term
        :param query: query for bing search
        :return:list of searching result in form of entity_property
        """
        return_result = {}
        try:
            headers, result = self.__bing_web_search(query, page_number)
            jres = json.loads(result)
            self.parent.check_point()
            # saving and parsing result, if status code = 401, wrong api key
            if 'statusCode' in jres and jres['statusCode'] == 401:
                raise WrongApiKeyError('Wrong or Invalid API')
            web_result = jres["webPages"]
            value = web_result["value"]
            self.update_progressbar(" parsing result ", 90)
            temp_parsed_result = self.parse_result(value)
            return_result['results'] = temp_parsed_result
            # no result found
            if len(return_result) == 0:
                return_result["results"] = [
                    {"data": " ", "properties": [{'title': '', 'type': 0}, {'description': '', 'type': 0}],
                     "type": 1}]
                return return_result

        except Exception as e:
            raise e

        return return_result

    @staticmethod
    def parse_result(result):
        # static method for convert results to standard
        """
        :param result:list of result to parse
        :return: list of parsed result
        """
        parsed_list = []
        for element in result:
            parsed_list.append({'data': element['displayUrl'], 'type': 1,
                                "properties": [{'title': element["name"], "type": 0},
                                               {'description': element["snippet"], "type": 0}]})
        return parsed_list
