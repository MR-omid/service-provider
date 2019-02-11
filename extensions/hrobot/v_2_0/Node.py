import base64
import os

from PyQt5.QtCore import QObject, pyqtSignal, QEventLoop, QTimer

from extensions.hrobot.v_2_0.Utils import Utils


class Node(QObject):
    asyncFinished = pyqtSignal()

    def __init__(self, parent, page, node_id):
        super().__init__()
        self.node_id = node_id
        self.__page = page
        self.__parent = parent
        self.__async_result = None

    def __node(self, node_id):
        return Node(self.__parent, self.__page, node_id)

    def __async_callback(self, result):
        self.__async_result = result
        self.asyncFinished.emit()

    def __run_js(self, script):
        loop = QEventLoop()
        self.asyncFinished.connect(loop.quit)
        self.__page.runJavaScript(script, self.__async_callback)
        loop.exec()
        return self.__async_result

    def click(self):
        """ Alias for left_click. """
        self.left_click()

    def left_click(self):
        """ Left clicks the current node, then waits for the page to fully load. """
        loop = QEventLoop()
        self.__parent._qt_invocation.async_js_finished.connect(loop.quit)
        self.__run_js(Utils.qt_js_prepare('Qt.click("{0}")').format(self.node_id))
        loop.exec()
        print('after click')

    def get_text(self) -> str:
        """ Returns the inner text (not HTML). """
        return self.__run_js(Utils.qt_js_prepare('Qt.text("{0}")').format(self.node_id))

    def enter(self):
        """ press enter on the node|element """
        self.__run_js(Utils.qt_js_prepare('Qt.enter("{0}")').format(self.node_id))

        print('after enter')

    def get_position(self) -> dict:
        """ Return the current node rect position """
        return self.__run_js(Utils.qt_js_prepare('Qt.position("{0}")').format(self.node_id))

    def get_center_position(self) -> dict:
        """ Return the current node center {x,y} position """
        return self.__run_js(Utils.qt_js_prepare('Qt.centerPosition("{0}")'.format(self.node_id)))

    def eval_script(self, script):
        """ Evaluates a piece of Javascript in the context of the current page and returns its value. """
        return self.__run_js(self.__build_node_script(script))

    def exec_script(self, script):
        """ Executes a piece of Javascript in the context of the current page. """
        self.__run_js(self.__build_node_script(script))

    def __build_node_script(self, script):
        return 'var node = Qt.getNode("{0}"); {1}'.format(self.node_id, script)

    def focus(self):
        """ Puts the focus onto the current node, then waits for the page to fully load. """
        self.__run_js(Utils.qt_js_prepare('Qt.focus("{0}")'.format(self.node_id)))

    def is_attached(self):
        """ Checks whether the current node is actually existing on the currently active web page. """
        return self.__run_js(Utils.qt_js_prepare('Qt.isAttached("{0}")'.format(self.node_id)))

    def is_checked(self):
        """ is the checked attribute set for this node? """
        return self.get_attribute('checked')

    def is_disabled(self):
        """ is the disabled attribute set for this node? """
        return self.get_attribute('disabled')

    def is_multi_select(self):
        """ is this node a multi-select? """
        return self.tag_name() == "select" and self.get_attribute("multiple")

    def is_selected(self):
        """ is the selected attribute set for this node? """
        return self.get_attribute('selected')

    def is_visible(self):
        """ Checks whether the current node is visible. """
        return self.__run_js(Utils.qt_js_prepare('Qt.visible("{0}")'.format(self.node_id)))

    def get_xpath(self):
        """ Returns an XPath expression that uniquely identifies the current node. """
        return self.__run_js(Utils.qt_js_prepare('Qt.path("{0}")'.format(self.node_id)))

    def select_option(self):
        """ Selects an option node. """
        self.__run_js(Utils.qt_js_prepare('Qt.selectOption("{0}")'.format(self.node_id)))

    def set_value(self, value):
        """ Sets the node content to the given value (e.g. for input fields). """
        self.__run_js(Utils.qt_js_prepare('Qt.set("{0}","{1}")'.format(self.node_id, value)))

    def set_attribute(self, attr, value):
        """ Sets the value of an attribute. """
        self.exec_script('node.{0} = "{1}"'.format(attr, value))

    def get_attribute(self, attr):
        """ Returns the value of an attribute. """
        return self.eval_script('node.getAttribute("{0}")'.format(attr))

    def submit(self):
        """ Submits a form node, then waits for the page to completely load. """
        self.__run_js(Utils.qt_js_prepare('Qt.submit("{0}")'.format(self.node_id)))

    def get_tag_name(self):
        """ Returns the tag name of the current node. """
        return self.__run_js(Utils.qt_js_prepare('Qt.tagName("{0}")'.format(self.node_id)))

    def unselect_options(self):
        """ Unselects an option node (only possible within a multi-select). """
        self.__run_js(Utils.qt_js_prepare('Qt.unselectOption("{0}")'.format(self.node_id)))

    def get_value(self):
        """ Return the node`s value. """
        return self.__run_js(Utils.qt_js_prepare('Qt.value("{0}")'.format(self.node_id)))

    def find_by_css(self, selector):
        """ Return the first node matching the given CSSv3 expression within current node or None. """
        nodes = self.find_all_by_css(selector)
        return None if not nodes else nodes[0]

    def find_by_xpath(self, xpath):
        """ Return the first node matching the given XPath 2.0 expression within current node or None. """
        nodes = self.find_all_by_xpath(xpath)
        return None if not nodes else nodes[0]

    def find_all_by_css(self, selector):
        """ Finds another node by a CSS selector relative to the current node. """
        try:
            return [self.__node(node_id)
                    for node_id in self.__run_js(
                    Utils.qt_js_prepare('Qt.findCssRelativeTo(Qt.getNode({0}), "{1}")'.format(self.node_id,
                                                                                              Utils.normalize_quotes(
                                                                                                  selector)))).split(",")
                    if node_id]
        except AttributeError:
            return None

    def find_all_by_xpath(self, xpath):
        """ Finds another node by XPath originating at the current node. """
        try:
            return [self.__node(node_id)
                    for node_id in self.__run_js(
                    Utils.qt_js_prepare('Qt.findXpathRelativeTo(Qt.getNode({0}), "{1}")'.format(self.node_id,
                                                                                                Utils.normalize_quotes(
                                                                                                    xpath)))).split(",")
                    if node_id]
        except AttributeError:
            return None

    def get_children(self):
        """ Return the child of nodes. """
        return self.find_all_by_xpath('*')

    def get_form(self):
        """ Return the form wherein this node is contained or None. """
        return self.find_by_xpath("ancestor::form")

    def get_parent(self):
        """ Return the parent node. """
        return self.find_by_xpath('..')

    def save_image(self, path, name='untitled'):
        b64 = self.__run_js(Utils.qt_js_prepare('Qt.img2b64("{0}")'.format(self.node_id)))
        if b64 is not None and b64.startswith('data:'):
            b64 = b64.split(',')
            if len(b64) > 1:
                img_b64 = b64[-1]
                if not os.path.exists(path):
                    os.mkdir(path)
                f = open(path + '/' + name + '.png', 'wb')
                f.write(base64.b64decode(img_b64))
                f.close()