import os
import pickle
import subprocess
from PyQt5.QtCore import QThread
from vendor.custom_exception import InvalidInputError
from modules.base_module import BaseModule


class Module(BaseModule):
    def __init__(self, task_model):
        super().__init__(task_model)
        self.task_model = task_model

    def run(self):
        parser_data = self.params.get('data')
        if parser_data is None:
            raise InvalidInputError('missing data keyword')

        if 'method_id' in parser_data.keys():
            method_id = parser_data['method_id']
        else:
            raise InvalidInputError('missing method_id keyword')

        if 'email' in parser_data.keys():
            email = parser_data['email']
        else:
            raise InvalidInputError('missing email keyword')

        if 'password' in parser_data.keys():
            password = parser_data['password']
        else:
            raise InvalidInputError('missing password keyword')

        if 'region' in parser_data.keys():
            region = parser_data['region']
        else:
            raise InvalidInputError('missing region keyword')

        if 'number' in parser_data.keys():
            number = parser_data['number']
        else:
            raise InvalidInputError('missing number keyword')


        if method_id == 1:
            subprocess.call(
                ['python3', '/home/dpe/PycharmProjects/F.SystemAPI.01/modules/truecaller/v_1_0/truecaller.py',
                 email, password, region, number, self.task_model.process_id])

            result_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))) + '/modules/truecaller/v_1_0/storage/' + self.task_model.process_id + '.pkl'
            try:
                with open(result_path, 'rb') as f:
                    content = pickle.load(f)
                    f.close()
                os.remove(result_path)
            except Exception as e:
                print(e)
        else:
            raise InvalidInputError('no such method id has been found')
