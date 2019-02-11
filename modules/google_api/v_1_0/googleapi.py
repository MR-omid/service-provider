import httplib2
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from vendor.custom_exception import NetworkError, WrongApiKeyError, WrongCseKeyError, ResultNotFoundError


class GoogleSearch:
    def __init__(self, api_key_value, cse_id_value, parent=None):
        """

        :param api_key_value: this parameter determine api key to use google search api service
        :param cse_id_value: custom search engine id to use google search api service
        """

        self.api_key = api_key_value
        self.pages = 3
        self.cse_id = cse_id_value
        self.parent = parent  # type: BaseModule

    def update_progressbar(self, message, percent):
        """
        :param message: message of new state
        :param percent: total percent
        update progressbar value of request
        """
        self.parent.progress = {'state': message, 'percent': percent}

    def get_result(self, search_term, api_key_value, cse_id_value, pages, **kwargs):
        """
        :param search_term: query for search
        :param api_key_value: google api key
        :param cse_id_value: custom search engine id
        :param pages: number of google pages wants to search
        :param kwargs:
        :return: list of result from custom google search api
        """
        return_result = {}
        # build a google custom search v1
        try:
            service = build("customsearch", "v1", developerKey=api_key_value,
                            cache_discovery=False)
        except httplib2.ServerNotFoundError:
            raise NetworkError('Unable to find the server at www.googleapis.com')

        result_list = []
        if pages:
            self.pages = pages
        # iterate on number of excepted result, save one page on each iteration
        for i in range(pages):
            start_point_of_search_result = (i * 10) + 1
            self.parent.check_point()
            try:
                # dictionary which is produced by google custom search api
                result_dict_temp = (
                    service.cse().list(q=search_term, cx=cse_id_value, num=10, start=start_point_of_search_result,
                                       **kwargs).execute())

                # extract items from dictionary and reformat it
                if 'items' in result_dict_temp:
                    temp_parsed_result = self.parse_result(
                        result_dict_temp['items'])
                    for element in temp_parsed_result:
                        result_list.append(element)
                # update progressbar value
                self.update_progressbar(" Pages has been searched: " + str(i + 1),
                                        (100 * (i + 1) / self.pages))
            # invalid api_key or cse_id
            except HttpError as e:
                if "Invalid Value" in str(e):
                    raise WrongCseKeyError("wrong cse_id number")

                elif "Bad Request" in str(e):
                    raise WrongApiKeyError("wrong api_key number")
                elif 'Forbidden' in str(e):
                    raise WrongCseKeyError('wrong api_key or wrong cse_key')
                else:
                    raise NetworkError(e)
            except Exception as e:
                raise NetworkError(e)
            # no result found
            if len(result_list) == 0:
                raise ResultNotFoundError(' can not find result for your query')

        return_result['results'] = result_list
        return return_result

    @staticmethod
    def parse_result(unstructured_data):
        """
        :param unstructured_data: list of result to parse
        :return: list of parsed result
        """
        parsed_list = []
        for element in unstructured_data:
            parsed_list.append({'data': element["link"], 'type': 1,
                                "properties": [{'title': element["title"], 'type': 0},
                                               {'description': element["snippet"], 'type': 0}]})
        return parsed_list
