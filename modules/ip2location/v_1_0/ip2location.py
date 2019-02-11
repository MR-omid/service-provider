import requests
import json
from vendor.custom_exception import WrongApiKeyError, NetworkError, ResultNotFoundError, \
    InsufficientCredit, InternalModuleError


class IP2Location(object):
    """
    :attribute usage_and_proxy_type: usage types as a dictionary
    :attribute get_ip_info_keys: the keys of "special properties"'s value of
    get_ip_info's output class method for mapping them to desire key names as a dictionary
    :attribute ip_is_proxy_keys: the keys of "special properties"'s value of
    ip_is_proxy's output class method for mapping them to desire key names as a dictionary

    """
    usage_and_proxy_type = {'COM': 'Commercial', 'ORG': 'Organization', 'GOV': 'Goverment', 'MIL': 'Military',
                            'EDU': 'University/College/School/', 'LIB': 'Library',
                            'CDN': 'Content Delivery Network', 'ISP': 'Fixed Line ISP', 'MOB': 'Mobile ISP',
                            'DCH': 'Data Center/Web Hosting/Transit', 'SES': 'Search Engine Spider',
                            'RSV': 'Reserved'}

    get_ip_info_keys = {"country_name": 'country_name', "region_name": 'region_name', "city_name": 'city_name',
                        "latitude": 'latitude', "longitude": 'longitude', "zip_code": 'zip_code',
                        "time_zone": 'time_zone', "isp": 'isp', "domain": 'domain', "idd_code": 'idd_code',
                        "area_code": 'area_code', "mobile_brand": 'mobile_brand',
                        "elevation": 'elevation', "usage_type": 'usage_type_desc', "mcc": 'mcc', "mnc": 'mnc',
                        "net_speed": 'net_speed'}

    ip_is_proxy_keys = {"countryName": "country_name", "regionName": "region_name",
                        "cityName": "city_name", "isp": "isp", "proxyType": "proxy_type_desc",
                        "isProxy": "is_proxy"}

    def __init__(self, api_key, parent=None):
        """
        :param api_key: api key
        :param parent: BaseModule, for updating progressbar and check point
        """
        self.api_key = api_key
        self.parent = parent

    def update_progressbar(self, message, percent):
        """
        :param message: message of new state
        :param percent: total percent
        update progressbar value of request
        """
        if self.parent:
            self.parent.progress = {'state': message, 'percent': percent}

    def get_ip_info(self, ip):
        """
        this function get the given ip information
        :return Returns ip information in json format
        """
        api_key = self.api_key
        if self.parent:
            self.parent.check_point()
        self.update_progressbar('set request to get ip info', 20)
        try:
            r = requests.get(
                'https://api.ip2location.com/?ip=' + ip + '&key=' + api_key + '&package=WS24&format=json')
        except (requests.exceptions.RequestException, requests.exceptions.ConnectionError):
            raise NetworkError(' can no access api')
        if r.status_code == 200:
            result = json.loads(r.content.decode())
            temp = list()
            self.update_progressbar('parsing result', 60)
            if self.parent:
                self.parent.check_point()
            if 'response' in result:
                if result['response'] == 'INSUFFICIENT CREDIT':
                    raise InsufficientCredit(result['response'])
                elif result['response'] == 'INVALID ACCOUNT':
                    raise WrongApiKeyError(result['response'])
                else:
                    raise InternalModuleError(result['response'])
            else:
                longitude = 'unknown'
                latitude = 'unknown'
                if result.items():
                    for k, v in result.items():
                        # parsing result
                        if k in ['country_name', 'region_name', 'city_name', 'isp', 'mobile_brand']:
                            temp.append({self.get_ip_info_keys[k]: v, "type": 11})
                        elif k in ['domain']:
                            temp.append({self.get_ip_info_keys[k]: v, "type": 12})

                        elif k in ['usage_type']:
                            for each in v.split('/'):
                                try:
                                    temp.append(
                                        {self.get_ip_info_keys[k]: self.usage_and_proxy_type[each],
                                         "type": 0})
                                except KeyError:
                                    pass

                        elif k in ['latitude', 'zip_code', 'time_zone', 'idd_code', 'area_code', 'elevation', 'mcc',
                                   'mnc',
                                   'net_speed', 'longitude']:
                            temp.append({k: v, "type": 0})
                            if k == 'longitude':
                                longitude = v
                            if k == 'latitude':
                                latitude = v
                        else:
                            pass  # new key is founded
                    geo_coordinates = str(latitude) + ',' + str(longitude)
                    geo_record = {'geo_coordinates': geo_coordinates, 'type' : 14}
                    final = {"properties": [], "special_properties": temp, "results": [geo_record]}
                    return final
                else:
                    raise ResultNotFoundError('no result found for your request')

        else:
            if r.status_code == 404:
                raise ResultNotFoundError('no result found for your request')
            NetworkError('status code: ', r.status_code)

    def ip_is_proxy(self, ip):
        """
        this function specifies whether the given ip is proxy or not
        :return Returns ip information as a dictionary
        """
        api_key = self.api_key
        self.update_progressbar('set request to is it proxy', 20)
        if self.parent:
            self.parent.check_point()
        try:
            r = requests.get(
                'http://api.ip2proxy.com/?ip=' + ip + '&key=' + api_key + '&package=PX4&format=json‬‬')
        except (requests.exceptions.RequestException, requests.exceptions.ConnectionError):
            raise NetworkError(' can not access api')
        if r.status_code == 200:
            result = json.loads(r.content.decode())
            self.update_progressbar('parsing result', 60)
            if self.parent:
                self.parent.check_point()
            if 'response' in result:
                temp = list()
                if result['response'] == 'OK':
                    if result.items():
                        # parsing result
                        for k, v in result.items():
                            if k in ['countryName', 'regionName', 'cityName', 'isp']:
                                temp.append({self.ip_is_proxy_keys[k]: v, "type": 11})

                            elif k in ['proxyType']:
                                for each in v.split('/'):
                                    try:
                                        temp.append(
                                            {self.ip_is_proxy_keys[k]: self.usage_and_proxy_type[each],
                                             "type": 0})
                                    except KeyError:
                                        temp.append(
                                            {self.ip_is_proxy_keys[k]: v,
                                             "type": 0})

                            elif k in ['isProxy']:
                                temp.append({self.ip_is_proxy_keys[k]: v, "type": 0})
                            else:
                                pass
                        final = {"properties": [], "special_properties": temp, "results": []}
                        return final
                    else:
                        raise ResultNotFoundError('no result found for your request')
                else:
                    if result['response'] == 'INSUFFICIENT CREDIT':
                        raise InsufficientCredit(result['response'])
                    elif result['response'] == 'INVALID ACCOUNT':
                        raise WrongApiKeyError(result['response'])
                    else:
                        raise InternalModuleError(result['response'])
            else:
                raise NetworkError(r.status_code)
        else:
            if r.status_code == 404:
                raise ResultNotFoundError('no result found for your request')
            else:
                raise NetworkError('status_code ' + str(r.status_code))

    def get_ip_info_balance(self):
        """
        this function return the get_ip_info balance
        :return Returns api balance as a dictionary

        """
        api_key = self.api_key
        self.update_progressbar('set request to get ip_info balance', 50)
        if self.parent:
            self.parent.check_point()
        try:
            r = requests.get('https://api.ip2location.com/?key=' + api_key + '&check=1‬')
        except (requests.exceptions.RequestException, requests.exceptions.ConnectionError):
            raise NetworkError('can not access api')

        if r.text == 'INVALID ACCOUNT':
            raise WrongApiKeyError(r.text)
        else:
            return {'ip_info_balance': r.text, 'type': 0}

    def get_ip_is_proxy_balance(self):
        """
        this function return the ip_is_proxy balance
        :return Returns api balance as a dictionary
        """
        api_key = self.api_key
        self.update_progressbar('set request to get ip_proxy balance', 50)
        if self.parent:
            self.parent.check_point()
        try:
            r = requests.get('https://api.ip2proxy.com/?key=' + api_key + '&check=1‬')
        except (requests.exceptions.RequestException, requests.exceptions.ConnectionError):
            raise NetworkError(' can not access api')

        if 'response' in json.loads(r.text):
            if json.loads(r.text)['response'] == "INVALID ACCOUNT":
                raise WrongApiKeyError(json.loads(r.text)['response'])
            else:
                return {'ip_is_proxy_balance': json.loads(r.text)['response'], 'type': 0}
