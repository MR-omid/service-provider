import os
import ast

from extensions.parser.v_1_0.parser import ParseElements, FetchResult
from modules.base_module import BaseModule
from vendor.custom_exception import InvalidInputError


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
        parsed_data = self.params.get('data')
        if parsed_data is None:
            raise InvalidInputError('missing data keyword')
        try:
            if 'on_demand' in parsed_data:
                on_demand = parsed_data['on_demand']
                on_demand = ast.literal_eval(on_demand)
                if len(on_demand) == 0:
                    on_demand = [1, 2, 3, 4, 5, 12]
            else:
                on_demand = [1, 2, 3, 4, 5, 12]

        except Exception:
            on_demand = [1, 2, 3, 4, 12]
        if 'method_id' not in parsed_data.keys():
            raise InvalidInputError('missing method_id keyword')

        if 'region' in parsed_data:
            region = parsed_data['region']
        else:
            region = None

        if parsed_data['method_id'] == 1:
            # if method_id==1 parse content
            if 'content' not in parsed_data.keys():
                raise InvalidInputError('missing content keyword')
            parser_data = parsed_data['content']

        elif parsed_data['method_id'] == 2:
            # if method_id==2 parse from file
            if 'path' not in parsed_data.keys():
                raise InvalidInputError('missing path keyword')
            path = parsed_data['path']

            is_exists = os.path.exists(path)
            if is_exists:
                f = open(path, 'rb')
                parser_data = f.read().decode()
                f.close()

            else:

                parser_data = ""

        else:
            raise InvalidInputError('wrong method_id')

        self.check_point()
        parse = ParseElements()
        fetch = FetchResult()
        return_list = {}
        known_account = []
        e = []
        u = []
        p = []
        i = []
        d = []
        a = []
        if 2 in on_demand:
            # parsing emails from data
            emails = parse.parse_email(content=parser_data)

        else:
            emails = []
        if 4 in on_demand:
            # parsing phone from data
            phones = parse.parse_phone(content=parser_data, region=region)
        else:
            phones = []

        if 3 in on_demand:
            # parsing ip from data
            ips = parse.parse_ip(content=parser_data)
        else:
            ips = []

        if 1 in on_demand or 12 in on_demand or 5 in on_demand:
            # parsing url from data
            urls = parse.parse_url(content=parser_data)
        else:
            urls = []

        self.check_point()
        self.update_progressbar("extract phone, ip, email, urls from text ",
                                50)

        # preparing result
        for email in emails:
            email = email.replace("'", '')
            email = email.replace('"', '')
            if fetch.prepare_email_result(email) is None:
                continue
            else:
                e.append(fetch.prepare_email_result(email))

        for url in urls:
            # separating url and domain from each other
            if str(url).startswith('https://www.facebook.com/') or \
                str(url).startswith('https://www.twitter.com/') or \
                    str(url).startswith('https://www.instagram.com/'):

                if fetch.prepare_account(url) is None:
                    pass
                else:
                    if url not in known_account:
                        known_account.append(url)
                        a.append(fetch.prepare_account(url))
            if fetch.prepare_url_result(url) is None:
                pass
            else:
                u.append(fetch.prepare_url_result(url))
            if fetch.prepare_domain_name_result(url) is None:
                continue
            else:
                d.append(fetch.prepare_domain_name_result(url))
        # checking on demand input
        if 1 not in on_demand:
            u = []
        if 12 not in on_demand:
            d = []
        if 5 not in on_demand:
            a = []
        for phone in phones:
            phone = phone.replace("'", '')
            phone = phone.replace('"', '')
            p.append(fetch.prepare_phone_result(phone))

        for ip in ips:
            ip = ip.replace("'", '')
            ip = ip.replace('"', '')
            i.append(fetch.prepare_ip_result(ip))
        self.update_progressbar(" preparing result ",
                                100)

        return_list["results"] = e + u + p + i + d + a

        self.result = return_list
