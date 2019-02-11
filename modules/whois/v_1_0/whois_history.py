import json
import urllib
from urllib.error import URLError
from vendor.custom_exception import NetworkError, WrongApiKeyError, InvalidInputError, InternalModuleError, \
    ResultNotFoundError
import validators


class WhoisHistory:
    def __init__(self, parent=None):
        self.temp_result = []
        self.return_result = []
        self.parent = parent

    def whois_history(self, domain, api_key):
        """
        :param domain: whois_history domain requested
        :param api_key: optional, for whoxy.com api
        return whois info of domain
        """
        if not (validators.domain(domain)):
            raise InvalidInputError('invalid domain')
        try:
            url_request = "http://api.whoxy.com/?key=%s&history=%s" % (api_key, domain)
            with urllib.request.urlopen(
                    url_request) as url:
                data = json.loads(url.read().decode())
                if 'status_reason' in data:
                    if data['status_reason'] == 'Incorrect API Key':
                        raise WrongApiKeyError('wrong or invalid api key')
                    else:
                        raise InvalidInputError(data['status_reason'])
                elif 'status' in data:
                    if data['status'] == 0:
                        raise InternalModuleError(' something goes wrong in api')
                if 'whois_records' not in data:
                    raise ResultNotFoundError('cant find any result for your request')
        except URLError:
            raise NetworkError('can not access whoxy.com')
        if self.parent:
            self.parent.check_point()
        result = {'results': self.parse_history(data['whois_records'])}
        return result

    def parse_history(self, records):
        """
        :param records: unstructured data for parsing
        return parsed dataa
        """
        if type(records) == list:
            if len(records) > 0:

                # creating current_value for registrant_contact name, email, phone
                self.__create_temp_result(records[0], 11, 'registrant_contact', 'full_name')
                self.__create_temp_result(records[0], 2, 'registrant_contact', 'email_address')
                self.__create_temp_result(records[0], 4, 'registrant_contact', 'phone_number')
                self.__create_temp_result_address(records[0], 'registrant_contact')

                # creating current_value for administrative_contact name, email, phone
                self.__create_temp_result(records[0], 11, 'administrative_contact', 'full_name')
                self.__create_temp_result(records[0], 2, 'administrative_contact', 'email_address')
                self.__create_temp_result(records[0], 4, 'administrative_contact', 'phone_number')
                self.__create_temp_result_address(records[0], 'administrative_contact')

                # creating current_value for technical_contact name, email, phone
                self.__create_temp_result(records[0], 11, 'technical_contact', 'full_name')
                self.__create_temp_result(records[0], 2, 'technical_contact', 'email_address')
                self.__create_temp_result(records[0], 4, 'technical_contact', 'phone_number')
                self.__create_temp_result_address(records[0], 'technical_contact')

                # creating current_value for name_servers
                self.__create_temp_result_nameserver(records[0])

                for record in self.temp_result:
                    # creating history blocks, if current value has been changed in time, append to result in function
                    if record['ref_key'] == 'registrant_contact' and record['type'] == 11:
                        self.__create_history(records, 11, 'registrant_contact', 'full_name', record['data'])

                    if record['ref_key'] == 'registrant_contact' and record['type'] == 2:
                        self.__create_history(records, 2, 'registrant_contact', 'email_address', record['data'])

                    if record['ref_key'] == 'registrant_contact' and record['type'] == 4:
                        self.__create_history(records, 4, 'registrant_contact', 'phone_number', record['data'])

                    if record['ref_key'] == 'registrant_contact' and record['type'] == 8:
                        self.__create_history_address(records, 'registrant_contact',
                                                      record['data'], record['properties'])

                    if record['ref_key'] == 'administrative_contact' and record['type'] == 11:
                        self.__create_history(records, 11, 'administrative_contact', 'full_name', record['data'])

                    if record['ref_key'] == 'administrative_contact' and record['type'] == 2:
                        self.__create_history(records, 2, 'administrative_contact', 'email_address', record['data'])

                    if record['ref_key'] == 'administrative_contact' and record['type'] == 4:
                        self.__create_history(records, 4, 'administrative_contact', 'phone_number', record['data'])

                    if record['ref_key'] == 'administrative_contact' and record['type'] == 8:
                        self.__create_history_address(records, 'administrative_contact',
                                                      record['data'], record['properties'])

                    if record['ref_key'] == 'technical_contact' and record['type'] == 11:
                        self.__create_history(records, 11, 'technical_contact', 'full_name', record['data'])

                    if record['ref_key'] == 'technical_contact' and record['type'] == 2:
                        self.__create_history(records, 2, 'technical_contact', 'email_address', record['data'])

                    if record['ref_key'] == 'technical_contact' and record['type'] == 4:
                        self.__create_history(records, 4, 'technical_contact', 'phone_number', record['data'])

                    if record['ref_key'] == 'technical_contact' and record['type'] == 8:
                        self.__create_history_address(records, 'technical_contact',
                                                      record['data'], record['properties'])

                    if record['ref_key'] == 'name_servers':
                        self.__create_history_name_servers(records, record['data'], record['properties'])

                return self.return_result

    def __create_temp_result(self, record, entity_type, main_key, secondary_key):
        """
        :param record: current record of history
        :param entity_type: type of phone or name or email
        :param main_key: role, like admin and tech
        :param secondary_key: entity like phone and email and name
        return current value of name, phone, email in appropriate format
        """
        if main_key in record:
            if secondary_key in record[main_key]:
                self.temp_result.append(
                    {'ref_key': main_key, 'data': record[main_key][secondary_key], 'type': entity_type})

    def __create_temp_result_address(self, record, main_key):
        """
        :param record: current record of history
        :param main_key: role, like admin and tech
        return current value of address in appropriate format
        """
        address_dic = {'ref_key': main_key, 'data': '', 'type': 8, 'properties': {}}
        if main_key in record:
            if 'mailing_address' in record[main_key]:
                address_dic['data'] = record[main_key]['mailing_address']
            else:
                return
            if 'zip_code' in record[main_key]:
                address_dic['properties']['zip_code'] = record[main_key]['zip_code']
            else:
                address_dic['properties']['zip_code'] = ''

            if 'city_name' in record[main_key]:
                address_dic['properties']['city_name'] = record[main_key]['city_name']
            else:
                address_dic['properties']['city_name'] = ''

            if 'country_name' in record[main_key]:
                address_dic['properties']['country_name'] = record[main_key]['country_name']
            else:
                address_dic['properties']['country_name'] = ''
            self.temp_result.append(
                address_dic)

    def __create_temp_result_nameserver(self, record):
        """
        :param record: current record of history
        return current value of name server in appropriate format
        """
        dict_dns = {'data': '', 'properties': {'other_name_servers': []}, 'type': 12, 'ref_key': 'name_servers'}
        if 'name_servers' in record:
            if type(record['name_servers']) is list:
                try:
                    dict_dns['data'] = record['name_servers'][0]
                except IndexError:
                    return
                try:
                    for i in range(1, len(record['name_servers'])):
                        dict_dns['properties']['other_name_servers'].append(record['name_servers'][i])
                except IndexError:
                    pass
            self.temp_result.append(dict_dns)

    def __create_history(self, records, entity_type, main_key, secondary_key, current_value):
        """
        :param records: records of history
        :param entity_type: type of name, email, phone
        :param main_key: role, like admin , tech
        :param secondary_key: entity, like phone and email and name
        :param current_value: whois_history domain requestedapi
        return history of name, phone, email
        """
        history = []
        current_old_value = ''
        for i in range(1, len(records)):
            # todo: what about add or remove new record in previous history
            if 'query_time' in records[i]:
                time = records[i]['query_time']
            else:
                time = ''
            if main_key in records[i]:
                if secondary_key in records[i][main_key]:
                    if WhoisHistory.__compare(records[i][main_key][secondary_key], current_value):
                        if current_old_value != records[i][main_key][secondary_key]:
                            current_old_value = records[i][main_key][secondary_key]
                            history.append({'data': records[i][main_key][secondary_key],
                                            'type': entity_type, 'more': {'time': time}})

        if len(history) != 0:
            self.return_result.append({'data': current_value, 'type': entity_type,
                                       'properties': {'history': history},
                                       'special_properties': {'ref': main_key}})

    def __create_history_address(self, records, main_key, current_value, properties):
        """
        :param records: records of history
        :param main_key: role, like admin, tech
        :param current_value: current value of mailing address
        :param properties: other info of address, zip code, city name, country name
        return history of address
        """
        history = []
        current_old_value = ''

        for i in range(1, len(records)):
            address_dict = {'data': '',
                            'type': 8, 'more': {'time': '', 'zip_code': '', 'city_name': '', 'country_name': ''}}
            # todo: what about add or remove new record in previous history
            if 'query_time' in records[i]:
                time = records[i]['query_time']
            else:
                time = ''
            if main_key in records[i]:
                if 'mailing_address' in records[i][main_key]:
                    if WhoisHistory.__compare(records[i][main_key]['mailing_address'], current_value):
                        if current_old_value != records[i][main_key]['mailing_address']:
                            current_old_value = records[i][main_key]['mailing_address']
                            address_dict['data'] = records[i][main_key]['mailing_address']
                        else:
                            continue

                        if 'zip_code' in records[i][main_key]:
                            address_dict['more']['zip_code'] = records[i][main_key]['zip_code']
                        if 'city_name' in records[i][main_key]:
                            address_dict['more']['city_name'] = records[i][main_key]['city_name']
                        if 'country_name' in records[i][main_key]:
                            address_dict['more']['country_name'] = records[i][main_key]['country_name']
                        address_dict['more']['time'] = time
                        history.append(address_dict)

        if len(history) != 0:
            self.return_result.append({'data': current_value, 'type': 8,
                                       'properties': {'history': history, 'zip_code': properties['zip_code'],
                                                      'city_name': properties['city_name'],
                                                      'country_name': properties['country_name']},
                                       'special_properties': {'ref': main_key}})

    def __create_history_name_servers(self, records, current_value, properties):
        """
        :param records: records of history
        :param current_value: current value of name server
        :param properties: other current name server
        return history of name server
        """
        history = []
        current_old_value = ''
        for i in range(1, len(records)):
            dns_dict = {'data': '',
                        'type': 12, 'more': {'time': '', 'other_name_servers': []}}
            # todo: what about add or remove new record in previous history
            if 'query_time' in records[i]:
                time = records[i]['query_time']
            else:
                time = ''
            if 'name_servers' in records[i]:
                if type(records[i]['name_servers']) is list:
                    if len(records[i]['name_servers']) != 0:
                        if WhoisHistory.__compare(records[i]['name_servers'][0], current_value):
                            if current_old_value != records[i]['name_servers'][0]:
                                current_old_value = records[i]['name_servers'][0]
                                dns_dict['data'] = records[i]['name_servers'][0]
                            else:
                                continue
                            try:
                                for j in range(1, len(records[i]['name_servers'])):
                                    dns_dict['more']['other_name_servers'].append(records[i]['name_servers'][j])
                            except IndexError:
                                pass
                            dns_dict['more']['time'] = time
                            history.append(dns_dict)

        if len(history) != 0:
            self.return_result.append({'data': current_value, 'type': 12,
                                       'properties': {'history': history,
                                                      'other_name_servers': properties['other_name_servers']},
                                       'special_properties': {'ref': 'name_servers'}})

    @staticmethod
    def __compare(first_val, second_val):
        """
        :param first_val: first value for compare
        :param second_val: second value for compare
        return compare result between first and second
        """
        if not first_val == second_val:
            return True
