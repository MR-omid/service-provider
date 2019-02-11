from components.utils import to_json
from modules.whois.v_1_0.parser import Parser
from modules.whois.v_1_0.whois import Whois
from modules.whois.v_1_0.whois_api import WhoisApi
from modules.whois.v_1_0.reverse_whois import get_whois_by_email, get_whois_by_name
from modules.whois.v_1_0.whois_history import WhoisHistory

from socket import gaierror
from modules.base_module import BaseModule
from vendor.custom_exception import InvalidInputError, NetworkError, IncorrectDataError
import validators


class Module(BaseModule):
    def __init__(self, task_model):
        super().__init__(task_model)

    def update_progressbar(self, message, percent):
        """
        :param message: message of new state
        :param percent: total percent
        update progressbar value of request
        """
        self.progress = {'state': message, 'percent': percent}

    def run(self):
        # checking input and calling appropriate method
        parser_data = self.params.get('data')
        if parser_data is None:
            raise InvalidInputError('missing data keyword')

        # if input data has not method_id keyword raise exception
        if 'method_id' not in parser_data.keys():
            raise InvalidInputError('missing method_id keyword')

        # get balance
        if parser_data['method_id'] == 0:
            if 'api_key' not in parser_data.keys():
                raise InvalidInputError(' missing api_key keyword')
            api_key = parser_data['api_key']
            self.check_point()
            self.update_progressbar('connecting to whois_api', 40)
            result = {'results': [{'live_whois_balance': WhoisApi.check_balance(api_key), 'type': 0}]}
            self.result = result
        # reverse by email
        elif parser_data['method_id'] == 1:
            if 'email' not in parser_data.keys():
                raise InvalidInputError(' missing email keyword')
            if 'api_key' not in parser_data.keys():
                raise InvalidInputError(' missing api_key keyword')
            api_key = parser_data['api_key']
            email = parser_data['email']
            self.check_point()
            self.update_progressbar('connecting to whois_api', 40)
            self.result = get_whois_by_email(email, api_key)

        # reverse by name
        elif parser_data['method_id'] == 2:
            if 'name' not in parser_data.keys():
                raise InvalidInputError(' missing name keyword')
            if 'api_key' not in parser_data.keys():
                raise InvalidInputError(' missing api_key keyword')
            api_key = parser_data['api_key']
            name = parser_data['name']
            self.check_point()
            self.update_progressbar('connecting to whois_api', 40)
            self.result = get_whois_by_name(name, api_key)

        # get whois by name
        elif parser_data['method_id'] == 3:
            if 'domain' in parser_data.keys():
                domain = parser_data['domain']
                api_key = None
            else:
                raise InvalidInputError('missing domain keyword')
            if 'api_key' in parser_data.keys():
                api_key = parser_data['api_key']

            self.result = self.get_whois_by_domain_api(domain, api_key)
        # get whois_history by name
        elif parser_data['method_id'] == 4:
            if 'domain' in parser_data.keys():
                domain = parser_data['domain']
            else:
                raise InvalidInputError('missing domain keyword')
            if 'api_key' in parser_data.keys():
                api_key = parser_data['api_key']
            else:
                raise InvalidInputError('missing api keyword')
            whois_history = WhoisHistory(parent=self)
            self.check_point()
            self.update_progressbar('get history of domain and parse result', 70)
            self.result = whois_history.whois_history(domain, api_key)

        # get domains hosted from the given ip
        elif parser_data['method_id'] == 5:
            if 'api_key' in parser_data.keys():
                api_key = parser_data['api_key']
            else:
                raise InvalidInputError('missing api_key keyword')
            if 'host' in parser_data.keys():
                host = parser_data['host']
            else:
                raise InvalidInputError('missing host keyword')
            if 'max_results' in parser_data.keys():
                max_results = parser_data['max_results']
            else:
                max_results = 20
            if 'domain_count_flag' in parser_data.keys():
                domain_count_flag = parser_data['domain_count_flag']
            else:
                domain_count_flag = False
            reverse_object = Whois(parent=self)

            self.result = reverse_object.reverse_ip_lookup(host, api_key, domain_count_flag, max_results)
        else:
            raise InvalidInputError('Invalid method id')

    # get whois info, by using domain, method_id_3
    def get_whois_by_domain(self, domain):
        """
        :param domain: whois domain requested
        return whois info of domain
        """
        if not (validators.domain(domain)):
            raise InvalidInputError('invalid domain')

        # use manual whois module for .ir domains
        try:  # using old version of whois

            whois = Whois(parent=self)
            parser = Parser()
            whois_res, dns = whois.get_whois_with_zone(domain)
        except gaierror:  # raise when can not access network
            raise NetworkError('Unable to find the server')
        has_dns = True
        if not dns:
            has_dns = False
        if whois_res == -1:
            raise IncorrectDataError('whois server not found for your domain ')
        unstructured_res = parser.get_main_srtucture(whois_res, has_dns=has_dns)
        email_res = parser.get_emails(whois_res)
        phone_res = parser.get_phones(whois_res)
        name_res = parser.get_names(whois_res)
        result_list = []
        properties_list = []
        special_properties_list = []
        result = {'results': []}
        # create structure data from result
        if unstructured_res:
            result_list.append(unstructured_res['results'])
            special_properties_list = (unstructured_res['special_properties'])
            properties_list = (unstructured_res['properties'])
        # saving emails, phone, names in list of results
        for email in email_res:
            if email:
                result_list.append(email)
        for phone in phone_res:
            if phone:
                result_list.append(phone)
        for name in name_res:
            if name:
                result_list.append(name)
        # if our output is empty, create empty skeleton
        if len(special_properties_list) == 0:
            result['special_properties'] = ''
        else:
            result['special_properties'] = special_properties_list
        if len(properties_list) == 0:
            result['properties'] = ''
        else:
            result['properties'] = properties_list

        result['results'] = result_list
        return result

    def get_whois_by_domain_api(self, domain, api_key=None):
        # using api, for all domain except whois Retrieval failed error in api, that sent to old whois
        # if input data has not api_key keyword raise exception
        if domain.split('.')[-1] == 'ir':
            return self.get_whois_by_domain(domain)
        else:
            if api_key is None:
                raise InvalidInputError('missing api_key keyword')
            self.check_point()
            self.update_progressbar('connecting to whois_api', 40)
            whois_api = WhoisApi(api_key, domain, parent=self)
            try:
                whois_res = whois_api.get_result()
            except InvalidInputError:
                return self.get_whois_by_domain(domain)
            return whois_res
