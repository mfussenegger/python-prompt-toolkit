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
        pass

    def test_initial(self):
        pass
