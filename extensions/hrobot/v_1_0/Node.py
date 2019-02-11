
class Node(object):

    def __init__(self, node):
        self.node = node

    def __return(self,node):
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

    def click(self):
        """ Alias for left_click. """
        self.node.click()

    def double_click(self):
        """ Double clicks the current node, then waits for the page to fully load. """
        self.node.double_click()

    def left_click(self):
        """ Left clicks the current node, then waits for the page to fully load. """
        self.node.left_click()

    def right_click(self):
        """ Right clicks the current node, then waits for the page to fully load. """
        self.node.right_click()

    def drag_to(self,dest_node):
        """ drag the current node to dest_node """
        self.node.drag_to(dest_node)

    def eval_script(self,script):
        """ Evaluate arbitrary Javascript with the node variable bound to the current node. """
        return self.node.eval_script(script)

    def exec_script(self,script):
        """ Execute arbitrary Javascript with the node variable bound to the current node. """
        self.node.exec_script(script)

    def focus(self):
        """ Puts the focus onto the current node, then waits for the page to fully load. """
        self.node.focus()

    def get_attr(self,attr):
        """ Returns the value of an attribute. """
        return self.node.get_attr(attr)

    def get_bool_attr(self,attr):
        """ Return the value of a boolean HTML attribute like checked or disabled """
        return self.node.get_bool_attr(attr)

    def hover(self):
        """ overs over the current node, then waits for the page to fully load. """
        self.node.hover()

    def is_attached(self):
        """ Checks whether the current node is actually existing on the currently active web page. """
        return self.node.is_attached()

    def is_checked(self):
        """ is the checked attribute set for this node? """
        return self.node.is_checked()

    def is_disabled(self):
        """ is the disabled attribute set for this node? """
        return self.node.is_disabled()

    def is_multi_select(self):
        """ is this node a multi-select? """
        return self.node.is_multi_select()

    def is_selected(self):
        """ is the selected attribute set for this node? """
        return self.node.is_selected()

    def is_visible(self):
        """ Checks whether the current node is visible. """
        return self.node.is_visible()

    def get_xpath(self):
        """ Returns an XPath expression that uniquely identifies the current node. """
        return self.node.path()

    def select_option(self):
        """ Selects an option node. """
        self.node.select_option()

    def set_value(self,value):
        """ Sets the node content to the given value (e.g. for input fields). """
        self.node.set(value)

    def set_attr(self, name, value):
        """ Sets the value of an attribute. """
        self.node.set_attr(name, value)

    def submit(self):
        """ Submits a form node, then waits for the page to completely load. """
        self.node.submit()

    def get_tag_name(self):
        """ Returns the tag name of the current node. """
        return self.node.tag_name()

    def get_text(self):
        """ Returns the inner text (not HTML). """
        return self.node.text()

    def unselect_options(self):
        """ Unselects an option node (only possible within a multi-select). """
        self.node.unselect_options()

    def get_value(self):
        """ Return the node`s value. """
        return self.node.value()

    def find_by_css(self,selector):
        """ Return the first node matching the given CSSv3 expression within current node or None. """
        return self.__return(self.node.at_css(selector))

    def find_by_xpath(self,xpath):
        """ Return the first node matching the given XPath 2.0 expression within current node or None. """
        return self.__return(self.node.at_xpath(xpath))

    def find_all_by_css(self,selector):
        """ Finds another node by a CSS selector relative to the current node. """
        return self.__returns(self.node.css(selector))

    def find_all_by_xpath(self,xpath):
        """ Finds another node by XPath originating at the current node. """
        return self.__returns(self.node.xpath(xpath))

    def get_children(self):
        """ Return the child of nodes. """
        return self.__returns(self.node.children())

    def get_form(self):
        """ Return the form wherein this node is contained or None. """
        return self.__return(self.node.form())

    def get_parent(self):
        """ Return the parent node. """
        return self.__return(self.node.parent())

    def get_position(self):
        """ Return the current node rect position """
        return self.node.eval_script("node.getBoundingClientRect()")


