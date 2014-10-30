
__all__ = (
    'StateMachine',
    'Repeat',
    'Character',
)


class StateMachine(object):
    """
    `StateMachine`: Nondeterministic finite automaton.

    Actually, an instance of this class is also the start state itself of a
    state machine.
    """
    def __init__(self, transitions=None, accept=True):
        self.transitions = transitions or []  # (Character, State) tuples. We can have multiple transitions for one character.
        self.accept = accept
        #self.autocompleter = None
        #self.placeholder = None

    #def get_accepting_states(self):
    #    result = []

    #    for char, state in self.transitions:
    #        result.extend(state.get_accepting_states())

    #    if self.accept:
    #        result.append(self)

    #    return result

    def __repr__(self):
        return 'StateMachine(transitions=%r, accept=%r)' % (self.transitions, self.accept)

    @classmethod
    def from_character(cls, character):
        """
        Create a ``StateMachine`` with two nodes. The character is the
        transition/edge between them.
        """
        s = cls(accept=True)
        return cls(transitions=[(character, s)], accept=False)

    def __add__(self, other):
        """
        :param other: :class:`StateMachine`
        """
        # Create a new state machine for which other is appended to the
        # 'Accepting' states of the machine that we currently have.
        # `accept` becomes false for the machine that we have.

        transitions = []
        for char, s in self.transitions:
            transitions.append((char, s + other))

        if self.accept:
            transitions.append((None, other))

        return StateMachine(transitions=transitions, accept=False)

    def __or__(self, other):
        """
        Merge State machines.
        """
        # We create one accepting state, to make sure the graph does not get
        # unnessary large when apending other subgraphs.
        end_state = StateMachine(accept=True)

        return StateMachine(transitions=[
            (None, self + end_state),
            (None, other + end_state)
        ], accept=False)

    def match(self, inputstring):
        # Follow 'None' transitions.
        for char, state in self.transitions:
            if char is None:
                for m in state.match(inputstring):
                    yield m

        if inputstring:
            first_char, rest = inputstring[0], inputstring[1:]

            for char, state in self.transitions:
                if char is not None and first_char in char.characters:
                    # It's non deterministic. So several paths could lead to
                    # matches.
                    for m in state.match(rest):
                        yield m

        elif not inputstring and self.accept:
            yield 'MATCH'

    def complete(self, inputstring):
        if inputstring:
            first_char, rest = inputstring[0], inputstring[1:]

            for char, state in self.transitions:
                if char is None:
                    for completion in state.complete(inputstring):
                        yield completion
                elif first_char in char.characters:
                    for completion in state.complete(rest):
                        yield completion

        if not inputstring:
            for char, state in self.transitions:
                for completion in state.complete(''):
                    yield (char.characters if char else '') + completion # XXX


        if self.accept:
            # Accepting state. Yield empty completion.
            yield ''


class Completion(object):
    pass


class Repeat(StateMachine):
    def __init__(self, sub_state_machine):
        self.sub_state_machine = sub_state_machine

    def copy(self):
        pass

    def match(self, inputstring):
        for m in self.sub_state_machine.match(inputstring):
            if m.remainder:
                # When there is a remainder, try both a repeat and return.
                for sub_match in self.match(m.remainder):
                    yield sub_match
                yield m
            else:
                yield m

    def complete(self, inputstring):
        pass


class Label(object):
    """
    """
    def __init__(self, sub_state_machine, name='', placeholder='', description='', next_state=None):
        self.sub_state_machine = sub_state_machine
        self.name = name
        self.placeholder = placeholder
        self.description = description
        self.next_state = next_state

    @property
    def accept(self):
        return not bool(self.next_state)

    def __add__(self, other):
        if self.next_state:
            # TODO
            pass
        else:
            return Label(
                sub_state_machine=self.sub_state_machine,
                name=self.name,
                description=self.description,
                next_state=other)

    def __or__(self, other):
        pass



class Character(object):
    def __init__(self, characters=None, inverted=False):
        self.characters = characters
        self.inverted = inverted

    def __invert__(self):
        return Character(self.characters, inverted=not self.inverted)

    def __repr__(self):
        return 'Character(%r, inverted=%r)' % (self.characters, self.inverted)



# -----------------


space_characters = Character(characters=' \t')
non_space_characters = ~ Character(characters=' \t')



"""


Repeat(Literal('abcde') + Character('a-z')) | Label(Repeat(Literal('x')), name='labelname')



re.compile('(abcde[a-z]|(?P<labelname>x*))')

re.compile('(?P<literal1>(a|ab|abc|abcd|abcde))|


DISALLOW TWO LEVELS OF GREEDY MATCHING, eg::
(Terribly slow...)

    import re
    re.search("(a+)+b", "aaaaaaaaaaaaaaaa")



r = 'ab(c|d)ef"(?P<param>[^"]*)test
completers = { 'param': my_completer }

"""