from __future__ import unicode_literals

from prompt_toolkit.contrib.regular_languages.grammar2 import Literal, Variable, compile, Match, Repeat, Character

import unittest

__all__ = (
    'GrammarTest',
)


class GrammarTest(unittest.TestCase):
    def test_simple_match(self):
        grammar = Literal('hello') | Literal('world')
        t = compile(grammar)

        m = t.match('hello')
        self.assertIsInstance(m, Match)

        m = t.match('world')
        self.assertIsInstance(m, Match)

        m = t.match('somethingelse')
        self.assertEqual(m, None)

    def test_variable_varname(self):
        """
        Test `Variable` with varname.
        """
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
        """
        Test `match_prefix`.
        """
        grammar = (Literal('hello') + Literal(" ") + Literal('world')) | Literal('something else')
        t = compile(grammar)

        m = t.match_prefix('hello world')
        self.assertIsInstance(m, Match)

        m = t.match_prefix('he')
        self.assertIsInstance(m, Match)

        m = t.match_prefix('')
        self.assertIsInstance(m, Match)

        m = t.match_prefix('som')
        self.assertIsInstance(m, Match)

        m = t.match_prefix('hello wor')
        self.assertIsInstance(m, Match)

        m = t.match_prefix('no-match')
        self.assertEqual(m, None)

        m = t.match_prefix('ello')
        self.assertEqual(m, None)

    def test_something(self):
        """
        Test: '"' + text + '"' grammar.
        """
        grammar = Repeat(Character('[\s]')) + \
            Variable(Literal('"') + Repeat(Character('[^"]')) + Literal('"'), varname='var1') + \
            Repeat(Character('[\s]'))
        t = compile(grammar)

        # Match full string.
        m = t.match('   "abc" ')
        self.assertIsInstance(m, Match)
        self.assertEqual(m.variables(), {'var1': '"abc"'})

        m = t.match('"abc"')
        self.assertIsInstance(m, Match)
        self.assertEqual(m.variables(), {'var1': '"abc"'})

        m = t.match('"ab')
        self.assertEqual(m, None)

        # Prefix matching.
        m = t.match_prefix('"ab')
        self.assertIsInstance(m, Match)
        self.assertEqual(m.variables(), {'var1': '"ab'})

        m = t.match_prefix('  "ab')
        self.assertIsInstance(m, Match)
        self.assertEqual(m.variables(), {'var1': '"ab'})

