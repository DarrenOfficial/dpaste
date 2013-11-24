# -*- encoding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.test.client import Client
from django.test import TestCase

from ..models import Snippet
from ..forms import EXPIRE_DEFAULT
from ..highlight import LEXER_DEFAULT


class SnippetTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.new_url = reverse('snippet_new')

    def valid_form_data(self):
        return {
            'content': u"Hello Wörld.\n\tGood Bye",
            'lexer': LEXER_DEFAULT,
            'expire_options': EXPIRE_DEFAULT,
        }

    def test_empty(self):
        """
        The browser sent a content field but with no data.
        """
        # No data
        self.client.post(self.new_url, {})
        self.assertEqual(Snippet.objects.count(), 0)

        data = self.valid_form_data()

        # No content
        data['content'] = ''
        self.client.post(self.new_url, data)
        self.assertEqual(Snippet.objects.count(), 0)

        # Just some spaces
        data['content'] = '   '
        self.client.post(self.new_url, data)
        self.assertEqual(Snippet.objects.count(), 0)

        # Linebreaks or tabs only are not valid either
        data['content'] = '\n\t '
        self.client.post(self.new_url, data)
        self.assertEqual(Snippet.objects.count(), 0)

    def test_new_snippet(self):
        data = self.valid_form_data()
        response = self.client.post(self.new_url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Snippet.objects.count(), 1)
        self.assertContains(response, data['content'])

    def test_reply(self):
        data = self.valid_form_data()
        response = self.client.post(self.new_url, data, follow=True)
        response = self.client.post(response.request['PATH_INFO'], data, follow=True)
        self.assertContains(response, data['content'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Snippet.objects.count(), 2)
