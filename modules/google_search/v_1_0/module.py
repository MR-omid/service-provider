from modules.base_module import BaseModule
from vendor.custom_exception import InvalidInputError
from modules.google_search.v_1_0.googlesearch import GoogleSearch


class Module(BaseModule):
    def __init__(self, task_model):
        super().__init__(task_model)

    def run(self):
        parser_data = self.params.get('data')
        # if input data has not data keyword raise exception
        if parser_data is None:
            raise InvalidInputError(' missing data keyword')
        # if input data has not method_id keyword raise exception
        if 'method_id' not in parser_data.keys():
            raise InvalidInputError('missing method_id keyword')
        if parser_data['method_id']==1:
            # if input data has not term keyword raise exception
            if 'term' not in parser_data.keys():
                raise InvalidInputError('missing term keyword')

            # set values
            query = parser_data['term']
            # create GoogleSearch object and set number of expected result
            search = GoogleSearch(parent=self)
            if 'max_result' in parser_data:
                page_number = parser_data['max_result']
            else:
                page_number = search.page

            self.result = search.search(query,
                                        pages=page_number)

        else:
            raise InvalidInputError('invalid method_id')