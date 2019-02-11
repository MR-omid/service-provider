from vendor.custom_exception import InvalidInputError
from modules.facebook.v_1_0.facebook import Facebook
from modules.base_module import BaseModule


class Module(BaseModule):
    def __init__(self, task_model):
        super().__init__(task_model)
        self.task_model = task_model

    def run(self):
        result = ''
        parser_data = self.params.get('data')
        if parser_data is None:
            raise InvalidInputError(' missing data keyword')

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
        facebook = Facebook(username, password, parent=self)

        # check_profile, parameter: facebook_id( alias or id)
        if method_id == 1:
            if 'facebook_id' not in parser_data.keys():
                raise InvalidInputError('missing facebook_id keyword')
            else:
                facebook_id = parser_data['facebook_id']
                result = facebook.profile(facebook_id)

        # get_friends, parameter: facebook_id( alias or id)
        elif method_id == 2:
            if 'facebook_id' not in parser_data.keys():
                raise InvalidInputError('missing facebook_id keyword')

            else:
                facebook_id = parser_data['facebook_id']
                result = facebook.get_friends(facebook_id, number)

        # get_follower, parameter: facebook_id( alias or id)
        elif method_id == 3:
            if 'facebook_id' not in parser_data.keys():
                raise InvalidInputError('missing facebook_id keyword')

            else:
                facebook_id = parser_data['facebook_id']
                result = facebook.get_followers(facebook_id, number)

        # get_following, parameter: facebook_id( alias or id)
        elif method_id == 4:
            if 'facebook_id' not in parser_data.keys():
                raise InvalidInputError('missing facebook_id keyword')

            else:
                facebook_id = parser_data['facebook_id']
                result = facebook.get_following(facebook_id, number)

        # search_all, parameter: term
        elif method_id == 5:
            if 'term' not in parser_data.keys():
                raise InvalidInputError('missing term keyword')

            else:
                query = parser_data['term']
                result = facebook.search_all(query, number)
        if result:
            self.result = result
        else:
            raise InvalidInputError('no such method id has been found')
