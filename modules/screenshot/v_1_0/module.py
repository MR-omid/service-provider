import base64
import os
import uuid
from extensions.hrobot.v_1_0.Hrobot import Hrobot
from extensions.hrobot.v_1_0.webkit_server import InvalidResponseError
from modules.base_module import BaseModule
from vendor.custom_exception import *
import validators


class Module(BaseModule):
    def update_progressbar(self, message, percent):
        """
        :param message: message of new state
        :param percent: total percent
        update progressbar value of request
        """
        self.progress = {'state': message, 'percent': percent}

    def run(self):
        # extract URL from json file
        parsed_data = self.params.get('data')
        if parsed_data is None:
            raise InvalidInputError('missing data keyword')
        # if input data has not method_id keyword raise exception
        if 'method_id' not in parsed_data.keys():
            raise InvalidInputError('missing method_id keyword')
        if parsed_data['method_id'] == 1:
            if 'url' not in parsed_data.keys():
                raise InvalidInputError('missing url keyword')


            robot = Hrobot()
            # go to URL
            try:
                if not (validators.url(parsed_data['url'])):
                    raise InvalidInputError('invalid url')
                robot.go_to(parsed_data.get('url'))
                self.update_progressbar(" Opening URL: ",
                                        50)
                name = uuid.uuid4().hex + '.png'
                # saving screenshot of URL to file
                robot.save_as_png(name)
                self.check_point()

            except InvalidResponseError:
                raise NetworkError('Unable to find the server')
            f = open(name, "rb")
            file_data = f.read()
            f.close()
            self.update_progressbar(" Saving photo ",
                                    100)
            file_data = base64.b64encode(file_data)
            self.result = file_data
            os.remove(name)
        else:
            raise InvalidInputError('invalid method_id')