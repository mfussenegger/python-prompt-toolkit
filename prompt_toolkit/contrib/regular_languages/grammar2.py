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


class Literal(Node):
    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return 'Character(%r)' % (self.text, )


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
        self.variables = {}  # Mapping from 'varname' -> Variable instance
        self.nodes_to_numbers, self.nodelist = self._number_nodes(root_node)
        self.group_names_to_nodes = { }
        self._counter = 0

        self.re_text = '^%s$' % self._transform(root_node, self.nodes_to_numbers)
        self._re = re.compile(self.re_text)

        self.re_prefix_text = self._transform_prefix(root_node, self.nodes_to_numbers)
        print(self.re_prefix_text)
        self._re_prefix = re.compile(self.re_prefix_text)

    @classmethod
    def _number_nodes(cls, root_node):
        counter = [0]
        nodes_to_numbers = {}
        nodelist = []

        def traverse(node):
            c = counter[0] = counter[0] + 1

            nodes_to_numbers[node] = c
            nodelist.append(node)

            if isinstance(node, (Variable, Repeat)):
                traverse(node.childnode)
            elif isinstance(node, (Sequence, Any)):
                for child in node.children:
                    traverse(child)

        traverse(root_node)

        return nodes_to_numbers, nodelist

    def _transform(self, root_node, nodes_to_numbers):
        def transform(node):
            self._counter += 1
            name = 'node_%s' % self._counter
            self.group_names_to_nodes[name] = node
            return '(?P<%s>%s)' % (name, _transform_2(node))

        def _transform_2(node):
            if isinstance(node, Any):
                return '(?:%s)' % '|'.join(transform(c) for c in node.children)

            elif isinstance(node, Sequence):
                return ''.join(transform(c) for c in node.children)

            elif isinstance(node, Literal):
                return re.escape(node.text)

            elif isinstance(node, Character):
                return '%s' % node.data

            elif isinstance(node, Variable):
                return '%s' % transform(node.childnode)

            elif isinstance(node, Repeat):
                return '(?:%s)*' % transform(node.childnode)

            else:
                raise TypeError('Got %r' % node)

        return transform(root_node)

    def _transform_prefix(self, root_node, nodes_to_numbers):
        def transform(node):
            self._counter += 1
            name = 'node_%s' % self._counter
            self.group_names_to_nodes[name] = node
            return '(?P<%s>%s)' % (name, transform_2(node))

        def transform_2(node):
            if isinstance(node, Any):
                return '(?:%s)?' % '|'.join(transform(c) for c in node.children)

            elif isinstance(node, Sequence):
                prefix_children = [transform(c) for c in node.children]
                complete_children = [self._transform(c, nodes_to_numbers) for c in node.children]
                result = []

                for i in range(len(node.children)):
                    result.append(''.join(complete_children[:i] + prefix_children[i:i+1]))
                return '(?:%s)' % '|'.join(result)

                #count = len(children)
                #return '(?:%s' % '(?:'.join(''.join(children[i]) for i in range(count)) + ')?' * count

            elif isinstance(node, Literal):
                count = len(node.text)
                return '(?:%s' % '('.join(re.escape(node.text[i]) for i in range(count)) + ')?' * count

            elif isinstance(node, Character):
                return '(?:%s)?' % node.data

            elif isinstance(node, Variable):
                return '(?:%s)?' % transform(node.childnode)

            elif isinstance(node, Repeat):
                return '(?:%s)*' % transform(node.childnode)

        return '^%s$' % transform(root_node)

    def match(self, inputstring):
        m = self._re.match(inputstring)
        if m:
            return Match(self, self._re, m)

    def match_prefix(self, inputstring):
        m = self._re_prefix.match(inputstring)
        if m:
            return Match(self, self._re_prefix, m)


def compile(root_node):
    return _RegexTransformer(root_node)


class Match(object):
    def __init__(self, transformer, re_pattern, re_match):
        self.transformer = transformer
        self.re_pattern = re_pattern
        self.re_match = re_match

    def variables(self):
        def get(slice):
            if slice[0] == -1 and slice[1] == -1:
                return None
            else:
                return self.re_match.string[slice[0]:slice[1]]

        return { node.varname: get(slice) for node, slice in
            self.nodes_and_parts() if isinstance(node, Variable) }

        return {k[len('var_'):]:v for k, v in self.re_match.groupdict().items() if k.startswith('var_') }

    def nodes(self):
        return {int(k[len('node_'):]):v for k, v in self.re_match.groupdict().items() if k.startswith('node_') }

    def nodes_and_parts(self):  # DEBUG

                # TODO: use the self.re_pattern.groupindex {name->regs_index}
        regs = self.re_match.regs[1:]
        return [(node,r) for node, r in zip(self.transformer.nodelist, regs)]

    def complete(self):
        raise NotImplementedError
