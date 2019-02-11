from modules.ip2location.v_1_0.ip2location import IP2Location
from vendor.custom_exception import InvalidInputError
from modules.base_module import BaseModule


class Module(BaseModule):
    def __init__(self, task_model):
        super().__init__(task_model)

    def run(self):
        # checking input and keys
        parser_data = self.params.get('data')
        if parser_data is None:
            raise InvalidInputError(' missing data keyword')

        if 'method_id' not in parser_data.keys():
            raise InvalidInputError('missing method_id keyword')
        if 'api_key' not in parser_data.keys():
            raise InvalidInputError('missing api_key keyword')

        # get value from input dic and set on local variable
        method_id = parser_data['method_id']
        api_key = parser_data['api_key']

        # initializing IP2Location object
        ip2location = IP2Location(api_key, parent=self)

        # get ip info
        if method_id == 1:
            if 'ip' not in parser_data.keys():
                raise InvalidInputError('missing ip keyword')
            self.result = ip2location.get_ip_info(parser_data['ip'])

        # check if ip is proxy
        elif method_id == 2:

            if 'ip' not in parser_data.keys():
                raise InvalidInputError('missing ip keyword')

            self.result = ip2location.ip_is_proxy(parser_data['ip'])
        # check api_balance
        elif method_id == 3:
            self.result = ip2location.get_ip_info_balance()
        elif method_id == 4:
            self.result = ip2location.get_ip_is_proxy_balance()
        else:
            raise InvalidInputError('invalid method_id')
