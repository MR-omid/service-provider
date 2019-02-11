import hashlib
import os
import urllib
import uuid
from urllib.parse import urlparse
from components.utils import ApiLogging
from extensions.hrobot.v_1_0.Hrobot import Hrobot
from vendor import urltools
from vendor.custom_exception import ResultNotFoundError
from vendor.custom_exception import CrawlLimit


class Processor(object):
    def __init__(self, first_url, limit, base_url, dep, parent_instance, storage, mode='simple', has_next_dep=True):
        """
        :param limit:determine limit of saved page
        :param first_url:determine base url of first page
        :param base_url:determine base url
        :param dep:determine depth of crawl
        :param parent_instance:show instance of obligatory class
        :param storage:show storage path
        :param has_next_dep:boolean flag to determine status of having next depth or not
        :param mode:a flag to choose state of crawling from the list of [simple,advanced]
        """
        self.first_url = first_url
        self.limit = limit
        self.xpaths = []
        self.urls = []
        self.has_next_dep = has_next_dep
        self.dep = dep
        self.parent_instance = parent_instance
        self.storage = storage
        self.robot = Hrobot(cookie_path=os.path.dirname(__file__) + '/test_cookie', base_url=base_url)
        self.robot.set_skip_image_loading(True)
        # add google ads to black list, this site generate bad request exception
        self.robot.block_url("googleads.g.doubleclick.net")
        self.base_url = None
        self.domain_hash = None
        self.mode = mode
        self.exceed_limit = False
        self.not_saved_url = []
        self.files_url = []

    def __reload(self):
        self.robot.go_to(self.base_url)

    def __invalid_page(self):
        return len(self.robot.find_by_css('body').get_text()) < 30

    def __url_changed(self):
        return not urltools.compare(self.base_url, self.robot.get_url())

    def __find_clickables(self):
        if self.mode == "advance":
            css_selector_list = ['a', 'div']
        else:
            css_selector_list = ['a']
        for selector in css_selector_list:
            nodes = self.robot.find_all_by_css(selector)
            self.__save_xpath(nodes)

    def __save_xpath(self, nodes):
        """

        :param nodes: show list of nodes
        :return: list of xpath for input nodes
        """
        for node in nodes:
            xpath = node.get_xpath()
            if xpath not in self.xpaths:
                self.xpaths.append(xpath)

    def __compare_attrs(self, old_attrs, new_attrs):
        """

        :param old_attrs: determine first attribute
        :param new_attrs: determine second attribute
        :return: result of comparing two attribute in the form of boolean
        """
        attrs = ['href', 'id', 'class', 'part_of_text']
        for attr in attrs:
            if old_attrs.get(attr) != new_attrs.get(attr):
                return False
        return True

    def __try_find_node(self, xpath, timeout=5):
        """

        :param xpath:determine xpath of one node
        :param timeout: show timeout
        :return: node related to input xpath
        """
        timeout = timeout if timeout > 0 else 1
        timeout = timeout / 2
        node = self.robot.wait_until_xpath(xpath, timeout)
        if not node:
            self.__reload()
            node = self.robot.wait_until_xpath(xpath, timeout)
            return node
        return node

    def __find_url(self):
        for xpath in self.xpaths:
            self.parent_instance.check_point()
            try:
                node = self.__try_find_node(xpath, 2)
                if node:
                    xpath_black_list = self.parent_instance.get_xpath_blacklist()
                    xpath_hash = hashlib.md5(xpath.encode('utf-8')).hexdigest()
                    black_list_group = xpath_black_list.get(self.domain_hash, None)
                    node.set_attr('target', '_self')
                    attrs = {'href': node.get_attr('href'), 'id': node.get_attr('id'), 'class': node.get_attr('class'),
                             'part_of_text': node.get_text()[:20]}
                    if black_list_group and xpath_hash in black_list_group and self.__compare_attrs(attrs,
                                                                                                    black_list_group[
                                                                                                        xpath_hash]):
                        continue
                    else:
                        self.parent_instance.add_xpath_blacklist(xpath_hash, attrs, self.domain_hash)
                        self.robot.set_unknown_url_mode('block')
                        node.eval_script(
                            'node.click()')  # FIXME: may be need to use physical pointer and js click as redundancy
                        self.robot.set_unknown_url_mode('warn')
                        url = urltools.normalize(urllib.parse.unquote(self.robot.get_url()))
                        if self.__url_changed():
                            # new section faces invalid page, include: 404, not found, access denied
                            if self.__invalid_page():
                                self.not_saved_url.append(url)
                                self.__go_back()
                                continue

                            if url not in self.urls:
                                if self.first_url is None:
                                    self.urls.append(url)
                                else:  # in case of just crawling pages from base url
                                    data = urlparse(url)
                                    base_current_url = data.scheme + '://' + data.netloc
                                    if urltools.compare(self.first_url, base_current_url):
                                        self.urls.append(url)
                        else:
                            pass  # FIXME: if click action not change url, maybe ajax content loading happen,

                        if self.__url_changed() or self.__invalid_page():
                            self.__go_back()

            except Exception as msg:
                pass  # cant find url of this node, because of timeout ro some similar error

    def __go_back(self):
        self.robot.go_back()
        if self.__url_changed() or self.__invalid_page():
            self.__reload()  # reload page for fix url_replace with javascript
            # (url_replace clear history and go_back will be failed)

    def __save_html(self):
        base_path = self.storage[0]
        relative_path = self.storage[1]
        full_path = base_path + '/' + relative_path + '/'
        file = str(uuid.uuid4()) + '.html'
        os.makedirs(full_path, exist_ok=True)
        self.parent_instance.add_html_list({
            'type': 9,
            'data': base_path + '/' + relative_path + '/'
                    + file,
            'properties': [{'url': self.base_url, 'type': 1}],
            'ref': {
                'task': 'crawl',

                'depth': self.dep
            }
        }
        )
        html = open(full_path + '/' + file, 'w+')
        html.write(self.robot.get_body())
        html.close()
        if len(self.parent_instance.html_list) > self.limit:
            self.exceed_limit = True
            raise CrawlLimit('reach crawler limit: ', self.limit)

    def get_urls(self):
        try:
            # todo: if base_url is file_url, append that to file_url list, don't save as html
            # if self.base_url.endswith('file format'):
            #   file_urls.append(self.base_urls)
            # else:
            self.robot.go_to()
            self.base_url = urltools.normalize(urllib.parse.unquote(
                self.robot.get_url()))  # assign base_url here, because actual url may not
            #  equal to url requested by user. for example: redirect to login page
            if self.has_next_dep:
                domain_slit = urltools.parse(self.base_url)
                domain = domain_slit.domain + '.' + domain_slit.tld
                self.domain_hash = hashlib.md5(domain.encode('utf-8')).hexdigest()
                self.__find_clickables()
                self.__save_html()
                self.__find_url()
            else:
                self.__save_html()
        except Exception:
            # can not save this url to html, so add this url to crashed url
            self.not_saved_url.append(self.base_url)
        finally:
            self.robot.cleanup()
            if self.exceed_limit:
                raise CrawlLimit('reach crawler limit: ', self.limit)
            if not self.parent_instance.html_list:
                raise ResultNotFoundError
            return self.urls
