# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from dpaste.highlight import PLAIN_CODE, pygmentize


class HighlightAPITestCase(TestCase):

    def test_plain_code(self):
        """
        PLAIN_CODE is not run through Pygments, test it separately.
        """
        input = 'var'
        expected = '<span class="nn">var</span>'
        value = pygmentize(input, lexer_name=PLAIN_CODE)
        self.assertEqual(value, expected)

    def test_plain_code_leading_whitespace(self):
        """
        Whitespace on the first line is retained.
        """
        input = ' var=1'
        expected = '<span class="nn"> var=1</span>'
        value = pygmentize(input, lexer_name=PLAIN_CODE)
        self.assertEqual(value, expected)

    def test_plain_code_leading_whitespace_multiline(self):
        """
        Whitespace on the first line is retained, also on subsequent lines.
        """
        input = (' var=1\n'
                 '  var=2\n'
                 '   var=3\n'
                 '    var=4')
        expected = (
            '<span class="nn"> var=1</span>\n'
            '<span class="nn">  var=2</span>\n'
            '<span class="nn">   var=3</span>\n'
            '<span class="nn">    var=4</span>')
        value = pygmentize(input, lexer_name=PLAIN_CODE)
        self.assertEqual(value, expected)

    def test_pygments(self):
        """
        Pygemnts highlights the variable name, and also generally adds
        a trailing \n to all its result.
        """
        input = 'var'
        expected = '<span class="n">var</span>\n'
        value = pygmentize(input, lexer_name='python')
        self.assertEqual(value, expected)

    def test_pygments_leading_whitespace(self):
        """
        Whitespace on the first line is retained.
        """
        input = ' var'
        expected = ' <span class="n">var</span>\n'
        value = pygmentize(input, lexer_name='python')
        self.assertEqual(value, expected)

    def test_pygments_leading_whitespace_multiline(self):
        """
        Whitespace on the first line is retained, also on subsequent lines.
        """
        input = (' var\n'
                 '  var\n'
                 '   var\n'
                 '    var')
        expected = (
            ' <span class="n">var</span>\n'
            '  <span class="n">var</span>\n'
            '   <span class="n">var</span>\n'
            '    <span class="n">var</span>\n')
        value = pygmentize(input, lexer_name='python')
        self.assertEqual(value, expected)
