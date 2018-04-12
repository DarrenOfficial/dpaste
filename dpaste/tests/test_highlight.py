# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

from textwrap import dedent

from django.test import TestCase

from dpaste.highlight import PLAIN_CODE, PygmentsHighlighter, \
    PlainCodeHighlighter, RestructuredTextHighlighter


class HighlightAPITestCase(TestCase):

    def test_plain_code(self):
        """
        PLAIN_CODE is not run through Pygments, test it separately.
        """
        input = 'var'
        expected = '<span class="plain">var</span>'
        value = PlainCodeHighlighter().highlight(input)
        self.assertEqual(value, expected)

    def test_plain_code_leading_whitespace(self):
        """
        Whitespace on the first line is retained.
        """
        input = ' var=1'
        expected = '<span class="plain"> var=1</span>'
        value = PlainCodeHighlighter().highlight(input)
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
            '<span class="plain"> var=1</span>\n'
            '<span class="plain">  var=2</span>\n'
            '<span class="plain">   var=3</span>\n'
            '<span class="plain">    var=4</span>')
        value = PlainCodeHighlighter().highlight(input)
        self.assertEqual(value, expected)

    def test_pygments(self):
        """
        Pygemnts highlights the variable name, and also generally adds
        a trailing \n to all its result.
        """
        input = 'var'
        expected = '<span class="n">var</span>\n'
        value = PygmentsHighlighter().highlight(input, 'python')
        self.assertEqual(value, expected)

    def test_pygments_leading_whitespace(self):
        """
        Whitespace on the first line is retained.
        """
        input = ' var'
        expected = ' <span class="n">var</span>\n'
        value = PygmentsHighlighter().highlight(input, 'python')
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
        value = PygmentsHighlighter().highlight(input, 'python')
        self.assertEqual(value, expected)


    def test_broken_rst_syntax(self):
        """
        rst Syntax thats not valid must not raise an exception (SystemMessage)
        """
        # (SEVERE/4) Missing matching underline for section title overline.
        input = dedent("""
        =========================
        Generate 15 random numbers
        70 180 3 179 192 117 75 72 90 190 49 159 63 14 55 
        =========================
        """)
        try:
            RestructuredTextHighlighter().highlight(input)
        except Exception as e:
            self.fail('rst syntax raised unexpected exception: {}'.format(e))
