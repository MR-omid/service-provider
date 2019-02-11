import os
from components.utils import ApiLogging

nearchars = {
    'a': ['4', 's'],
    'b': ['v', 'n'],
    'c': ['x', 'v'],
    'd': ['s', 'f'],
    'e': ['w', 'r'],
    'f': ['d', 'g'],
    'g': ['f', 'h'],
    'h': ['g', 'j', 'n'],
    'i': ['o', 'u', '1'],
    'j': ['k', 'h', 'i'],
    'k': ['l', 'j'],
    'l': ['i', '1', 'k'],
    'm': ['n'],
    'n': ['m'],
    'o': ['p', 'i', '0'],
    'p': ['o', 'q'],
    'r': ['t', 'e'],
    's': ['a', 'd', '5'],
    't': ['7', 'y', 'z', 'r'],
    'u': ['v', 'i', 'y', 'z'],
    'v': ['u', 'c', 'b'],
    'w': ['v', 'vv', 'q', 'e'],
    'x': ['z', 'y', 'c'],
    'y': ['z', 'x'],
    'z': ['y', 'x'],
    '0': ['o'],
    '1': ['l'],
    '2': ['5'],
    '3': ['e'],
    '4': ['a'],
    '5': ['s'],
    '6': ['b'],
    '7': ['t'],
    '8': ['b'],
    '9': []
}

pairs = {
    'oo': ['00'],
    'll': ['l1l', 'l1l', '111', '11'],
    '11': ['ll', 'lll', 'l1l', '1l1']
}


class PublicSuffixList(object):
    def __init__(self, input_data):
        """Reads and parses public suffix list.

        input_file is a file object or another iterable that returns
        lines of a public suffix list file. If input_file is None, an
        UTF-8 encoded file named "publicsuffix.txt" in the same
        directory as this Python module is used.

        The file format is described at http://publicsuffix.org/list/
        """

        # if input_file is None:
        # input_path = os.path.join(os.path.dirname(__file__), 'publicsuffix.txt')
        # input_file = codecs.open(input_path, "r", "utf8")

        root = self._build_structure(input_data)
        self.root = self._simplify(root)

    def _find_node(self, parent, parts):
        """

        :param parent:determin one parent node
        :param parts:determine parts of domain
        :return:node related to child_node
        """
        if not parts:
            return parent

        if len(parent) == 1:
            parent.append({})

        assert len(parent) == 2
        negate, children = parent

        child = parts.pop()

        child_node = children.get(child, None)

        if not child_node:
            children[child] = child_node = [0]
        return self._find_node(child_node, parts)

    def _add_rule(self, root, rule):
        """

        :param root:determin root
        :param rule:rule in the public suffix file
        """
        if rule.startswith('!'):
            negate = 1
            rule = rule[1:]
        else:
            negate = 0

        parts = rule.split('.')
        self._find_node(root, parts)[0] = negate

    def _simplify(self, node):
        """

        :param node:determine one node
        :return:a list of node in standart format
        """

        if len(node) == 1:
            return node[0]

        return node[0], dict((k, self._simplify(v)) for (k, v) in node[1].items())

    def _build_structure(self, fp):
        """

        :param fp:input file of tlds.txt
        :return:return a list contains rules
        """
        root = [0]

        for line in fp:
            line = line.strip()
            if line.startswith('//') or not line:
                continue

            self._add_rule(root, line.split()[0].lstrip('.'))
        return root

    def _lookup_node(self, matches, depth, parent, parts):
        """

        :param matches:determine matches in format of list
        :param depth:determine depth
        :param parent:determine parent dns
        :param parts:determine splited  parts of domain
        """

        if parent in (0, 1):
            negate = parent
            children = None
        else:
            negate, children = parent

        matches[-depth] = negate

        if depth < len(parts) and children:
            for name in ('*', parts[-depth]):
                child = children.get(name, None)
                if child is not None:
                    self._lookup_node(matches, depth + 1, child, parts)

    def get_public_suffix(self, domain):
        """get_public_suffix("www.example.com") -> "example.com"

        Calling this function with a DNS name will return the
        public suffix for that name.

        Note that for internationalized domains the list at
        http://publicsuffix.org uses decoded names, so it is
        up to the caller to decode any Punycode-encoded names.
        :param domain:this parameter determine one hostname
        :return:extracted domain name  from hostname
        """

        parts = domain.lower().lstrip('.').split('.')
        hits = [None] * len(parts)
        self._lookup_node(hits, 1, self.root, parts)

        for i, what in enumerate(hits):
            if what is not None and what == 0:
                return '.'.join(parts[i:])


class SimilarDomain(object):
    TLDS = []

    def __init__(self, parent=None):
        self.parent = parent  # type: BaseModule
        if not SimilarDomain.TLDS:
            ApiLogging.info("open TLDS file for read...")
            path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            file = open(path + '/vendor/data/tlds.txt')
            lines = file.readlines()

            for line in lines:

                linee = line.strip()
                if len(linee) < 1:
                    continue
                SimilarDomain.TLDS.append(linee)
            file.close()

        self.internettlds = SimilarDomain.TLDS
        self.results = list()

    def update_progressbar(self, message, percent):
        self.parent.progress = {'state': message, 'percent': percent}

    @staticmethod
    def parse_result(full_domain, domain_name, tld):
        """
        :param full_domain:this parameter determine one domain name with tld
        :param domain_name:this parameter determine one domain name
        :param tld:this parameter determine one domain tld
        :return:one domain name in the form of entity_property
        """
        main_res = {}
        properties_list = []
        main_res["type"] = 12
        main_res["data"] = full_domain
        properties_list.append({"name": domain_name, "type": 0})
        properties_list.append({"tld": tld, "type": 0})
        main_res["special_properties"] = properties_list
        return main_res

    @staticmethod
    # Clean DNS results to be a simple list
    def normalizeDNS(res):
        """
        :param res:list of result to be normalized
        :return:list of normalized result
        """
        ret = list()
        for addr in res:
            if type(addr) == list:
                for host in addr:
                    ret.append(host)
            else:
                ret.append(addr)
        return ret

    def generate_domains(self, domain):
        """
        :param domain:this parameter determine one domain name
        :return:list domain name similar to input domain
        """
        domlist = list()
        count = domain.count('.')
        tld = ''
        sub = ''
        dom = ''
        return_result = {}
        # if tld exist in TLDS list, the below code use to find tld, subdomain and domain
        for i in range(0, len(self.internettlds)):
            if (self.internettlds[i]) != '':
                if domain.endswith(str(('.' + self.internettlds[i]))):
                    # use .intertld[i] as tld
                    tld = self.internettlds[i]
                    # last part after '.' is domain ( after removing tld)
                    rest = domain.replace('.' + tld, '')
                    dom = rest.split('.')[-1]
                    # rest is subdomain
                    sub = rest.replace(dom, '')
        self.parent.check_point()
        # if tld is not exist in tld file, use the below code to find domain, tld and subdomain
        if tld == '':
            # use chars that exist after the last '.' as tld
            tld = "." + domain.split(".")[count]
            # use chars that exist between two last '.' as domain
            rest = domain.replace(tld, '')
            dom = rest.split('.')[-1]
            # use the rest string as sub domain
            sub = rest.replace(dom, '')

        # Search for typos
        pos = 0
        for c in dom:
            if c not in nearchars:
                continue
            if len(nearchars[c]) == 0:
                continue
            npos = pos + 1
            for xc in nearchars[c]:
                newdom = dom[0:pos] + xc + dom[npos:len(dom)]
                domlist.append(newdom)

            pos += 1

        # Search for common double-letter re
        for p in pairs:
            if p in dom:
                for r in pairs[p]:
                    domlist.append(dom.replace(p, r))

        # Search for prefixed and suffixed domains
        for c in nearchars:
            domlist.append(dom + c)
            domlist.append(c + dom)

        # Search for double character domains
        pos = 0
        for c in dom:
            domlist.append(dom[0:pos] + c + c + dom[(pos + 1):len(dom)])
            pos += 1

        reslist = []

        custom_tlds = ['com', 'ir', 'net', 'org', 'tk', 'me', 'biz']
        if tld not in custom_tlds:
            custom_tlds.append(tld)
        self.update_progressbar(" domain has been created: " + str(0),
                                0)
        i = 0
        self.parent.check_point()
        for d in domlist:
            try:
                for ctld in custom_tlds:
                    res = self.parse_result(sub + d + '.' + ctld, d, ctld)
                    reslist.append(res)
                    i += 1

            except Exception:
                continue
        self.update_progressbar(" domain has been created: " + str(100),
                                100)

        return_result["results"] = reslist[0:100]
        return return_result
