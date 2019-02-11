import time

import os, logging

import sys
import traceback

from . import Config
from .dryscrape import Session, xvfb
from .dryscrape.driver.webkit import Driver
from .Node import Node


class Hrobot(object):
    def __init__(self, cookie_path='.', base_url=None):
        self.xvfb_obj = None
        self.killed = False
        if not cookie_path:
            cookie_path = '.' # may be user set path dynamically and set '', in this case, python try to make file in root directory and get permission denied, we re assign (dot[.] => point to this directory) to prevent previous error
        try:
            self.browser = Session(driver=Driver(), base_url=base_url)
        except Exception:
            self.xvfb_obj = xvfb.get_xvfb()
            self.xvfb_obj.start()
            self.browser = Session(driver=Driver(), base_url=base_url)
        self.set_timeout(60)
        self.__session_id = int(round(time.time() * 1000))
        self.__cookie_path = cookie_path
        if os.path.exists(Config.log_file):
            file_age = os.path.getsize(Config.log_file)
            if file_age > Config.log_file_size_limit * 1048576:
                os.remove(Config.log_file)

        if not Config.debug:
            logging.basicConfig(filename=Config.log_file)
            sys.excepthook = self.__exception_handler

    def __exception_handler(self, *exc_info):
        logging.exception("".join(traceback.format_exception(*exc_info)))

    def __return(self, node):
        """ Return node as callable Node class object or None"""
        if node is not None:
            return Node(node)
        return None

    def __returns(self, nodes):
        """ Return List of All nodes as callable Node class object or None"""
        if nodes is not None:
            node = []
            [node.append(Node(x)) for x in nodes]
            return node
        return None

    def cleanup(self):
        if not self.killed:
            self.browser.conn.server_instance.kill()
            self.killed = True

    def get_session_unique_id(self):
        """ return unique number generated for this session """
        return self.__session_id

    def get_document(self):
        """ Parses the HTML returned by body and returns it as an lxml.html document.
        If the driver supports live DOM manipulation (like webkit_server does),
        changes performed on the returned document will not take effect. """
        return self.browser.document()

    def get_body(self):
        """ Return the current DOM as HTML. """
        return self.browser.body()

    def clear_cookies(self):
        """ Deletes all cookies. """
        self.browser.clear_cookies()

    def get_cookies(self):
        """ Return a list of all cookies in cookie string format. """
        return self.browser.cookies()

    def set_cookie(self, cookie):
        """ Sets a cookie for future requests (must be in correct cookie string format). """
        self.browser.set_cookie(cookie)

    def eval_script(self, script):
        """ Evaluates a piece of Javascript in the context of the current page and returns its value. """
        return self.browser.eval_script(script)

    def exec_script(self, script):
        """ Executes a piece of Javascript in the context of the current page. """
        self.browser.exec_script(script)

    def set_timeout(self, timeout):
        """ Set timeout for every webkit-server command. """
        self.browser.set_timeout(timeout)

    def get_timeout(self):
        """ Return timeout for every webkit-server command """
        return self.browser.get_timeout()

    def set_header(self, key, value):
        """ Sets a HTTP header for future requests. """
        self.browser.set_header(key, value)

    def get_headers(self):
        """ Returns a list of the last HTTP response headers. Header keys are normalized to capitalized form,
        as in User-Agent. """
        return self.browser.headers()

    def block_url(self, url):

        self.browser.block_url(url)

    def allow_url(self, url):

        self.browser.allow_url(url)

    def set_unknown_url_mode(self, mode):
        """ mode [block, warn] """
        self.browser.set_unknown_url_mode(mode)

    def set_url_black_list(self, urls):
        """ set urls to black list (old urls added clear every time you call this method) """
        self.browser.set_url_black_list(urls)

    def set_html(self, html, url=None):
        """ Sets custom HTML in our Webkit session and allows to specify a fake URL.
        Scripts and CSS is dynamically fetched as if the HTML had been loaded from the given URL. """
        self.browser.set_html(html, url)

    def save_as_png(self, path, width=1024, height=1024):
        """ Renders the current page to a PNG file (viewport size in pixels). """
        self.browser.render(path, width, height)

    def clear_session(self):
        """ Resets the current web session. """
        self.browser.reset()

    def set_viewport_size(self, width, height):
        """ Sets the viewport size. """
        self.browser.set_viewport_size(width, height)

    def get_source(self):
        """ Return the source of the page as it was originally served by the web server. """
        return self.browser.source()

    def status_code(self):
        """ Return the numeric HTTP status of the last response. """
        return self.browser.status_code()

    def get_url(self):
        """ Returns the current location. """
        return self.browser.url()

    def go_to(self, url=''):
        """ Goes to a given URL. """
        self.browser.visit(url)

    def go_back(self):
        self.browser.go_back()

    def set_skip_image_loading(self, value):
        """ Specifies whether images are automatically loaded in web pages. This is disabled by default."""
        # self.browser.set_attribute('auto_load_images', value)
        value = 'true' if value else 'false'
        self.browser.set_skip_image_loading(value)

    def set_ignore_http_exception(self, value):
        """ set ignore http exception raise (default to False) """
        self.browser.set_ignore_http_exception(value)

    def dns_prefetch_enabled(self, value):
        """ Specifies whether Qt WebKit will try to pre-fetch DNS entries to speed up browsing.
         This only works as a global attribute. This is disabled by default."""
        self.browser.set_attribute('dns_prefetch_enabled', value)

    def plugins_enabled(self, value):
        """ Enables or disables plugins in Web pages (e.g. using NPAPI).
        Qt plugins with a mimetype such as "application/x-qt-plugin" are not affected by this setting.
        This is disabled by default."""
        self.browser.set_attribute('plugins_enabled', value)

    def private_browsing_enabled(self, value):
        """ Private browsing prevents WebKit from recording visited pages in the history and storing web page icons.
        This is disabled by default."""
        self.browser.set_attribute('private_browsing_enabled', value)

    def javascript_can_open_windows(self, value):
        """ Specifies whether JavaScript programs can open new windows. This is disabled by default."""
        self.browser.set_attribute('javascript_can_open_windows', value)

    def javascript_can_access_clipboard(self, value):
        """ Specifies whether JavaScript programs can read or write to the clipboard. This is disabled by default."""
        self.browser.set_attribute('javascript_can_access_clipboard', value)

    def offline_storage_database_enabled(self, value):
        """ Specifies whether support for the HTML 5 offline storage feature is enabled or not.
        This is disabled by default."""
        self.browser.set_attribute('offline_storage_database_enabled', value)

    def offline_web_application_cache_enabled(self, value):
        """ Specifies whether support for the HTML 5 web application cache feature is enabled or not.
        This is disabled by default."""
        self.browser.set_attribute('offline_web_application_cache_enabled', value)

    def local_storage_enabled(self, value):
        """ Specifies whether support for the HTML 5 local storage feature is enabled or not.
        This is disabled by default"""
        self.browser.set_attribute('local_storage_enabled', value)

    def local_content_can_access_remote_urls(self, value):
        """ Specifies whether locally loaded documents are allowed to access remote urls.
        This is disabled by default. """
        self.browser.set_attribute('local_content_can_access_remote_urls', value)

    def local_content_can_access_file_urls(self, value):
        """ Specifies whether locally loaded documents are allowed to access other local urls.
        This is enabled by default."""
        self.browser.set_attribute('local_content_can_access_file_urls', value)

    def site_specific_quirks_enabled(self, value):
        """ This setting enables WebKit's workaround for broken sites. It is enabled by default."""
        self.browser.set_attribute('site_specific_quirks_enabled', value)

    def find_by_css(self, selector):
        """ Return the first node matching the given CSSv3 expression or None. """
        return self.__return(self.browser.at_css(selector))

    def find_by_xpath(self, xpath):
        """ Return the first node matching the given XPath 2.0 expression or None. """
        return self.__return(self.browser.at_xpath(xpath))

    def find_all_by_css(self, selector):
        """ Return all nodes matching the given CSSv3 expression. """
        return self.__returns(self.browser.css(selector))

    def find_all_by_xpath(self, xpath):
        """ Return all nodes matching the given XPath 2.0 expression. """
        return self.__returns(self.browser.xpath(xpath))

    # adding new action#########################

    def find_by_following_sibling(self, tag, sibling):
        """ Return first sibling node after the current node """
        return self.find_by_xpath("//%s/following-sibling::%s" % (tag, sibling))

    def find_all_by_following_sibling(self, tag, sibling):
        """ Return all sibling nodes after the current node """
        return self.find_all_by_xpath("//%s/following-sibling::%s" % (tag, sibling))

    def find_by_preceding_sibling(self, tag, sibling):
        """ Return first sibling node before the current node """
        return self.find_by_xpath("//%s/preceding-sibling::%s" % (tag, sibling))

    def find_all_by_preceding_sibling(self, tag, sibling):
        """ Return all sibling nodes before the current node """
        return self.find_all_by_xpath("//%s/preceding-sibling::%s" % (tag, sibling))

    def find_element_has_attribute(self, tag, attr):
        """ Return the first node has attr in its attribute or none """
        return self.find_by_xpath("//%s[@%s]" % (tag, attr))

    def find_elements_has_attribute(self, tag, attr):
        """ Return all nodes has attr in their attribute or none """
        return self.find_all_by_xpath("//%s[@%s]" % (tag, attr))

    def find_elements_has_any_attribute(self, tag):
        """ Return all nodes that has any attribute or none"""
        return self.find_by_xpath("//%s[@*]" % tag)

    def find_elements_has_not_attribute(self, tag):
        """ Return all nodes that has not any attribute or none"""
        return self.find_by_xpath("//%s[not(@*)]" % tag)

    def find_by_attribute_value(self, tag, attr, value, normalize_space=True):
        """ Return first node has attr in its attribute and the value of attr is equal to value."""
        if normalize_space:
            return self.find_by_xpath("//%s[normalize-space(@%s = %s)]" % (tag, attr, value))
        else:
            return self.find_by_xpath("//%s[@%s = %s]" % (tag, attr, value))

    def find_all_by_attribute_value(self, tag, attr, value, normalize_space=True):
        """ Return all nodes has attr in their attribute and the value of attr is equal to value."""
        if normalize_space:
            return self.find_all_by_xpath("//%s[normalize-space(@%s = %s)]" % (tag, attr, value))
        else:
            return self.find_all_by_xpath("//%s[@%s = %s]" % (tag, attr, value))

    def find_by_children_number(self, tag, children_number):
        """ Return first node that number of its children is equal to children_number  """
        return self.find_all_by_xpath("//*[count(%s)= %s]" % (tag, children_number))

    def find_all_by_children_number(self, children_number):
        """ Return all nodes that number of their children is equal to children_number  """
        return self.find_all_by_xpath("//*[count(*)= %s]" % children_number)

    def find_by_name(self, tag_name):
        """ Return node that name of it is equal to tag_name """
        return self.find_all_by_xpath("//*[name()=%s]" % tag_name)

    def find_by_name_starts_with(self, letter):
        """ Return node that name of it starts with to letter """
        return self.find_all_by_xpath("//*[starts-with(name(), %s)]" % letter)

    def find_by_name_contains(self, letter):
        """ Return node that name of it contains letter """
        return self.find_all_by_xpath("//*[contains(name(),%s)]" % letter)

    # this finds excludes any descendants and  attribute nodes and namespace nodes.
    def find_by_following(self, node):
        """ Return nodes that exist in following of node """
        return self.find_all_by_xpath("//%s/following::*" % node)

    # this finds excludes any descendants and  attribute nodes and namespace nodes.
    def find_by_preceding(self, node):
        """ Return nodes that exist in preceding of node """
        return self.find_all_by_xpath("//%s/preceding::*" % node)

    def find_element_descendant(self, tag, child_tag='*'):
        return self.find_by_xpath("%s/descendant::%s" % (tag, child_tag))

    def find_elements_descendant(self, tag, child_tag='*'):
        return self.find_all_by_xpath("%s/descendant::%s" % (tag, child_tag))

    def find_all_elements_descendant(self, tag):
        return self.find_all_by_xpath("//%s/descendant::*" % tag)

        ##################################################

    def find_by_contain_text(self, tag, text):
        """ Return all nodes that contains text in their text value"""
        return self.find_by_xpath("//%s[contains(text(), '%s')]" %(tag, text))

    def save_cookies_to_file(self, list):
        text_file = open(self.__cookie_path + "/cookies.txt", "w+")
        for item in list:
            text_file.write("%s\n" % item)

    def load_cookies_from_file(self):
        path = self.__cookie_path + "/cookies.txt"
        if not os.path.exists(path):
            open(path, 'w').close()
        with open(path) as f:
            content = f.readlines()
        content = [x.strip() for x in content]
        return content

    def wait(self, ms):
        """ wait without sleep(freeze main thread) in milliseconds """
        self.exec_script("iwait(%d)" % ms)

    def wait_until_css(self, selector, timeout=30):
        node = self.find_by_css(selector)
        elapsed = 0
        while not node:
            if elapsed > timeout:
                return None
            self.wait(1000)
            elapsed += 1
            node = self.find_by_css(selector)
        return node

    def wait_until_xpath(self, xpath, timeout=30):
        node = self.find_by_xpath(xpath)
        elapsed = 0
        while not node:
            if elapsed > timeout:
                return None
            self.wait(1000)
            elapsed += 1
            node = self.find_by_xpath(xpath)
        return node

    def __del__(self):
        self.cleanup()
