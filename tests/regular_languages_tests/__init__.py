from __future__ import unicode_literals

from prompt_toolkit.contrib.regular_languages.grammar import StateMachine, Character
from prompt_toolkit.contrib.regular_languages.grammar2 import Node, Any, Sequence, Literal, Variable, compile, Match, Repeat

import unittest

#__all__ = (
#    'CharacterTest',
#    'RegularLanguagesTest',
#)

class CharacterTest(unittest.TestCase):
    def test_characters(self):
        c = Character('abc')

        self.assertEqual(c.characters, 'abc')
        self.assertEqual(c.inverted, False)

    def test_characters_inverted(self):
        c = Character('abc')
        d = ~ c  # This should invert, but not change the original.
        e = ~ d

        self.assertEqual(c.characters, 'abc')
        self.assertEqual(c.inverted, False)

        self.assertEqual(d.characters, 'abc')
        self.assertEqual(d.inverted, True)

        self.assertEqual(e.characters, 'abc')
        self.assertEqual(e.inverted, False)


class RegularLanguagesTest(unittest.TestCase):
    def setUp(self):
        self.c = Character('x')
        self.m = StateMachine.from_character(self.c)

    def test_initial(self):
        self.assertEqual(list(self.m.match('x')), ['MATCH'])
        self.assertEqual(list(self.m.match('y')), [])

    def test_concatenation(self):
        m1 = StateMachine.from_character(Character('x'))
        m2 = StateMachine.from_character(Character('y'))
        m = m1 + m2

        self.assertEqual(list(m.match('x')), [])
        self.assertEqual(list(m.match('y')), [])
        self.assertEqual(list(m.match('xy')), ['MATCH'])
        self.assertEqual(list(m.match('')), [])

    def test_union(self):
        m1 = StateMachine.from_character(Character('x'))
        m2 = StateMachine.from_character(Character('y'))
        m = m1 | m2

        self.assertEqual(list(m.match('x')), ['MATCH'])
        self.assertEqual(list(m.match('y')), ['MATCH'])
        self.assertEqual(list(m.match('xy')), [])

    def test_complete(self):
        m1 = StateMachine.from_character(Character('x'))
        m2 = StateMachine.from_character(Character('y'))
        m3 = StateMachine.from_character(Character('z'))
        m = m1 + m2 + m3

        self.assertEqual(list(m.complete('x')), ['yz'])

    """
    def test_large_input(self):
        c = Character('x')
        m = StateMachine.from_character(self.c)
        for _ in range(0, 1000):
            #m = m | (m + m)
            m = (m + m)

        result = list(m.match('x'*100))
        print(result)
    """


class Grammar2Test(unittest.TestCase):
    def test_simple_match(self):
        grammar = Literal('hello') | Literal('world')
        t = compile(grammar)

        m = t.match('hello')
        self.assertIsInstance(m, Match)

        m = t.match('world')
        self.assertIsInstance(m, Match)

        m = t.match('somethingelse')
        self.assertEqual(m, None)

    def test_label(self):
        grammar = Variable(Literal('hello') | Literal('world'), varname='varname') | Literal('test')
        t = compile(grammar)

        m = t.match('hello')
        self.assertEqual(m.variables(), {'varname': 'hello'})

        m = t.match('world')
        self.assertEqual(m.variables(), {'varname': 'world'})

        m = t.match('test')
        self.assertEqual(m.variables(), {'varname': None})

    def test_concatenation(self):
        grammar = Literal('hello') + Literal('world')
        t = compile(grammar)

        m = t.match('helloworld')
        self.assertIsInstance(m, Match)

        m = t.match('hello')
        self.assertEqual(m, None)

    def test_prefix(self):
        grammar = (Literal('hello') + Literal(" ") + Literal('world')) | Literal('something else')
        t = compile(grammar)

        print(t.re_text)
        print(t.re_prefix_text)
        print(t.match_prefix('he').variables())
        print(t.match_prefix('hello ').variables())
        print(t.match_prefix('hello wo').variables())
        print(t.match_prefix('hello world').variables())

        print('--')
        print(t.match_prefix('he').nodes())
        print(t.match_prefix('hello ').nodes())
        print(t.match_prefix('hello wo').nodes())
        print(t.match_prefix('hello world').nodes())

        #m = t.match_prefix('hello wo')
        #e = m.re_match

    def test_something(self):
        from prompt_toolkit.contrib.regular_languages.grammar2 import Character
        grammar = Literal('"') + Repeat(Character('[^"]')) + Literal('"')
        t = compile(grammar)

        #print('-----')
        #print(t.re_text)
        #print(t.match('"hello world"').nodes())
        #print(t.match('"hello world"').re_match.regs)

        #for k, v in t.match('"hello world"').nodes_and_parts():
        ##for k, v in t.match_prefix('"hello worl').nodes_and_parts():
        #    print ('    ', k, '   ', v)

        #print(t.match_prefix('"hello wor').nodes())

    def test_something(self):
        from prompt_toolkit.contrib.regular_languages.grammar2 import Character, Variable
        grammar = Repeat(Character('[\s]')) + \
                Variable(Literal('"') + Repeat(Character('[^"]')) + Literal('"'), varname='var1') + \
                Repeat(Character('[\s]'))
        grammar = Literal('"') + Repeat(Character('[\s]'))
        grammar = Literal('"') + Repeat(Literal('a'))
        t = compile(grammar)

        m = t.match('   "abc')
        print(m)



