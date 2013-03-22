# -*- encoding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.test.client import Client
from django.test import TestCase

from ..models import Snippet

class SnippetAPITestCase(TestCase):

    def setUp(self):
        self.api_url = reverse('dpaste_api_create_snippet')
        self.client = Client()

    def test_no_post_data(self):
        """
        No data passed. API returns a 400 Bad Request and no snippet
        instance was created.
        """
        response = self.client.post(self.api_url, {})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Snippet.objects.count(), 0)

    def test_empty(self):
        """
        The browser sent a content field but with no data.
        """
        # No data
        response = self.client.post(self.api_url, {'content': ''})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Snippet.objects.count(), 0)

        # Just some spaces
        response = self.client.post(self.api_url, {'content': '   '})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Snippet.objects.count(), 0)

        # Linebreaks or tabs only are not valid either
        response = self.client.post(self.api_url, {'content': '\n\t '})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Snippet.objects.count(), 0)

    def test_valid(self):
        """
        A valid snippet, contains Unicode, tabs, spaces, linebreaks etc.
        """
        content = u"Hello Wörld.\n\tGood Bye"
        response = self.client.post(self.api_url, {'content': content})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Snippet.objects.count(), 1)

        # The response is a URL with quotes
        self.assertTrue(response.content.startswith('"'))
        self.assertTrue(response.content.endswith('"'))

        # The URL returned is the absolute url to the snippet.
        # If we call that url our snippet should be in the page content.
        snippet_url = response.content[1:-1]
        response = self.client.get(snippet_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, content)
