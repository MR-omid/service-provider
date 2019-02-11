from modules.instagram.v_1_0.instagram import Instagram
from vendor.custom_exception import InvalidInputError
from modules.base_module import BaseModule


class Module(BaseModule):
    def __init__(self, task_model):
        super().__init__(task_model)
        self.task_model = task_model

    def run(self):
        # checking input and keys
        parser_data = self.params.get('data')
        if parser_data is None:
            raise InvalidInputError(' missing data keyword')
        if 'method_id' not in parser_data.keys():
            raise InvalidInputError('missing method_id keyword')
        if 'username' not in parser_data.keys():
            raise InvalidInputError('missing username keyword')
        if 'password' not in parser_data.keys():
            raise InvalidInputError('missing password keyword')
        # get value from input dic and set on local variable
        method_id = parser_data['method_id']
        username = parser_data['username']
        password = parser_data['password']

        if 'max_result' in parser_data.keys() and str(parser_data['max_result']).isdigit():
            if int(parser_data['max_result']) > 0:
                number = int(parser_data['max_result'])  # optional
            else:
                number = 20
        else:
            number = 20

        # initializing Instagram object
        instagram = Instagram(username, password, number, parent=self)

        # show user_id info in instagram
        if method_id == 1:
            if 'user_id' not in parser_data.keys():
                raise InvalidInputError('missing user_id keyword')
            else:
                user_id = parser_data['user_id']
                self.result = instagram.profile(user_id)[0]

        elif method_id == 2:
            if 'user_id' not in parser_data.keys():
                raise InvalidInputError('missing user_id keyword')
            else:
                user_id = parser_data['user_id']
                self.result = instagram.get_follower_following(user_id, 'follower')

        elif method_id == 3:
            if 'user_id' not in parser_data.keys():
                raise InvalidInputError('missing user_id keyword')
            else:
                user_id = parser_data['user_id']
                self.result = instagram.get_follower_following(user_id, 'following')

        elif method_id == 4:
            if 'phone_number' not in parser_data.keys():
                raise InvalidInputError('missing phone_number keyword')
            else:
                phone_number = parser_data['phone_number']
                self.result = instagram.search_number(phone_number)

        elif method_id == 5:
            if 'query' not in parser_data.keys():
                raise InvalidInputError('missing user_id keyword')
            else:
                query = parser_data['query']
                self.result = instagram.search_by_query(query)
        else:
            raise InvalidInputError(' in valid method_id')
