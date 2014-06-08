# -*- encoding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.test.client import Client
from django.test import TestCase
from django.test.utils import override_settings

from ..models import Snippet

class SnippetAPITestCase(TestCase):

    def setUp(self):
        self.api_url = reverse('dpaste_api_create_snippet')
        self.client = Client()


    def test_empty(self):
        """
        The browser sent a content field but with no data.
        """
        data = {}

        # No data
        response = self.client.post(self.api_url, {})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Snippet.objects.count(), 0)

        # No content
        data['content'] = ''
        response = self.client.post(self.api_url, data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Snippet.objects.count(), 0)

        # Just some spaces
        data['content'] = '   '
        response = self.client.post(self.api_url, data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Snippet.objects.count(), 0)

        # Linebreaks or tabs only are not valid either
        data['content'] = '\n\t '
        response = self.client.post(self.api_url, data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Snippet.objects.count(), 0)

    def test_default_format(self):
        """
        A valid snippet, contains Unicode, tabs, spaces, linebreaks etc.
        """
        data = {'content': u"Hello Wörld.\n\tGood Bye"}

        response = self.client.post(self.api_url, data)
        content = response.content.decode('utf-8')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Snippet.objects.count(), 1)

        # The response is a URL with quotes
        self.assertTrue(content.startswith('"'))
        self.assertTrue(content.endswith('"'))

        # The URL returned is the absolute url to the snippet.
        # If we call that url our snippet should be in the page content.
        response = self.client.get(content[1:-1])

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, data['content'])

    def test_new_url_format(self):
        """
        The 'new' url format is just the link with a linebreak.
        """
        data = {'content': u"Hello Wörld.\n\tGood Bye", 'format': 'url'}

        response = self.client.post(self.api_url, data)
        content = response.content.decode('utf-8')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Snippet.objects.count(), 1)

        # Response is just the link starting with http(s) and ends with a linebreak
        self.assertTrue(content.startswith('http'))
        self.assertTrue(content.endswith('\n'))


    def test_json_format(self):
        """
        The 'new' url format is just the link with a linebreak.
        """
        data = {
            'content': u"Hello Wörld.\n\tGood Bye",
            'format': 'json',
            'lexer': 'haskell'
        }

        response = self.client.post(self.api_url, data)
        content = response.content.decode('utf-8')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Snippet.objects.count(), 1)

        from json import loads
        json_data = loads(content)

        # Response is valid json, containing, content, lexer and url
        self.assertEqual(json_data['content'], data['content'])
        self.assertEqual(json_data['lexer'], data['lexer'])
        self.assertTrue(json_data['url'].startswith('http'))

    def test_invalid_format(self):
        """
        A broken format will not raise an error, just use the default
        format.
        """

        data = {
            'content': u"Hello Wörld.\n\tGood Bye",
            'format': 'broken-format',
            'lexer': 'haskell'
        }

        response = self.client.post(self.api_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Snippet.objects.count(), 1)

    def test_invalid_lexer(self):
        """
        A broken lexer will fail loudly.
        """
        data = {
            'content': u"Hello Wörld.\n\tGood Bye",
            'lexer': 'foobar'
        }
        response = self.client.post(self.api_url, data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Snippet.objects.count(), 0)

    def test_expire_choices_none_given(self):
        # No expire choice given will set a default expiration of one month
        response = self.client.post(self.api_url, {
            'content': u"Hello Wörld.\n\tGood Bye"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Snippet.objects.count(), 1)
        self.assertTrue(Snippet.objects.all()[0].expires)

    def test_expire_choices_invalid_given(self):
        # A expire choice that does not exist returns a BadRequest
        response = self.client.post(self.api_url, {
            'content': u"Hello Wörld.\n\tGood Bye", 'expires': 'foobar'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Snippet.objects.count(), 0)

    def test_valid_expiration_choices(self):
        """
        Test all the different expiration choices. We dont actually test
        the deletion, since thats handled in the `test_snippet` section.
        """
        response = self.client.post(self.api_url, {
            'content': u"Hello Wörld.\n\tGood Bye", 'expires': 'onetime'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Snippet.objects.count(), 1)
        self.assertEqual(Snippet.objects.all()[0].expire_type, Snippet.EXPIRE_ONETIME)

        response = self.client.post(self.api_url, {
            'content': u"Hello Wörld.\n\tGood Bye", 'expires': 'never'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Snippet.objects.count(), 2)
        self.assertEqual(Snippet.objects.all()[0].expire_type, Snippet.EXPIRE_KEEP)

        response = self.client.post(self.api_url, {
            'content': u"Hello Wörld.\n\tGood Bye", 'expires': 3600})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Snippet.objects.count(), 3)
        self.assertTrue(Snippet.objects.all()[0].expires)

        response = self.client.post(self.api_url, {
            'content': u"Hello Wörld.\n\tGood Bye", 'expires': 3600 * 24 * 7})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Snippet.objects.count(), 4)
        self.assertTrue(Snippet.objects.all()[0].expires)

        response = self.client.post(self.api_url, {
            'content': u"Hello Wörld.\n\tGood Bye", 'expires': 3600 * 24 * 30})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Snippet.objects.count(), 5)
        self.assertTrue(Snippet.objects.all()[0].expires)
