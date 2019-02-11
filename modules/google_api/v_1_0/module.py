from modules.base_module import BaseModule
from vendor.custom_exception import InvalidInputError
from modules.google_api.v_1_0.googleapi import GoogleSearch


class Module(BaseModule):
    def __init__(self, task_model):
        super().__init__(task_model)

    def run(self):
        parser_data = self.params.get('data')
        if parser_data is None:
            raise InvalidInputError('missing data keyword')

        # if input data has not method_id keyword raise exception
        if 'method_id' not in parser_data.keys():
            raise InvalidInputError('missing method_id keyword')
        if parser_data['method_id']==1:

            # if input data has not api_key keyword raise exception
            if 'api_key' not in parser_data.keys():
                raise InvalidInputError('missing api_key keyword')

            # if input data has not cse_id keyword raise exception
            if 'cse_id' not in parser_data.keys():
                raise InvalidInputError('missing cse_id keyword')

            # if input data has not term keyword raise exception
            if 'term' not in parser_data.keys():
                raise InvalidInputError('missing term keyword')

            # set values
            api_key = parser_data['api_key']
            cse_id = parser_data['cse_id']
            query = parser_data['term']
            # create GoogleSearch object and set number of expected result
            search = GoogleSearch(api_key, cse_id, parent=self)
            if 'max_result' in parser_data:
                page_number = parser_data['max_result']
            else:
                page_number = search.pages

            self.result = search.get_result(query, api_key_value=search.api_key, cse_id_value=search.cse_id,
                                            pages=page_number)
        else:
            raise InvalidInputError('invalid method_id')