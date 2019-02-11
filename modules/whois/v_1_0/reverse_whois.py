import json
import urllib
from urllib.error import URLError
from vendor.custom_exception import NetworkError, WrongApiKeyError, ResultNotFoundError, InvalidInputError
import re


def get_whois_by_email(email, api_key):
    """
    :param email: whois email requested
    :param api_key: optional, for whoxy.com api
    return whois info of domain
    """
    pattern = re.compile("[\w\.-]+@[\w\.-]+\.\w+")
    if (pattern.match(email)) == None:
        raise InvalidInputError('email format is invalid')
    try:
        url_request = "http://api.whoxy.com/?key=%s&reverse=whois&email=%s" % (api_key, email)
        with urllib.request.urlopen(
                url_request) as url:
            data = json.loads(url.read().decode())
            if 'status_reason' in data:
                if data['status_reason'] == 'Incorrect API Key':
                    raise WrongApiKeyError('wrong or invalid api key')
                else:
                    raise InvalidInputError(data['status_reason'])
    except URLError:
        raise NetworkError('can not access whoxy.com')
    result={'results': parse_reverse(data)}
    return result


def get_whois_by_name(name, api_key):
    """
    :param name: whois name requested
    :param api_key: optional, for whoxy.com api
    return whois info of name
    """
    try:
        if ' ' in name:
            name = name.replace(' ', '+')
        url_request = "http://api.whoxy.com/?key=%s&reverse=whois&name=%s" % (api_key, name)
        with urllib.request.urlopen(
                url_request) as url:
            data = json.loads(url.read().decode())
            if 'status_reason' in data:
                if data['status_reason'] == 'Incorrect API Key':
                    raise WrongApiKeyError('wrong or invalid api key')
                else:
                    raise InvalidInputError(data['status_reason'])
    except URLError:
        raise NetworkError('can not access whoxy.com')
    result={'results': parse_reverse(data)}
    return result


def parse_reverse(data):
    """
    :param data: use this data for parsing and get final result
    return parsed data
    """
    known_value = []
    result_list = []
    if 'search_result' in data:
        search_list = data['search_result']
    else:
        raise ResultNotFoundError('not found any whois for your request')
    for search in search_list:
        temp_result = {'data': '', 'type': 12, 'properties': []}
        if 'domain_name' in search:
            if search['domain_name'] not in known_value:
                known_value.append(search['domain_name'])
            temp_result['data'] = search['domain_name']
        if 'registrant_contact' in search:
            if 'full_name' in search['registrant_contact']:
                temp_result['properties'].append(
                    {'registrant_name': search['registrant_contact']['full_name'], 'type': 11})

            else:
                temp_result['properties'].append({'registrant_name': '', 'type': 11})

            if 'email_address' in search['registrant_contact']:
                temp_result['properties'].append(
                    {'registrant_email_address': search['registrant_contact']['email_address'], 'type': 2})
            else:
                temp_result['properties'].append({'registrant_email_address': '', 'type': 2})
        else:
            temp_result['properties'].append({'registrant_email_address': '', 'type': 2})
            temp_result['properties'].append({'registrant_name': '', 'type': 11})

        if 'domain_registrar' in search:
            if 'registrar_name' in search['domain_registrar']:
                temp_result['properties'].append(
                    {'registrar_name': search['domain_registrar']['registrar_name'], 'type': 11})

            else:
                temp_result['properties'].append({'registrar_name': '', 'type': 11})
        else:
            temp_result['properties'].append({'registrar_name': '', 'type': 11})

        if 'expiry_date' in search:
            temp_result['properties'].append({'expiration_date': search['expiry_date'], 'type': 0})
        else:
            temp_result['properties'].append({'expiration_date': '', 'type': 0})

        result_list.append(temp_result)
    return result_list
