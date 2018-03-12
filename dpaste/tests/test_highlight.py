# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

from dpaste import highlight
from django.test import TestCase


class HighlightAPITestCase(TestCase):
    def test_simple_highlight(self):
        input = 'int_value = 1'
        expected = 'int_value = 1'

        value = highlight.pygmentize(input, lexer_name='python')
        self.assertEqual(input, expected)