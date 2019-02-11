from modules.base_module import BaseModule
from vendor.custom_exception import InvalidInputError
from modules.bing_api.v_1_0.Bingsearch_api import BingSearch


class Module(BaseModule):
    def __init__(self, task_model):
        super().__init__(task_model)

    def run(self):
        parser_data = self.params.get('data')
        if parser_data is None:
            raise InvalidInputError(' missing data keyword')

        # if input data has not method_id keyword raise exception
        if 'method_id' not in parser_data.keys():
            raise InvalidInputError('missing method_id keyword')
        if parser_data['method_id']==1:
            # if input data has not api_key keyword raise exception
            if 'api_key' not in parser_data.keys():
                raise InvalidInputError('missing api_key keyword')

            # if input data has not term keyword raise exception
            if 'term' not in parser_data.keys():
                raise InvalidInputError('missing term keyword')

            api_key = parser_data['api_key']
            query = parser_data['term']
            search = BingSearch(api_key, parent=self)
            if 'max_result' in parser_data:
                page_number = parser_data['max_result']
            else:
                page_number = search.pages
            self.result = search.api_searching(query, page_number)
        else:
            raise InvalidInputError('invalid method_id')
