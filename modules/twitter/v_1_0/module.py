import re

from vendor.custom_exception import InvalidInputError
from modules.twitter.v_1_0.twitter import Twitter
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
        if 'consumer_key' not in parser_data.keys():
            raise InvalidInputError('missing consumer_key keyword')
        if 'consumer_secret' not in parser_data.keys():
            raise InvalidInputError('missing consumer_secret keyword')
        if 'access_key' not in parser_data.keys():
            raise InvalidInputError('missing access_key keyword')
        if 'access_secret' not in parser_data.keys():
            raise InvalidInputError('missing access_secret keyword')

        # get value from input dic and set on local variable
        method_id = parser_data['method_id']
        consumer_key = parser_data['consumer_key']
        consumer_secret = parser_data['consumer_secret']
        access_key = parser_data['access_key']
        access_secret = parser_data['access_secret']
        if 'max_result' in parser_data.keys():
            number = parser_data['max_result']  # optional
        else:
            number = None

        # initializing Twitter object
        twitter = Twitter(consumer_key, consumer_secret, access_key, access_secret, parent=self)

        # search twitter by query
        if method_id == 1:
            if 'query' not in parser_data.keys():
                raise InvalidInputError('missing query keyword')
            else:
                query = parser_data['query']
                self.result = twitter.search(query, number)

        # show user by username
        elif method_id == 2:
            if 'user_id' not in parser_data.keys():
                raise InvalidInputError('missing user_id keyword')
            else:
                user_id = parser_data['user_id']
                self.result = twitter.show_user(user_id)

        # get_friends by username
        elif method_id == 3:
            if 'user_id' not in parser_data.keys():
                raise InvalidInputError('missing user_id keyword')
            else:
                user_id = parser_data['user_id']
                self.result = twitter.friends_list(user_id, number)

        # get_followers by username
        elif method_id == 4:
            if 'user_id' not in parser_data.keys():
                raise InvalidInputError('missing user_id keyword')
            else:
                user_id = parser_data['user_id']
                self.result = twitter.follower_list(user_id, number)

        else:
            raise InvalidInputError('invalid method_id')
