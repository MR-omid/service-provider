import re
import urllib.request, json
from urllib.error import URLError

from vendor.custom_exception import NetworkError, WrongApiKeyError, InvalidInputError


class WhoisApi:
    def __init__(self, api_key_value, domain_name, parent=None):
        """
        :param api_key_value: this parameter determine api key to use whoxy api
        :param domain_name: domain for whois request
        :param parent: use this to check flags of pause and cancel
        """

        self.api_key = api_key_value
        self.domain = domain_name
        self.parent = parent  # type: BaseModule

    def update_progressbar(self, message, percent):
        """
        :param message: message of new state
        :param percent: total percent
        update progressbar value of request
        """
        self.parent.progress = {'state': message, 'percent': percent}

    @staticmethod
    def check_balance(api_key):
        try:
            balance = ''
            key = api_key
            url_request = "http://api.whoxy.com/?key=%s&account=balance" % (key)
            with urllib.request.urlopen(
                    url_request) as url:
                data = json.loads(url.read().decode())
                if 'status_reason' in data:
                    if data['status_reason'] == 'Incorrect API Key':
                        raise WrongApiKeyError('wrong or invalid api key')
                    else:
                        raise InvalidInputError(data['status_reason'])

                if 'live_whois_balance' in data:
                    balance = data['live_whois_balance']

            if balance:
                return balance
            else:
                return 'can not get balance'
        except URLError:
            raise NetworkError('can not access whoxy.com')

    def get_result(self):
        """
        :return: whois info of domain
        """
        # build a whois request
        try:
            key = self.api_key
            domain = self.domain
            url_request = "http://api.whoxy.com/?key=%s&whois=%s" % (key, domain)
            with urllib.request.urlopen(
                    url_request) as url:
                data = json.loads(url.read().decode())
                if 'status_reason' in data:
                    if data['status_reason'] == 'Incorrect API Key':
                        raise WrongApiKeyError(data['status_reason'])
                    else:
                        raise InvalidInputError(data['status_reason'])
        except URLError:
            raise NetworkError('can not access whoxy.com')
        self.parent.check_point()
        self.update_progressbar('parsing result', 80)
        unstructured_res = WhoisApi.parse_unstructure(data)
        email_res = WhoisApi.get_emails(data)
        phone_res = WhoisApi.parse_phone(data)
        name_res = WhoisApi.get_names(data)

        result_list = []
        properties_list = []
        special_properties_list = []

        result = {'results': [], 'special_properties': [], 'properties': []}

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

    @staticmethod
    def parse_unstructure(parsed_data):
        """
        :param parsed_data: list of result to parse
        :return: list of parsed result
        """

        """
         extract all contacts from whois parsed data
        :param data: determine raw input data
        :param as_json: a boolean that determine we want json result or not
        :return: a dictionary contains main structure data with it' properties
        """
        result = {"properties": {}, "results": {'data': {}}, "special_properties": {}}
        special_properties_list = []
        properties_list = []

        # creating ref block in result block
        result['results'].update({'ref': {'task': 'whois', 'whois_for': '', 'whois_from': ''}})
        result['results'].update({'type': 0})
        if 'domain_name' in parsed_data and len(parsed_data['domain_name']) > 0:
            result['results']['ref']['whois_for'] = parsed_data['domain_name']

        if 'whois_server' in parsed_data:
            result['results']['ref']['whois_from'] = parsed_data['whois_server']

        # creating special_properties in main structure
        if 'domain_registered' in parsed_data:

            if parsed_data['domain_registered'] == 'yes':
                special_properties_list.append({'valid': True, 'type': 0})
                special_properties_list.append({'should_be_fixed': False, 'type': 0})
                special_properties_list.append({'has_dns': True, 'type': 0})
            else:
                special_properties_list.append({'valid': False, 'type': 0})
                special_properties_list.append({'should_be_fixed': False, 'type': 0})
                special_properties_list.append({'has_dns': False, 'type': 0})

        # creating properties of main structure
        # creating regitrant_name and email_address
        try:
            if 'registrant_contact' in parsed_data:
                if 'full_name' in parsed_data['registrant_contact']:
                    properties_list.append(
                        {'registrant_name': parsed_data['registrant_contact']['full_name'], 'type': 11})
                else:
                    properties_list.append(
                        {'registrant_name': '', 'type': 11})
                if 'email_address' in parsed_data['registrant_contact']:
                    properties_list.append(
                        {'registrant_email_address': parsed_data['registrant_contact']['email_address'], 'type': 2})
                else:
                    properties_list.append({'registrant_name': '', 'type': 2})
            else:
                properties_list.append(
                    {'registrant_name': '', 'type': 11})
                properties_list.append({'registrant_name': '', 'type': 2})
        except Exception:
            properties_list.append(
                {'registrant_name': '', 'type': 11})

        # creating admin_name
        try:
            if 'administrative_contact' in parsed_data:
                if 'full_name' in parsed_data['administrative_contact']:
                    properties_list.append(
                        {'admin_name': parsed_data['administrative_contact']['full_name'], 'type': 11})
                else:
                    properties_list.append(
                        {'admin_name': '', 'type': 11})
            else:
                properties_list.append(
                    {'admin_name': '', 'type': 11})
        except Exception:
            properties_list.append({'admin_name': '', 'type': 11})

        # creating tech_name
        try:
            if 'technical_contact' in parsed_data:
                if 'full_name' in parsed_data['technical_contact']:
                    properties_list.append({'tech_name': parsed_data['technical_contact']['full_name'], 'type': 11})
                else:
                    properties_list.append({'tech_name': '', 'type': 11})
            else:
                properties_list.append({'tech_name': '', 'type': 11})
        except Exception:
            properties_list.append({'tech_name': '', 'type': 11})

        # creating regitrar_name and website
        try:
            if 'domain_registrar' in parsed_data:
                if 'registrar_name' in parsed_data['domain_registrar']:
                    properties_list.append(
                        {'registrar_name': parsed_data['domain_registrar']['registrar_name'], 'type': 11})
                else:
                    properties_list.append({'registrar_name': '', 'type': 11})

                if 'registrar_website_url' in parsed_data['domain_registrar']:
                    properties_list.append(
                        {'registrar_website_url': parsed_data['domain_registrar']['registrar_website_url'], 'type': 1})
                elif 'website_url' in parsed_data['domain_registrar']:
                    properties_list.append(
                        {'registrar_website_url': parsed_data['domain_registrar']['website_url'],
                         'type': 1})
                else:
                    properties_list.append({'registrar_website_url': '', 'type': 1})
            else:
                properties_list.append({'registrar_name': '', 'type': 11})
                properties_list.append({'registrar_website_url': '', 'type': 1})

        except Exception:
            properties_list.append({'registrar_name': '', 'type': 11})
            properties_list.append({'registrar_website_url': '', 'type': 1})

        # creatin name_servers
        if 'name_servers' in parsed_data and len(parsed_data['name_servers']) > 0:
            known_dns = []
            for i in parsed_data['name_servers']:
                if i in known_dns:
                    continue
                else:

                    properties_list.append({'dns': i, 'type': 3})
                    known_dns.append(i)
        else:
            properties_list.append({'dns': '', 'type': 3})

        if 'create_date' in parsed_data and len(parsed_data['create_date']) > 0:
            properties_list.append({'registration_date': parsed_data['create_date'], 'type': 0})
        else:
            properties_list.append({'registration_date': '', 'type': 0})

        if 'expiry_date' in parsed_data and len(parsed_data['expiry_date']) > 0:
            properties_list.append({'expiration_date': parsed_data['expiry_date'], 'type': 0})
        else:
            properties_list.append({'expiration_date': '', 'type': 0})

        result['special_properties'] = special_properties_list
        result['properties'] = properties_list

        # creating data of registrant, admin, tech info for result
        contacts = {'registrant_contact': [], 'administrative_contact': [], 'technical_contact': [], }
        if 'registrant_contact' in parsed_data:
            contacts['registrant_contact'].append(parsed_data['registrant_contact'])
        else:
            result['results']['data'].update({'registrant_contact': {'name': '', 'phone': '', 'fax': '', 'country': '',
                                                                     'city': '', 'street': '', 'email': '',
                                                                     'type': 'whois_contact_name'}})

        if 'administrative_contact' in parsed_data:
            contacts['administrative_contact'].append(parsed_data['administrative_contact'])
        else:
            result['results']['data'].update({'administrative_contact': {'name': '', 'phone': '', 'fax': '',
                                                                         'country': '', 'city': '', 'street': '',
                                                                         'email': '', 'type': 'whois_contact_name'}})

        if 'technical_contact' in parsed_data:
            contacts['technical_contact'].append(parsed_data['technical_contact'])
        else:
            result['results']['data'].update({'technical_contact': {'name': '', 'phone': '', 'fax': '', 'country': '',
                                                                    'city': '', 'street': '', 'email': '',
                                                                    'type': 'whois_contact_name'}})

        for contact, info in contacts.items():
            if contact == 'billing':
                continue
            d = {contact: {}}
            d[contact] = {'name': '', 'phone': '', 'fax': '', 'country': '', 'city': '', 'street': '', 'email': ''}
            if info is not None:
                for name in info:
                    for feature in name.keys():
                        if feature == "full_name":
                            d[contact]['name'] = name['full_name']
                        if feature == "phone_number":
                            d[contact]['phone'] = name['phone_number']
                        if feature == "fax_number":
                            d[contact]['fax'] = name['fax_number']
                        if feature == "country_name":
                            d[contact]['country'] = name['country_name']
                        if feature == "city_name":
                            d[contact]['city'] = name['city_name']
                        if feature == "zip_code":
                            d[contact]['postalcode'] = name['zip_code']
                        if feature == "email_address":
                            d[contact]['email'] = name['email_address']
                        if feature == "company_name":
                            d[contact]['organization'] = name['company_name']
            d[contact].update({'type': 'whois_contact_name'})
            result['results']['data'].update(d)

        return result

    @staticmethod
    def parse_phone(parsed_data):
        """
         extract all phone numbers from raw string
        :param parsed_data: determine raw input data
        :return:  a dictionary contains phone data with it' properties
        """
        result = []
        known_values = []

        contacts = {'registrant_contact': [], 'administrative_contact': [], 'technical_contact': [],
                    'domain_registrar' :[]}
        if 'registrant_contact' in parsed_data:
            contacts['registrant_contact'].append(parsed_data['registrant_contact'])
        if 'administrative_contact' in parsed_data:
            contacts['administrative_contact'].append(parsed_data['administrative_contact'])
        if 'technical_contact' in parsed_data:
            contacts['technical_contact'].append(parsed_data['technical_contact'])
        if 'domain_registrar' in parsed_data:
            contacts['domain_registrar'].append(parsed_data['domain_registrar'])
        # parsing phone number from contact block

        for contact, info in contacts.items():
            if info is not None:
                d = {'type': 4, 'data': '', 'properties': {}, 'special_properties': {}, 'ref': {}}
                # properties dictionary
                owener = {'type': 11, 'owner': ''}
                location = {'type': 11, 'location': ''}
                properties_list = []
                special_properties_list = []
                d.update({'ref': {'task': 'whois', 'whois_for': '', 'whois_from': ''}})
                if 'domain_name' in parsed_data and len(parsed_data['domain_name']) > 0:
                    d['ref']['whois_for'] = parsed_data['domain_name']
                if 'whois_server' in parsed_data:
                    d['ref']['whois_from'] = parsed_data['whois_server']

                for name in info:
                    if "phone_number" in name:
                        if name['phone_number'] in known_values:
                            break
                    for feature in name.keys():
                        if feature == "phone_number":
                            d['data'] = name['phone_number']
                            known_values.append(name['phone_number'])
                        if feature == "full_name":
                            owener['owner'] = name['full_name']

                        if feature =="registrar_name":
                            owener['owner'] = name['registrar_name']
                        if feature == "city_name":
                            location['location'] = name['city_name']
                        # prevent from create result if phone number of contact is not available
                if d['data'] == '':
                    continue
                properties_list.append(location)
                properties_list.append(owener)
                special_properties_list.append({'phone_type': '', 'type': 0})
                special_properties_list.append({'country_code': '', 'type': 0})
                special_properties_list.append({'operator': '', 'type': 0})
                special_properties_list.append({'is_valid': '', 'type': 0})
                d['special_properties'] = special_properties_list
                d['properties'] = properties_list
                result.append(d)
        return result

    @staticmethod
    def get_names(parsed_data):
        """
         extract all name from raw string
        :param parsed_data: determine raw input data
        :return:  a dictionary contains name data with it' properties
        """
        known_values = []
        result = []
        # get name from contacts
        contacts = {'registrant_contact': [], 'administrative_contact': [], 'technical_contact': [],
                    'domain_registrar': []}
        if 'registrant_contact' in parsed_data:
            contacts['registrant_contact'].append(parsed_data['registrant_contact'])
        if 'administrative_contact' in parsed_data:
            contacts['administrative_contact'].append(parsed_data['administrative_contact'])
        if 'technical_contact' in parsed_data:
            contacts['technical_contact'].append(parsed_data['technical_contact'])
        if 'domain_registrar' in parsed_data:
            contacts['domain_registrar'].append(parsed_data['domain_registrar'])

        for contact, info in contacts.items():
            # properties dictionary
            fax = {'fax': '', 'type': 4}
            phone = {'phone': '', 'type': 4}
            country = {'country': '', 'type': 11}
            street = {'street': '', 'type': 8}
            city = {'city': '', 'type': 11}
            email = {'email': '', 'type': 2}
            if info is not None:
                d = {'type': 11, 'data': '', 'properties': {}, 'special_properties': {}, 'ref': {}}
                properties_list = []
                special_properties_list = []
                d.update({'ref': {'task': 'whois', 'whois_for': '', 'whois_from': ''}})
                if 'domain_name' in parsed_data and len(parsed_data['domain_name']) > 0:
                    d['ref']['whois_for'] = parsed_data['domain_name']
                if 'whois_server' in parsed_data:
                    d['ref']['whois_from'] = parsed_data['whois_server']

                for name in info:
                    if 'full_name' in name:
                        if name['full_name'] in known_values:
                            break
                    if 'registrar_name' in name:
                        if name['registrar_name'] in known_values:
                            break

                    for feature in name.keys():
                        if feature == 'full_name':
                            d['data'] = name['full_name']
                            known_values.append(name['full_name'])
                        if feature == 'registrar_name':
                            d['data'] = name['registrar_name']
                            known_values.append(name['registrar_name'])
                        if feature == 'city_name':
                            city['city'] = name['city_name']
                        if feature == 'street_name':
                            street['street'] = name['street_name']
                        if feature == 'country_name':
                            country['country'] = name['country_name']
                        if feature == 'phone_number':
                            phone['phone'] = name['phone_number']
                        if feature == 'fax_number':
                            fax['fax'] = name['fax_number']
                        if feature == 'email_address':
                            email['email'] = name['email_address']
                # if name is null, discard other info
                if d['data'] == '':
                    continue
                # saving name special properties
                special_properties_list.append({'is_username': False, 'type': 0})
                special_properties_list.append({'is_domain_name': False, 'type': 0})
                special_properties_list.append({'is_public_name': False, 'type': 0})
                special_properties_list.append({'is_account_name': False, 'type': 0})
                d['special_properties'] = special_properties_list
                properties_list.append(fax)
                properties_list.append(phone)
                properties_list.append(country)
                properties_list.append(street)
                properties_list.append(city)
                properties_list.append(email)
                d['properties'] = properties_list
                result.append(d)
        return result

    @staticmethod
    def get_emails(parsed_data):
        """
          extract all emails from raw string
        :param data: determine raw input data
        :return: a dictionary contains email data with it' properties
        """
        result = []
        known_values = []
        contacts = {'registrant_contact': [], 'administrative_contact': [], 'technical_contact': [],
                    'domain_registrar': []}
        if 'registrant_contact' in parsed_data:
            contacts['registrant_contact'].append(parsed_data['registrant_contact'])
        if 'administrative_contact' in parsed_data:
            contacts['administrative_contact'].append(parsed_data['administrative_contact'])
        if 'technical_contact' in parsed_data:
            contacts['technical_contact'].append(parsed_data['technical_contact'])
        if 'domain_registrar' in parsed_data:
            contacts['domain_registrar'].append(parsed_data['domain_registrar'])
        # parsing email address from contact block

        for contact, info in contacts.items():
            if info is not None:
                d = {'type': 2, 'data': '', 'properties': {}, 'special_properties': {}, 'is_valid': False, 'ref': {}}
                # properties dictionary
                is_valid = {}
                owner = {'owner': '', 'type': 11}
                organization = {'organization': '', 'type': 11}
                local_address = {'local_address': '', 'type': 5}
                domain_name = {'domain_name': '', 'type': 12}
                properties_list = []
                special_properties_list = []
                d.update({'ref': {'task': 'whois', 'whois_for': '', 'whois_from': ''}})
                if 'domain_name' in parsed_data and len(parsed_data['domain_name']) > 0:
                    d['ref']['whois_for'] = parsed_data['domain_name']
                if 'whois_server' in parsed_data:
                    d['ref']['whois_from'] = parsed_data['whois_server']

                for name in info:
                    if "email_address" in name:
                        if name['email_address'] in known_values:
                            break
                    for feature in name.keys():
                        if feature == "email_address":
                            d['data'] = name['email_address']
                            known_values.append(name['email_address'])

                        if feature == "full_name":
                            owner['owner'] = name['full_name']
                            properties_list.append(owner)

                        if feature == "city_name":
                            organization['organization'] = name['city_name']
                            properties_list.append(organization)

                        d['is_valid'] = ''
                        is_valid = {'isvalid': '', 'type': 0}

                # prevent from create result if phone number of contact is not available
                if d['data'] == '':
                    continue
                try:
                    domain_name['domain_name'] = d['data'].split('@')[1]
                    local_address['local_address'] = d['data'].split('@')[0]
                    properties_list.append(domain_name)
                    properties_list.append(local_address)
                except:

                    domain_name['domain_name'] = ''
                    local_address['local_address'] = d['data']
                    properties_list.append(domain_name)
                    properties_list.append(local_address)

                d.update({'ref': {'task': 'whois', 'whois_for': '', 'whois_from': '', 'label': ''}})
                d['ref']['label'] = "%s_name" % contact
                if 'domain_name' in parsed_data and len(parsed_data['domain_name']) > 0:
                    d['ref']['whois_for'] = parsed_data['domain_name']
                if 'whois_server' in parsed_data:
                    d['ref']['whois_from'] = parsed_data['whois_server']
                d['properties'] = properties_list
                special_properties_list.append(is_valid)
                d['special_properties'] = special_properties_list
                result.append(d)

        return result
