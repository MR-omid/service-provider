from modules.base_module import BaseModule
from vendor.custom_exception import InvalidInputError
from modules.similar_domain.v_1_0.similarDomain import SimilarDomain
import validators

class Module(BaseModule):
    def __init__(self, task_model):
        super().__init__(task_model)

    def run(self):
        # fet parameter from input
        parsed_data = self.params.get('data')
        if parsed_data is None:
            raise InvalidInputError('missing data keyword')
        if 'method_id' not in parsed_data.keys():
            raise InvalidInputError('missing method_id keyword')
        if parsed_data['method_id'] == 1:
            if 'domain' in parsed_data.keys():
                if not (validators.domain(parsed_data['domain'])):
                    raise InvalidInputError('invalid domain')
                sm = SimilarDomain(parent=self)
                self.result = sm.generate_domains(parsed_data['domain'])
            else:
                raise InvalidInputError(' missing domain keyword')
        else:
            raise InvalidInputError('invalid method_id')
