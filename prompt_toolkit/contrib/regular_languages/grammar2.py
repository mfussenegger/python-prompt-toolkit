import re




class Node(object):
    def __add__(self, other_node):
        return Sequence([self, other_node])

    def __or__(self, other_node):
        return Any([self, other_node])


class Any(Node):
    def __init__(self, children):
        self.children = children

    def __or__(self, other_node):
        return Any(self.children + [other_node])

    def __repr__(self):
        return 'Any(len=%r)' % len(self.children)


class Sequence(Node):
    def __init__(self, children):
        self.children = children

    def __add__(self, other_node):
        return Sequence(self.children + [other_node])

    def __repr__(self):
        return 'Sequence(len=%r)' % len(self.children)


def Literal(text):
    """
    List of characters.
    """
    characters = [Character('[%s]' % re.escape(c)) for c in text]
    return Sequence(characters)


class Character(Node):
    def __init__(self, data):
        # e.g. data='[a-z]' or '[^a-z]'
        self.data = data
        assert data[0] == '['
        assert data[-1] == ']'
        assert '*' not in data
        assert '?' not in data

    def __repr__(self):
        return 'Character(%r)' % (self.data, )


class Variable(Node):
    def __init__(self, childnode, varname=None, completer=None, wrapper=None, unwrapper=None, token=None):
        #assert name.isidentifier()

        self.childnode = childnode
        self.varname = varname
        self.compler = completer
        self.wrapper = wrapper
        self.unwrapper = unwrapper
        self.token = token

    def __repr__(self):
        return 'Variable(childnode=%r, varname=%r)' % (self.childnode, self.varname)

    def unwrap(self, text):
        if self.unwrapper:
            return self.unwrapper(text)
        else:
            return text

    def wrap(self, text):
        if self.wrapper:
            return self.wrapper(text)
        else:
            return text


class Repeat(Node):
    def __init__(self, childnode):
        self.childnode = childnode

    def __repr__(self):
        return 'Repeat(childnode=%r)' % (self.childnode, )


class _RegexTransformer(object):
    """
    Transform nodes to a Python regex.
    """
    def __init__(self, root_node):
        self._group_names_to_nodes = { }
        self._prefix_group_names_to_nodes = { }

        def create_groupname_creator(dictionary):
            counter = [0]

            def create_group_func(node):
                name = 'n%s' % counter[0]
                dictionary[counter[0]] = node
                counter[0] += 1
                return name
            return create_group_func

        self.re_text = '^%s$' % self._transform(
            root_node, create_groupname_creator(self._group_names_to_nodes))

        self.re_prefix_text = self._transform_prefix(
            root_node,create_groupname_creator(self._prefix_group_names_to_nodes))

        self._re = re.compile(self.re_text)
        self._re_prefix = re.compile(self.re_prefix_text)

    @classmethod
    def _transform(cls, root_node, create_group_func):
        def transform(node):
            if isinstance(node, Any):
                return '(?:%s)' % '|'.join(transform(c) for c in node.children)

            elif isinstance(node, Sequence):
                return ''.join(transform(c) for c in node.children)

            elif isinstance(node, Character):
                return '%s' % node.data

            elif isinstance(node, Variable):
                return '(?P<%s>%s)' % (create_group_func(node), transform(node.childnode))

            elif isinstance(node, Repeat):
                return '(?:%s)*' % transform(node.childnode)

            else:
                raise TypeError('Got %r' % node)

        return transform(root_node)

    @classmethod
    def _transform_prefix(cls, root_node, create_group_func):
        def transform(node):
            if isinstance(node, Any):
                return '(?:%s)?' % '|'.join(transform(c) for c in node.children)

            elif isinstance(node, Sequence):
                result = []

                for i in range(len(node.children)):
                    a = [cls._transform(c, create_group_func) for c in node.children[:i]]
                    a.append(transform(node.children[i]))
                    result.append(''.join(a))

                return '(?:%s)' % '|'.join(result)

            elif isinstance(node, Character):
                return '(?:%s)?' % node.data

            elif isinstance(node, Variable):
                return '(?P<%s>%s)?' % (create_group_func(node), transform(node.childnode))

            elif isinstance(node, Repeat):
                return '(?:%s)*' % transform(node.childnode)

        return '^%s$' % transform(root_node)

    def match(self, inputstring):
        m = self._re.match(inputstring)
        if m:
            return Match(self, self._re, m, self._group_names_to_nodes)

    def match_prefix(self, inputstring):
        m = self._re_prefix.match(inputstring)
        if m:
            return Match(self, self._re_prefix, m, self._prefix_group_names_to_nodes)


def compile(root_node):
    return _RegexTransformer(root_node)


class Match(object):
    def __init__(self, transformer, re_pattern, re_match, group_names_to_nodes):
        self.transformer = transformer
        self.re_pattern = re_pattern
        self.re_match = re_match
        self.group_names_to_nodes = group_names_to_nodes

    def nodes(self):
        return dict((int(k[len('n'):]), v) for k, v in self.re_match.groupdict().items() if k.startswith('n'))

    def nodes_to_regs(self):
        """
        Return { Node -> reg_index } mappings.
        """
        result = {}
                # TODO: maybe use the self.re_pattern.groupindex {name->regs_index}
        regs = self.re_match.regs[1:]

        for i, r in enumerate(regs):
            node = self.group_names_to_nodes[i]

            if node not in result:
                result[node] = r

        return result

    def nodes_to_values(self):
        """
        Returns { Node -> string_value } mapping.
        """
        def get(slice):
            if slice[0] == -1 and slice[1] == -1:
                return None
            else:
                return self.re_match.string[slice[0]:slice[1]]

        return {node: get(slice) for node, slice in self.nodes_to_regs().items()}

    def variables(self):
        """
        Returns { varname -> value } mapping.
        """
        return { k.varname: k.unwrap(v) for k, v in self.nodes_to_values().items() if isinstance(k, Variable) }

    def complete(self):
        raise NotImplementedError
