
__all__ = (
    'StateMachine',
    'Repeat',
    'Character',
)


class StateMachine(object):
    """
    `StateMachine`: Nondeterministic finite automaton.

    Actually, this is also the start state itself of the state machine.
    """
    def __init__(self, transations=None, accept=True):
        self.transitions = transations or []  # (Character, State) tuples. We can have multiple transitions for one character.
        self.accept = accept
        self.autocompleter = None
        self.placeholder = None

    def get_accepting_states(self):
        result = []

        for char, state in self.transitions:
            result.extend(state.get_accepting_states())

        if self.accept:
            result.append(self)

        return result

    def copy(self):
        """
        Create deep copy of state machine.
        """

    def __add_(self, other):
        # Create a new state machine for which other is appended to the
        # 'Accepting' states of the machine that we currently have.
        # `accept` becomes false for the machine that we have.
        self2 = self.copy()
        other2 = other.copy() # XXX: I don't think we need to copy this one.

        for s in self2.accepting_states:
            s.transitions.append((None, other2))
            s.accept = False

        return StateMachine(transitions=[(None, self2)])

    def __or__(self, other):
        """
        Merge State machines.
        """
        return StateMachine(transitions=[
            (None, self),
            (None, other)
        ])

    def match(self, inputstring):
        if inputstring:
            first_char, rest = inputstring[0], inputstring[1:]

            for char, state in self.transitions:
                if char == first_char:
                    # It's non deterministic. So several paths could lead to
                    # matches.
                    for m in state.match(rest):
                        yield m

        elif not inputstring and self.accept:
            yield MATCH


    def complete(self, inputstring):
        if inputstring:
            first_char, rest = inputstring[0], inputstring[1:]

            for char, state in self.transitions:
                if char == first_char:
                    for completion in state.complete(rest):
                        yield completion

        if not inputstring:
            for char, state in self.transitions:
                for completion in state.complete(rest):
                    yield Completion(char + completion.suffix)


        if self.accept:
            # Accepting state. Yield empty completion.
            yield Completion()



class Repeat(StateMachine):
    def __init__(self, sub_state_machine):
        self.sub_state_machine = sub_state_machine

    def copy(self):
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
