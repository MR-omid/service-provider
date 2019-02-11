from components.Qhttp import Qhttp
from modules.base_module import BaseModule
from modules.hash.v_1_0.cmd5 import Hash
from vendor.custom_exception import InvalidInputError


class Module(BaseModule):
    def __init__(self, task_model):
        super().__init__(task_model)

    def run(self):
        data = self.params.get('data')
        if data is None:
            raise InvalidInputError('missing data keyword')
        # if input data has not method_id keyword raise exception
        if 'method_id' not in data.keys():
            raise InvalidInputError('missing method_id keyword')
        if data['method_id'] == 1:
            # if input data has not hash_code keyword raise exception
            if 'hash_code' not in data.keys():
                raise InvalidInputError('missing hash_code keyword')
            else:
                hash_code = data.get('hash_code')

            # if input data has not username keyword raise exception
            if 'username' not in data.keys():
                raise InvalidInputError('missing username keyword')
            else:
                username = data.get('username')

            # if input data has not password keyword raise exception
            if 'password' not in data.keys():
                raise InvalidInputError('missing password keyword')
            else:
                password = data.get('password')

            if 'hash_type' is None:
                hash_type = 'md5'
            else:
                hash_type = data.get('hash_type')

            hash = Hash(username, password)
            result = {}
            result_list = []
            decoded = hash.decode(hash_type, hash_code)
            result_list.append({'type': 7, 'data': decoded, 'properties': [{}]})
            result['results'] = result_list
            self.result = result

        if data['method_id'] == 2:
            # if input data has not hash_code keyword raise exception
            if 'hash_code' not in data.keys():
                raise InvalidInputError('missing hash_code keyword')
            else:
                hash_code = data.get('hash_code')

            # if input data has not api_key keyword raise exception
            if 'api_key' not in data.keys():
                raise InvalidInputError('missing api_key keyword')
            else:
                api_key = data.get('api_key')

            # if input data has not email keyword raise exception
            if 'email' not in data.keys():
                raise InvalidInputError('missing email keyword')
            else:
                email = data.get('email')
            self.result = Hash.get_result_by_api(api_key, email, hash_code)

        else:
            raise InvalidInputError('invalid method_id')