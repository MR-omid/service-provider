import os
from datetime import date

from modules.base_module import BaseModule
from vendor.custom_exception import InvalidInputError
from modules.crawler.v_1_0.crawl import Processor
import validators
from urllib.parse import urlparse


class Module(BaseModule):
    # define expected link number per page
    mean_link_per_page = 100

    def __init__(self, task_model):
        super().__init__(task_model)
        self.xpath_black_list = {}
        self.url_black_list = []
        self.html_list = []
        self.all_founded_urls = []
        self.storage = [os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
                        'modules/crawler/storage/' + str(date.today().isoformat())]
        self.remaining = 0
        self.all = 0
        self.mode = None

    def update_progressbar(self, message, percent):
        self.progress = {'state': message, 'percent': percent}

    # checking parametr then start crawling
    def run(self):
        parse_data = self.params.get('data')
        if parse_data is None:
            raise InvalidInputError(' missing data keyword')
        # if input data has not method_id keyword raise exception
        if 'method_id' not in parse_data.keys():
            raise InvalidInputError('missing method_id keyword')
        if parse_data['method_id'] == 1:
            if 'url' not in parse_data.keys():
                raise InvalidInputError(' missing url keyword')

            url = parse_data['url']
            if not (validators.url(url)):
                raise InvalidInputError('url not valid')

            # get dep from data
            if 'depth' in parse_data.keys():
                dep = parse_data['depth']
            else:
                dep = 1

            # get link_limit from data
            if 'link_limit' in parse_data.keys():
                if str(parse_data['link_limit']).isdigit():
                    link_limit = int(parse_data['link_limit'])
                else:
                    link_limit = 2000
            else:
                link_limit = 2000

            # get base_url_constraint from data
            if 'base_url_constraint' in parse_data.keys():
                if parse_data['base_url_constraint'] in [True, 'True', 1, 'true', '1']:
                    data = urlparse(url)
                    base_url = data.scheme + '://' + data.netloc
                else:
                    base_url = None
            else:
                base_url = None
            self.crawl(base_url, link_limit, [url], dep, dep)
        else:
            raise InvalidInputError('invalid method_id')

    def crawl(self, base_url, link_limit, urls, total_dep, dep=0):
        if dep >= 0:

            dep -= 1
            for url in urls:
                self.check_point()
                # add url to black list, for preventing crawling same page
                if url not in self.url_black_list:
                    self.url_black_list.append(url)
                    #  crawl the url in urls
                    np = Processor(base_url, link_limit, url, dep + 1, self, self.storage, self.mode, (dep >= 0))
                    # get new urls from the present page
                    np_urls = np.get_urls()
                    if np_urls:
                        # if there is new url, process them
                        self.remaining = len(np_urls)
                        self.all_founded_urls.append({'page': url, 'urls': np_urls})
                        self.all += (len(np_urls) + 1)
                        try:
                            self.update_progressbar(
                                'all_saved_html_file: ' + str(len(self.html_list))
                                + ' ,remaining_url_in_depth: ' + str(self.remaining) + ' ,current_depth: ' + str(
                                    total_dep-(dep+1)),
                                int(100 * (len(self.html_list) / self.all)))
                        except Exception:
                            pass

                        self.check_point()

                        self.crawl(base_url, link_limit, np_urls, total_dep, dep)
                    else:
                        # if there is no new url, go to next url in present loop
                        self.remaining -= 1
                        try:
                            self.update_progressbar(
                                'all_saved_html_file: ' + str(len(self.html_list))
                                + ' ,remaining_url_in_depth: ' + str(self.remaining) + ' ,current_depth: ' + str(
                                    total_dep - (dep + 1)),
                                int(100 * (len(self.html_list) / self.all)))

                        except Exception:
                            pass

    def add_xpath_blacklist(self, xpath_hash, attrs, domain_hash):
        if self.xpath_black_list.get(domain_hash, None):
            self.xpath_black_list.get(domain_hash).update({xpath_hash: attrs})
        else:
            self.xpath_black_list[domain_hash] = {xpath_hash: attrs}

    def get_xpath_blacklist(self):
        return self.xpath_black_list

    def add_html_list(self, html):
        result = {}
        self.html_list.append(html)
        result['results'] = self.html_list
        self.result = result
