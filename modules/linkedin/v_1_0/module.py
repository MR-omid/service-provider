from vendor.custom_exception import InvalidInputError
from modules.linkedin.v_1_0.linkedin import Linkedin
from modules.base_module import BaseModule


class Module(BaseModule):
    def __init__(self, task_model):
        super().__init__(task_model)
        self.task_model = task_model

    def run(self):
        parser_data = self.params.get('data')
        if parser_data is None:
            raise InvalidInputError('missing data keyword')

        if 'method_id' not in parser_data.keys():
            raise InvalidInputError('missing method_id keyword')
        if 'username' not in parser_data.keys():
            raise InvalidInputError('missing username keyword')
        if 'password' not in parser_data.keys():
            raise InvalidInputError('missing password keyword')

        method_id = parser_data['method_id']
        username = parser_data['username']
        password = parser_data['password']

        if 'max_result' in parser_data.keys():
            number = int(parser_data['max_result'])  # optional
        else:
            number = None

        linkedin = Linkedin(username, password, parent=self)

        if method_id == 1:
            if 'linkedin_id' not in parser_data.keys():
                raise InvalidInputError('missing linkedin_id keyword')
            else:
                linkedin_id = parser_data['linkedin_id']
                self.result = linkedin.profile(linkedin_id)

        elif method_id == 2:
            if 'query' not in parser_data.keys():
                raise InvalidInputError('missing query keyword')
            else:
                query = parser_data['query']
                self.result = linkedin.search(query, number=number)

        else:
            raise InvalidInputError('no such method id has been found')
