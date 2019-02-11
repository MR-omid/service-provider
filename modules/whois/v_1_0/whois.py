# -*- coding: utf-8 -*-
import re
import socket
from codecs import encode, decode
from urllib.parse import urlparse
import dns.resolver
import requests

from components.Qhttp import Qhttp
from vendor.custom_exception import InvalidInputError, NetworkError, BadRequest, ResultNotFoundError


class Whois(object):
    """   whois for domain and ip   """
    Reverse_IP_Lookup_url = 'https://api.viewdns.info/reverseip'

    def __init__(self, parent=None):
        self.founded_data = None
        self.parent = parent  # type: BaseModule

    def update_progressbar(self, message, percent):
        """
        :param message: message of new state
        :param percent: total percent
        update progressbar value of request
        """
        self.parent.progress = {'state': message, 'percent': percent}

    def domain_whois(self, domain, server="", previous=None, is_ascii=True,
                     server_list=None):
        """
        find domain whois server(s) and get information about it .

        :param domain: domain name (eg: google.com)
        :param server: lookup server
        :param previous: previous server processed for find information `internal use`
        :param is_ascii: set to False if non-unicode domain (eg:دامنه.ایران)
        :param server_list: list of processed servers `internal use`
        :return: whois response
        """

        domain = self.__domain_validate(domain)

        previous = previous or []
        server_list = server_list or []
        target_server = ""
        # Sometimes IANA simply won't give us the right root WHOIS server
        exceptions = {
            ".ac.uk": "whois.ja.net",
            ".ps": "whois.pnina.ps",
            ".buzz": "whois.nic.buzz",
            ".moe": "whois.nic.moe",
            # The following is a bit hacky,
            # but IANA won't return the right answer for example.com because it's a direct registration.

            "example.com": "whois.verisign-grs.com"
        }

        if is_ascii:
            domain = encode(domain if type(domain) is str else decode(domain, "utf8"), "idna").decode()
        if len(previous) == 0 and server == "":
            is_exception = False
            for exception, exc_serv in exceptions.items():
                if domain.endswith((exception,)):
                    is_exception = True
                    target_server = exc_serv
                    break
            if is_exception == False:
                target_server = self.__get_root_server(domain)
                if target_server is False:
                    return -1  # whois server not found and should be fixed if possible
        else:
            self.parent.check_point()
            target_server = server
        if target_server == "whois.jprs.jp":
            request_domain = "%s/e" % domain  # Suppress Japanese output
        elif domain.endswith(".de") and (target_server == "whois.denic.de" or target_server == "de.whois-servers.net"):
            request_domain = "-T dn,ace %s" % domain  # regional specific stuff
        elif target_server == "whois.verisign-grs.com":
            request_domain = "=%s" % domain  # Avoid partial matches
        else:
            request_domain = domain

        self.parent.check_point()
        response = self.__whois_request(request_domain, target_server)

        if response is None and self.founded_data is not None:
            return self.founded_data
        if target_server == "whois.verisign-grs.com" and response is not None:
            # VeriSign is a little... special. As it may return multiple full records and there's
            # no way to do an exact query,
            # we need to actually find the correct record in the list.
            for record in response.split("\n\n"):
                s = "Domain Name: %s" % domain.upper()
                if re.search(s, record):
                    response = record
                    break

        new_list = [response] + previous
        server_list.append(target_server)
        for line in [x.strip() for x in response.splitlines()]:
            match = re.match(
                "(refer|whois server|referral url|registrar whois|Registrar WHOIS Server):\s*([^\s]+\.[^\s]+)", line,
                re.IGNORECASE)
            if match is not None:
                referal_server = match.group(2)
                if referal_server != server and "://" not in referal_server:  # We want to ignore anything non-WHOIS
                    # (eg. HTTP) for now.
                    # save before founded data
                    self.founded_data = new_list
                    #         Referal to another WHOIS server...
                    self.parent.check_point()
                    return self.domain_whois(domain, referal_server, new_list, server_list=server_list)
        return new_list

    def get_whois_with_zone(self, domain, server="", previous=None, is_ascii=True,
                            server_list=None):

        """
         find domain zone records if available, like [`A`, `AAAA`, `MX`, `NS`, `TXT`, `SOA`]
        :param domain: domain name (eg: google.com)
        :param server: lookup server
        :param previous: previous server processed for find information `internal use`
        :param is_ascii: set to False if non-unicode domain (eg:دامنه.ایران)
        :param server_list: list of processed servers `internal use`
        :return: a tuple contains whois and zone
        """
        self.parent.check_point()
        self.update_progressbar(" set request to whois server ",
                                20)
        whois = self.domain_whois(domain, server, previous, is_ascii, server_list)
        self.update_progressbar(" get zone of domain and parsing data ",
                                50)
        zone = self.__zone_request(domain)
        self.parent.check_point()
        self.update_progressbar("parsing result",
                                80)
        return whois, zone

    def ip_whois(self, ip_or_domain):
        """
        use `RIPE` rest api for find ip address information
        :param ip_or_domain: determine ip or whois
        :return: response whois of ip or domain
        """
        try:
            self.parent.check_point()
            entery = socket.gethostbyname(self.__domain_validate(ip_or_domain))
        except ValueError:
            entery = ip_or_domain

        request = requests.get('http://rest.db.ripe.net/search.json', params={
            'query-string': entery,
        })
        return request.text

    def __zone_request(self, domain):
        """

        :param domain:determine domain
        :return: result of zone request of doamin
        """
        domain = self.__domain_validate(domain)
        data = []
        try:
            for qtype in 'A', 'AAAA', 'MX', 'NS', 'TXT', 'SOA':
                answer = dns.resolver.query(domain, qtype, raise_on_no_answer=False)
                if answer.rrset is not None:
                    data.append(str(answer.rrset))
        except:
            return []
        return data

    def __get_root_server(self, domain):
        """

        :param domain: determine domain
        :return: result of brequesting root whois server
        """
        data = self.__whois_request(domain, "whois.iana.org")
        for line in [x.strip() for x in data.splitlines()]:
            match = re.match("refer:\s*([^\s]+)", line)
            if match is None:
                continue
            return match.group(1)
        return False

    def __whois_request(self, domain, server, port=43):
        """

        :param domain: determine domain target
        :param server: determine server for whois request
        :param port: determine port of server for whois request
        :return: whois response data for domain
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((server, port))
            sock.settimeout(50)
            domain = ("%s\r\n" % domain).encode("utf-8")
            sock.send(domain)
            buff = b""

            while True:
                self.parent.check_point()
                data = sock.recv(1024)
                if len(data) == 0:
                    break
                buff += data
            b = buff.decode("utf-8")
            return b
        except socket.error as e:
            if self.founded_data is None:
                raise e
            else:
                return None

    def __domain_validate(self, domain):
        """
        :param domain: determine domain input
        :return: normalized and validate doamin if domain input is valid
        """
        valid_domain = None
        try:
            valid_domain = re.search(r'(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,6}', domain)
        except TypeError:
            pass
        if valid_domain is None:
            raise InvalidInputError("domain format is not valid!")
        domain = valid_domain.group(0)
        if not re.match(r'http(s?):', domain):
            domain = 'http://' + domain
        domain = urlparse(domain).netloc
        if domain.startswith("www"):
            domain = domain.replace("www.", "")
        return domain

    def reverse_ip_lookup(self, host, api_key, domain_count_flag, max_results):
        """"
        this functions takes a domain or IP address as host parameter and quickly shows all other domains hosted
         from the same server

        :param host: the domain or IP address to find all hosted domains on type as string
        :param api_key: api key of this API type as string
        :param max_results: maximum number of results that its default value is 200 type as Integer
        :param domain_count_flag: just return number of domains
        :returns if output_type is json, return {'query': {'tool': 'reverseip_PRO', 'host': ''},
            'response': {'domain_count': '', 'domains': [{'name': '', 'last_resolved': ''}] }}
        :raises if got request status code except 200, return {'error': 'Bad request'}
        :raises if got exception {'error': 'error message'}
        """
        page = 1
        domains = []
        self.update_progressbar('setting request to server', 20)
        if domain_count_flag:
            payload = {'host': host, 'apikey': api_key, 'output': 'json', 'page': page}
            try:
                self.parent.check_point()
                r = Qhttp.get(url=Whois.Reverse_IP_Lookup_url, url_query=payload)
                if r.status_code == 200:
                    result = r.json()
                    response = result.get('response')
                    if response:
                        domain_count = response.get('domain_count')
                        if domain_count:
                            return {'results': [{'domain_count': int(domain_count), 'type': 0}]}
                        else:
                            raise NetworkError(r.text)
                else:
                    raise BadRequest(r.status_code)
            except Exception as e:
                raise NetworkError(e.__str__())

        while int(max_results) > len(domains):
            payload = {'host': host, 'apikey': api_key, 'output': 'json', 'page': page}
            try:
                self.parent.check_point()
                r = Qhttp.get(url=Whois.Reverse_IP_Lookup_url, url_query=payload)
                if r.status_code == 200:
                    result = r.json()
                    response = result.get('response')
                    if response:
                        domain_count = response.get('domain_count')
                        domains_results = response.get('domains')
                        if domains_results and domain_count:
                            domains.extend(domains_results)
                            if int(domain_count) <= len(domains):
                                # reaching end of result number
                                break
                        else:
                            # continue to next request if something bad happening
                            continue
                    else:
                        raise NetworkError(r.text)
                else:
                    raise BadRequest(r.status_code)

            except Exception as e:
                raise NetworkError(e.__str__())
            page += 1
        self.update_progressbar('parsing_results',80)
        parse_result = {'results': []}
        for item in domains:
            if len(parse_result['results']) >= int(max_results):
                break
            try:
                parse_result['results'].append(
                    {'data': item['name'], 'type': 12,
                     'properties': [{'type': 0, 'last_resolved': item['last_resolved']}]})
            except Exception:
                continue
        if len(parse_result['results']) == 0:
            raise ResultNotFoundError
        return parse_result
