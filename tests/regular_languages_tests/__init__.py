from __future__ import unicode_literals

from prompt_toolkit.contrib.regular_languages.grammar import StateMachine, Character

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

        self.assertEqual(list(m.complete('x')), [])
