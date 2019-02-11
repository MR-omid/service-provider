# -*- coding: utf-8 -*-
import os

from dateutil.parser import parse
import phonenumbers
import validators
import re

from components.utils import ApiLogging
from extensions.parser.v_1_0.Verify import Verify_email
from urllib.parse import urlparse
import validate_email
from urlextract import URLExtract


class BaseTypeClass(object):
    def __init__(self):
        pass

    @staticmethod
    def _is_dict(_type):
        """

        :param _type: an object to check it's type
        :return: a boolean value that show object is dictionary or not
        """
        return isinstance(_type, dict)

    @staticmethod
    def _is_string(_type):
        """

        :param _type:an object to check it's type
        :return: a boolean value that show object is string or not
        """
        return isinstance(_type, str)

    @staticmethod
    def _is_int(_type):
        """

        :param _type: an object to check it's type
        :return: a boolean value that show object is integer or not
        """
        return isinstance(_type, int)

    @staticmethod
    def _is_float(_type):
        """

        :param _type:an object to check it's type
        :return: a boolean value that show object is float or not
        """
        return isinstance(_type, float)

    @staticmethod
    def _is_list(_type):
        """

        :param _type: an object to check it's type
        :return: a boolean value that show object is list or not
        """
        return isinstance(_type, list)

    @staticmethod
    def _is_tuple(_type):
        """

        :param _type: an object to check it's type
        :return: a boolean value that show object is tuple or not
        """
        return isinstance(_type, tuple)

    @staticmethod
    def _is_bin(_type):
        """

        :param _type: an object to check it's type
        :return: a boolean value that show object is binary or not
        """
        return isinstance(_type, bin)

    @staticmethod
    def _is_unicode(_object):
        """

        :param _object: an object to check it's type
        :return: a boolean value that show object is unicode or not
        """
        return isinstance(_object, str)

    @staticmethod
    def _is_bool(_object):
        """

        :param _object: an object to check it's type
        :return: a boolean value that show object is Boolean or not
        """
        return isinstance(_object, bool)


class ValidateTypes(BaseTypeClass):
    def __init__(self):
        super(ValidateTypes, self).__init__()

    def _is_email(self, _object, online=None):
        """
        :param: _object, a Python object
        :return: boolean value for checking if the object is an email adress
        """
        if online:
            # return (self._is_string(_object) or self._is_unicode(_object)) and validate_email.validate_email(_object,
            #                                                                                                 verify=True)
            return (self._is_string(_object) or self._is_unicode(_object)) and Verify_email.validate_email(_object,
                                                                                                           check_mx=True)
        else:
            return (self._is_string(_object) or self._is_unicode(_object)) and validate_email.validate_email(_object)

    def _is_phone_number(self, _object):
        """
        :param: _object, a Python object
        :return: boolean value for checking if the object is phone number
        """

        if self._is_string(_object) or self._is_unicode(_object):
            phone_flag = False
            try:
                z = phonenumbers.parse(_object, None)
                if phonenumbers.is_valid_number(z):
                    phone_flag = True
            except:
                phone_flag = False

            return phone_flag
        return False

    def _is_url(self, _object):
        """
        :param: _object, a Python object
        :return: boolean value for checking if the object is a  url address
        """
        if self._is_string(_object) or self._is_unicode(_object):
            if validators.url(_object):
                url_flag = True
            else:
                url_flag = False
            return url_flag
        return False

    def _is_ip(self, _object):
        """
        :param _object:a python object
        :return: boolean value for checking if the object is a  ip address
        """
        if self._is_string(_object) or self._is_unicode(_object):
            ip_flag = False
        try:
            host_bytes = _object.split('.')
            valid = [int(b) for b in host_bytes]
            valid = [b for b in valid if 0 <= b <= 255]
            if len(host_bytes) == 4 and len(valid) == 4:
                ip_flag = True
            else:
                ip_flag = False
            return ip_flag
        except:
            return False

    def _is_date(self, _object):
        """

        :param _object:a python object
        :return:  boolean value for checking if the object is a standard date
        """
        if not self._is_string(_object) and not self._is_unicode(_object):
            return False
        try:
            parse(_object)
            return True
        except (OverflowError, ValueError):
            return False


class ParseElements(ValidateTypes):
    def parse_email(self, content):
        """
        :param content:content of a file for parsing
        :return: list of parsed email from content
        """
        email_regs = r'(\b[\w\.-]+@[\w\.-]+\.\w{2,4}\b)|(\b[\w\.-]+_at_[\w\.-]+\.\w{2,4}\b)|(\b[\w\.-]+\[at\][' \
                     r'\w\.-]+\.\w{2,4}\b)|(\b[\w\.-]+\[at\][\w\.-]+\[dot\]\w{2,4}\b) '
        email_list = list()
        email_result = list()
        email_pattern = re.compile(email_regs)
        match1 = email_pattern.findall(content)
        for item in match1:
            for email in item:
                if email != '' and email not in email_list:
                    email_list.append(email)
        # uncomment below code for validate if email is online or not
        # for email in email_list:
        #     if self._is_email(email, online=True):
        #         email_result.append(email)
        # return email_result
        return email_list

    def parse_phone(self, content, region):
        """
        :param content: content of a file for parsing
        :param region: this parameter determine country region  for parsing phone.for example IR for iran
        :return: list of parsed phone from content
        """
        phone_list = list()
        # using phonenumber google lib to extract phone number
        for match in phonenumbers.PhoneNumberMatcher(content, region):
            a = phonenumbers.format_number(match.number, phonenumbers.PhoneNumberFormat.E164)
            if a not in phone_list:
                phone_list.append(a)

        # using telephone tag to extract phone number
        phones_tag = re.findall('"telephone": ".*"', content)
        for item in phones_tag:
            single_phone = item.replace('"telephone": ', '').replace('"', '')
            if single_phone not in phone_list:
                phone_list.append(single_phone)

        # using href to extract phones
        phones = re.findall(r'href\s?=\s?[\'"]?([^\'" >]+)', content)
        for phone in phones:
            if phone.startswith('tel:'):
                single_phone = phone.replace('tel:', '')
                if single_phone != '':
                    if single_phone not in phone_list:
                        phone_list.append(single_phone)
            if phone.startswith('tel:'):
                single_phone = phone.replace('tel:', '')
                if single_phone != '':
                    if single_phone not in phone_list:
                        phone_list.append(single_phone)

            # using href to extract fax number
            elif phone.startswith('fax:'):
                single_fax = phone.replace('fax:', '')
                if single_fax != '':
                    if single_fax not in phone_list:
                        phone_list.append(single_fax)

            # using href to extract sms number
            elif phone.startswith('sms:'):
                single_sms = phone.replace('sms:', '')
                if single_sms != '':
                    if single_sms not in phone_list:
                        phone_list.append(phone.replace(single_sms))

        return phone_list

    def parse_ip(self, content):
        """
        :param content: content of a file for parsing
        :return: list of parsed ip from content
        """
        ip_regs = r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"
        ip_list = list()
        ip_result = list()
        matches = re.finditer(ip_regs, content, flags=re.U)
        for matchNum, match in enumerate(matches):
            ip_list.append(match.group())
        for ip in ip_list:
            if self._is_ip(ip) and ip not in ip_result:
                ip_result.append(ip)

        return ip_result

    def parse_url(self, content):
        """
        :param content: content of a file for parsin
        :return: list of parsed url from content
        """
        extractor = URLExtract()
        url_list = extractor.find_urls(content, only_unique=True)
        return url_list


class FetchResult:
    TLDS = []

    def __init__(self):
        if not FetchResult.TLDS:
            path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            ApiLogging.info("open TLDS file for read...")
            file = open(path + '/vendor/data/tlds.txt')
            lines = file.readlines()

            for line in lines:
                linee = line.strip()
                if len(linee) < 1:
                    continue
                FetchResult.TLDS.append(linee)
            file.close()
        self.internettlds = FetchResult.TLDS

    def prepare_email_result(self, email):
        """
        :param email:an email address
        :return:a dictionary in format of entity_property for email entity
        """
        properties = []
        res = dict()
        tld = ''
        for i in range(0, len(self.internettlds)):
            if (self.internettlds[i]) != '':
                if email.endswith(str(('.' + self.internettlds[i]))):
                    # use .intertld[i] as tld
                    tld = self.internettlds[i]

        if tld == '':
            return None

        else:
            try:
                local_address, domain_name = email.split('@')
            except ValueError:
                try:
                    local_address, domain_name = email.split('_at_')
                except ValueError:
                    return None

        res["data"] = email
        res["type"] = 2
        properties.append({'owener': '', 'type': 11})
        properties.append({'local_address': local_address, 'type': 5})
        properties.append({'domain_name': domain_name, 'type': 12})
        properties.append({'organization': '', 'type': 11})
        properties.append({'isvalid': '', 'type': 0})
        res["properties"] = properties
        return res

    def prepare_phone_result(self, phone):
        """
        :param phone: a phone number
        :return: a dictionary in format of entity_property for phone entity
        """
        res = dict()
        # add ip property
        properties = []
        special_properties = []
        res["data"] = phone
        res["type"] = 4
        properties.append({'operator': '', 'type': 11})
        properties.append({'location': '', 'type': 11})
        properties.append({'country_code': '', 'type': 0})
        properties.append({'phone_type': '', 'type': 0})
        special_properties.append({'sub_type': 0, 'type': 0})
        res["properties"] = properties
        res['special_properties'] = special_properties
        return res

    def prepare_ip_result(self, ip):
        """
        :param ip:and ip addresss
        :return: a dictionary in format of entity_property for ip entity
        """
        # add ip property
        res = dict()
        properties = []
        special_properties = []
        res["data"] = ip
        res["type"] = 3
        properties.append({'country': '', 'type': 11})
        properties.append({'state': '', 'type': 11})
        res["properties"] = properties
        special_properties.append({'is_site_local': '', 'type': 0})
        special_properties.append({'is_link_local': '', 'type': 0})
        special_properties.append({'is_reserved': '', 'type': 0})
        special_properties.append({'is_private': '', 'type': 0})
        special_properties.append({'is_global': '', 'type': 0})
        special_properties.append({'is_multicast': '', 'type': 0})
        special_properties.append({'is_loopback': '', 'type': 0})
        special_properties.append({'is_unspecified': '', 'type': 0})
        special_properties.append({'version_type': '', 'type': 0})
        res["special_properties"] = special_properties
        return res

    def prepare_url_result(self, url):
        """
        :param url:an url address
        :return: a dictionary in format of entity_property for url entity
        """
        res = dict()
        properties = []
        special_properties = []
        parse_object = urlparse(url)
        # urlparse bug, if domain has not scheme can not parse it. add  temporary scheme to domain to parse correctly
        if parse_object.netloc == '':
            url_edit = 'http://' + url
            parse_object_edit = urlparse(url_edit)
        else:
            parse_object_edit = parse_object
        # if parseurl (after add shceme) has'nt path, or the original domain has'nt scheme,it's not URL it's domain name
        if parse_object_edit.path == '' and parse_object.scheme == '':
            return None
        if not (validators.url(url)):
            return None
        res["data"] = url
        res["type"] = 1
        properties.append({'domain_name': parse_object_edit.netloc, 'type': 12})
        # use the last part of domain name as tld.
        properties.append({'tld': parse_object_edit.netloc.split('.')[-1], 'type': 11})
        special_properties.append({'query': parse_object_edit.query, 'type': 0})
        special_properties.append({'fragment': parse_object_edit.fragment, 'type': 0})
        special_properties.append({'scheme': parse_object.scheme, 'type': 0})
        special_properties.append({'path': parse_object_edit.path, 'type': 0})
        res["properties"] = properties
        res["special_properties"] = special_properties
        return res

    def prepare_account(self, account):
        """
        :param account:an url of account
        :return: a dictionary in format of entity_property for url entity
        """
        import re
        result = {'type': '', 'data': '', 'properties': [], 'special_properties': []}
        facebook_pattern = re.compile('https://www.facebook.com/.*')
        twitter_pattern = re.compile('https://www.twitter.com/.*')
        instagram_pattern = re.compile('https://www.instagram.com/.*')
        instagram_pattern2 = re.compile('instagram.com/.*')
        linkdin_pattern = re.compile('https://www.linkdin.com/.*')

        if facebook_pattern.match(account) is not None:
            if account.count('/') == 3:
                result['data'] = account.split('/')[-1]
                result['type'] = 5
                result['special_properties'].append({'sub_type': 1, 'type': 0})
                result['properties'].append({'ref': account, 'type': 0})
                return result
        elif twitter_pattern.match(account) is not None:
            if account.count('/') == 3:
                result['data'] = account.split('/')[-1]
                result['type'] = 5
                result['special_properties'].append({'sub_type': 2, 'type': 0})
                result['properties'].append({'ref': account, 'type': 0})
                return result

        elif instagram_pattern2.match(account) is not None:
            if account.count('/') == 1:
                result['data'] = account.split('/')[-1]
                result['type'] = 5
                result['special_properties'].append({'sub_type': 3, 'type': 0})
                result['properties'].append({'ref': account, 'type': 0})
                return result

        elif instagram_pattern.match(account) is not None:
            if account.count('/') == 3:
                result['data'] = account.split('/')[-1]
                result['type'] = 5
                result['special_properties'].append({'sub_type': 3, 'type': 0})
                result['properties'].append({'ref': account, 'type': 0})
                return result

        elif linkdin_pattern.match(account) is not None:
            if account.count('/') == 3:
                result['data'] = account.split('/')[-1]
                result['type'] = 5
                result['special_properties'].append({'sub_type': 4, 'type': 0})
                result['properties'].append({'ref': account, 'type': 0})
                return result

        else:
            return None

    def prepare_domain_name_result(self, url):
        """
        :param url: an url address
        :return: a dictionary in format of entity_property for url entity
        """
        res = dict()
        properties = []
        parse_object = urlparse(url)
        # urlparse bug, if domain has not scheme can not parse it. add  temporary scheme to domain to parse correctly
        if parse_object.netloc == '':
            url_edit = 'http://' + url
            parse_object_edit = urlparse(url_edit)
        else:
            parse_object_edit = parse_object

        # if parse url ( after adding shceme) has path, or the original domain has scheme, it's URL not domain name
        if parse_object_edit.path != '' or parse_object.scheme != '':
            return None
        if not (validators.domain(url)):
            return None
        res["type"] = 12
        if parse_object.netloc:
            res["data"] = parse_object.netloc
        else:
            res["data"] = url
        tld = ''
        domain = ''
        sub_domain = ''
        custom_tlds = ['.com', '.ir', '.net', '.org', '.tk', '.me', '.biz']
        for i in range(0, len(custom_tlds)):
            if url.endswith(str((custom_tlds[i]))):
                # use .intertld[i] as tld
                tld = custom_tlds[i]
                # last part after '.' is domain ( after removing tld)
                rest = url.replace(tld, '')
                domain = rest.split('.')[-1]
                # rest is subdomain
                sub_domain = rest.replace(domain, '')
                # removing dot from sub domain
                sub_domain = sub_domain[:-1]
        # if tld is not exist in tld file, use the below code to find domain, tld and subdomain
        if tld == '':
            # use chars that exist after the last '.' as tld
            tld = "." + parse_object.netloc.split(".")[-1]
            # use chars that exist between two last '.' as domain
            rest = parse_object.netloc.replace(tld, '')
            domain = rest.split('.')[-1]
            # use the rest string as sub domain
            sub_domain = rest.replace(domain, '')

        properties.append({'name': domain, 'type': 11})
        properties.append({'subdomain': sub_domain, 'type': 11})
        properties.append({'tld': tld.replace('.', ''), 'type': 11})
        res["properties"] = properties
        return res
