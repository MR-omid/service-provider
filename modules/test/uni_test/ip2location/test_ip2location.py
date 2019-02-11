import unittest
from modules.ip2location.v_1_0.ip2location import *
import json
from vendor.custom_exception import InvalidInputError

class TestIp2location(unittest.TestCase):
    ip = '185.81.98.126'
    API_KEY_is_ip_proxy = '2F88280C42'
    API_KEY_get_ip_info = 'C571380781'

    def test_invalid_account(self):
        api_key = '00000'
        with self.assertRaises(WrongApiKeyError):
            IP2Location(api_key).ip_is_proxy(self.ip)

        with self.assertRaises(WrongApiKeyError):
            IP2Location(api_key).ip_is_proxy(self.ip)

    def test_invalid_ip(self):
        ip = '0.0.0.0'
        r = requests.get(
            'https://api.ip2location.com/?ip=' + ip + '&key=' + self.API_KEY_get_ip_info + '&package=WS24&format=json')
        module_result = IP2Location(self.API_KEY_get_ip_info).get_ip_info(ip)
        self.assertEqual(json.loads(r.text)['response'], module_result)

        IP2Location(self.API_KEY_is_ip_proxy).ip_is_proxy(ip)
        with self.assertRaises(InvalidInputError):
            IP2Location(self.API_KEY_is_ip_proxy).ip_is_proxy(ip)

    def test_invalid_balance_get_info(self):
        r = requests.get(
            'https://api.ip2location.com/?ip=' + self.ip + '&key=' + self.API_KEY_get_ip_info +
            '&package=WS24&format=json')
        module_result = IP2Location(self.API_KEY_get_ip_info).get_ip_info(self.ip)
        if IP2Location(self.API_KEY_get_ip_info).get_ip_info_balance()['ip_info_balance'] == '0':
            self.assertEqual(json.loads(r.text)['response'], module_result)

    def test_invalid_balance_is_proxy(self):
        r = requests.get(
            'http://api.ip2proxy.com/?ip=' + self.ip + '&key=' + self.API_KEY_is_ip_proxy + '&package=PX4&format=json')
        module_result = IP2Location(self.API_KEY_get_ip_info).get_ip_info(self.ip)
        if IP2Location(self.API_KEY_is_ip_proxy).get_ip_is_proxy_balance()['ip_is_proxy_balance'] == '0':
            self.assertEqual(json.loads(r.text)['response'], module_result)

    def test_key_for_ip_is_proxy(self):

        r = requests.get(
            'http://api.ip2proxy.com/?ip=' + self.ip + '&key=' + self.API_KEY_is_ip_proxy + '&package=PX4&format=json')

        keys = ["country_name", "region_name", "city_name", "isp", "proxy_type_desc", "is_proxy"]
        if json.loads(r.text)['response'] == 'OK':
            module_result = IP2Location(self.API_KEY_is_ip_proxy).ip_is_proxy(self.ip)
            for each in module_result['special_properties']:
                for k in each.keys():
                    if k != 'type':
                        self.assertIn(k, keys)

    def test_key_for_get_info(self):
        r = requests.get(
            'https://api.ip2location.com/?ip=' + self.ip + '&key=' + self.API_KEY_get_ip_info +
            '&package=WS24&format=json')

        keys = ['mnc', 'isp', 'idd_code', 'country_name', 'time_zone', 'longitude', 'elevation', 'mcc', 'latitude',
                'usage_type_desc',
                'area_code', 'domain', 'region_name', 'zip_code', 'mobile_brand', 'city_name', 'net_speed']
        if json.loads(r.text)['response'] == 'OK':
            module_result = IP2Location(self.API_KEY_get_ip_info).get_ip_info(self.ip, )
            for each in module_result['special_properties']:
                for k in each.keys():
                    if k != 'type':
                        self.assertIn(k, keys)


if __name__ == '__main__':
    unittest.main()
