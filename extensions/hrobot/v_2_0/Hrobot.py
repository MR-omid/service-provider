import datetime
from typing import Union

from PyQt5.QtCore import QEventLoop, QUrl, QObject, QDir, pyqtSignal, QFile, QIODevice, QTimer, Qt, QPoint, QSize, \
    QRect, QCoreApplication, QDateTime
from PyQt5.QtNetwork import QNetworkCookie
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWebEngineWidgets import QWebEngineProfile, QWebEngineView

from core.constants import BASE_APP_PATH
from extensions.hrobot.v_2_0.Interceptor import Interceptor
from extensions.hrobot.v_2_0.Node import Node
from extensions.hrobot.v_2_0.Page import Page
from extensions.hrobot.v_2_0.QtInvocation import QtInvocation
from extensions.hrobot.v_2_0.Utils import Utils


class Hrobot(QObject):

    asyncFinished = pyqtSignal()

    def __init__(self, base_url=None, private=True, profile_name=None, gui=False):
        super().__init__()
        self.base_url = QUrl(base_url)
        self.__interceptor = Interceptor(self)
        if private:
            self.__profile = QWebEngineProfile()
        elif profile_name:
            self.__profile = QWebEngineProfile(profile_name)
        else:
            raise Exception('please pass `profile_name` in case of `private` flag set to False')
        self.__profile.setRequestInterceptor(self.__interceptor)
        self.__page = Page(self.__profile, None)
        self.__cookie_store = self.__profile.cookieStore()
        self.__cookie_store.cookieAdded.connect(self.__on_cookie_added)
        self.__cookies = []
        self.__async_result = None
        self.__loading = False

        self.__view = QWebEngineView()

        self.__page.setView(self.__view)
        self._qt_invocation = QtInvocation(self.__page)
        self.__channel = QWebChannel(self)
        self.__channel.registerObject("QtInvocation", self._qt_invocation)
        self.__page.setWebChannel(self.__channel)

        self.__page.loadStarted.connect(self.__load_started)
        self.__page.loadFinished.connect(self.__load_finished)
        self.__view.loadProgress.connect(self.__prg)
        self.__page.navigationRequested.connect(self.__navigation_requested)
        # self._qt_invocation.js_navigation_requested.connect(self.__page._js_gap_eventloop)
        self.__page.settings().setAttribute(self.__page.settings().LocalContentCanAccessRemoteUrls, True)
        self.__page.setUrl(QUrl('about:blank'))

        self.__view.setWindowState(Qt.WindowMaximized)
        if gui:
            self.__view.show()

    def __prg(self, p):
        print('progress: ', p)

    def __load_started(self):
        print('load started')

    def __load_finished(self, ok):
        print('load finished', ok)

    def __node(self, node_id):
        return Node(self, self.__page, node_id)

    def __navigation_requested(self):
        print('navvvvvvvvvvvvv', self.__loading)
        if not self.__loading:
            self.__loading = True
            print('navigation event loop started')
            loop = QEventLoop()
            self.__page.loadFinished.connect(loop.quit)
            loop.exec()
            print('navigation event loop ended')
            loop_js = QEventLoop()
            self._qt_invocation.js_ready.connect(loop_js.quit)
            self.__register_js()
            loop_js.exec()
            self.__loading = False
            print('js register event loop ended')

    def __register_js(self):
        channel_file = QFile(":/qtwebchannel/qwebchannel.js")
        if channel_file.open(QIODevice.ReadOnly):
            content = channel_file.readAll()
            channel_file.close()
            print('runjssssssssssssssssssssssssssssssssssssssss 1')
            self.__run_js(content.data().decode())
            print('runjssssssssssssssssssssssssssssssssssssssss 2', BASE_APP_PATH)
        qt_file = QFile('{0}/extensions/hrobot/v_2_0/qt.js'.format(BASE_APP_PATH))
        if qt_file.open(QIODevice.ReadOnly):
            content = qt_file.readAll()
            qt_file.close()
            print('runjssssssssssssssssssssssssssssssssssssssss 3')
            self.__run_js(content.data().decode())
            print('runjssssssssssssssssssssssssssssssssssssssss 4')

    def __async_callback(self, result):
        self.__async_result = result
        self.asyncFinished.emit()
        print('async js emit')

    def __run_js(self, script):
        loop = QEventLoop()
        self.asyncFinished.connect(loop.quit)
        self.__page.runJavaScript(script, self.__async_callback)
        loop.exec()
        print('run js finished')
        return self.__async_result

    def __on_cookie_added(self, cookie):
        print('on add cookie', cookie.toRawForm(1))
        for c in self.__cookies:
            if c.hasSameIdentifier(cookie):
                return
        print('coocke', cookie)
        print('net cookie', QNetworkCookie(cookie))
        self.__cookies.append(QNetworkCookie(cookie))

    def set_cookie(self, cookie):
        self.__cookie_store.setCookie(cookie)

    def __set_browser_attribute(self, attr, value):
        self.__page.settings().setAttribute(attr, value)

    def go_to(self, url: Union[QUrl, str]) -> bool:
        """ Goes to a given URL. """
        url = QUrl(url)
        if self.base_url:
            url = self.base_url.resolved(url)
        loop = QEventLoop()
        self.__page.loadFinished.connect(loop.exit)
        self.__page.load(url)
        return True if loop.exec() else False

    def go_back(self):
        self.__view.back()

    def get_body(self):
        """ Return the current DOM as HTML. """
        loop = QEventLoop()
        self.asyncFinished.connect(loop.quit)
        self.__page.toHtml(self.__async_callback)
        loop.exec()
        return self.__async_result

    def get_cookies(self, as_json=False):
        if as_json:
            return self.__cookie_to_json()
        return self.__cookies

    def __cookie_to_json(self):
        cookies_list_info = []
        for c in self.__cookies:
            c = QNetworkCookie(c)
            data = {"name": bytearray(c.name()).decode(), "domain": c.domain(), "value": bytearray(c.value()).decode(),
                    "path": c.path(), "expirationDate": c.expirationDate().toString(Qt.ISODate), "secure": c.isSecure(),
                    "httponly": c.isHttpOnly()}
            cookies_list_info.append(data)
        return cookies_list_info

    def json_to_cookie(self, json_cookie_list):
        cookies_list_info = []
        for json_cookie in json_cookie_list:
            c = QNetworkCookie()
            print(json_cookie, '** json_cookie')
            for k, v in json_cookie.items():
                if k == 'path':
                    c.setPath(v)
                elif k == 'domain':
                    c.setPath(v)
                elif k == 'expirationDate':
                    print(v, type(v))
                    qdate = QDateTime(2019, 12, 20, 11, 59, 59)
                    print(qdate)
                    c.setExpirationDate(qdate)
                elif k == 'httponly':
                    c.setHttpOnly(v)
                elif k == 'secure':
                    c.setSecure(v)
                elif k == 'value':
                    c.setValue(v.encode())
                elif k == 'name':
                    c.setName(v.encode())
            print('c', c.expirationDate())
            cookies_list_info.append(c)
        return cookies_list_info

    def eval_script(self, script):
        """ Evaluates a piece of Javascript in the context of the current page and returns its value. """
        return self.__run_js(script)

    def exec_script(self, script):
        """ Executes a piece of Javascript in the context of the current page. """
        self.__run_js(script)

    def block_url(self, url):
        raise NotImplementedError

    def allow_url(self, url):
        raise NotImplementedError

    def get_url(self):
        """ Returns the current location. """
        return self.__page.url()

    def reload(self):
        self.go_to(self.current_url())

    def is_private(self):
        return self.__page.profile().isOffTheRecord()

    def set_skip_image_loading(self, value):
        """ Specifies whether images are automatically loaded in web pages. This is disabled by default."""
        # self.browser.set_attribute('auto_load_images', value)
        self.__set_browser_attribute(self.__page.settings().AutoLoadImages, not value)

    def save_as_pdf(self, name):
        loop = QEventLoop()
        self.__page.pdfPrintingFinished.connect(loop.quit)
        self.__page.printToPdf(name)
        loop.exec()

    def scroll_to_end(self, lazy_load=True):
        loop = QEventLoop()
        self._qt_invocation.async_js_finished.connect(loop.quit)
        self.__run_js('Qt.scrollToEnd({0})'.format('true' if lazy_load else 'false'))
        loop.exec()

    def find_by_css(self, selector):
        """ Return the first node matching the given CSSv3 expression or None. """
        nodes = self.find_all_by_css(selector)
        return None if not nodes else nodes[0]

    def find_by_xpath(self, xpath):
        """ Return the first node matching the given XPath 2.0 expression or None. """
        nodes = self.find_all_by_xpath(xpath)
        return None if not nodes else nodes[0]

    def find_all_by_css(self, selector):
        """ Return all nodes matching the given CSSv3 expression. """
        try:
            return [self.__node(node_id)
                    for node_id in self.__run_js(Utils.qt_js_prepare('Qt.findCss("{0}")'.format(Utils.normalize_quotes(selector)))).split(",")
                    if node_id]
        except AttributeError:
            return None

    def find_all_by_xpath(self, xpath):
        """ Return all nodes matching the given XPath 2.0 expression. """
        try:
            return [self.__node(node_id)
                            for node_id in self.__run_js(Utils.qt_js_prepare('Qt.findXpath("{0}")'.format(Utils.normalize_quotes(xpath)))).split(",")
                            if node_id]
        except AttributeError:
            return None

    def wait_until_css(self, selector, timeout=30):
        node = self.find_by_css(selector)
        elapsed = 0
        while not node:
            if elapsed > timeout:
                return None
            Utils.wait(1000)
            elapsed += 1
            node = self.find_by_css(selector)
        return node

    def wait_until_xpath(self, xpath, timeout=30):
        node = self.find_by_xpath(xpath)
        elapsed = 0
        while not node:
            if elapsed > timeout:
                return None
            Utils.wait(1000)
            elapsed += 1
            node = self.find_by_xpath(xpath)
        return node

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

    def find_by_contain_text(self, tag, text):
        """ Return node that contains text in their text value"""
        return self.find_by_xpath("//%s[contains(text(), '%s')]" % (tag, text))

    def find_all_by_contain_text(self, tag, text):
        """ Return all nodes that contains text in their text value"""
        return self.find_all_by_xpath("//%s[contains(text(), '%s')]" % (tag, text))

