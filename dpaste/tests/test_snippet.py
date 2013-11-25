# -*- encoding: utf-8 -*-

from datetime import timedelta

from django.core import management
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

    # -------------------------------------------------------------------------
    # New Snippet
    # -------------------------------------------------------------------------
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
        # Simple GET
        response = self.client.get(self.new_url, follow=True)

        # POST data
        data = self.valid_form_data()
        response = self.client.post(self.new_url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Snippet.objects.count(), 1)
        self.assertContains(response, data['content'])

    def test_new_spam_snippet(self):
        """
        The form has a `title` field acting as a honeypot, if its filled,
        the snippet is considered as spam. We let the user know its spam.
        """
        data = self.valid_form_data()
        data['title'] = u'Any content'
        response = self.client.post(self.new_url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Snippet.objects.count(), 0)

    # -------------------------------------------------------------------------
    # Reply
    # -------------------------------------------------------------------------
    def test_reply(self):
        data = self.valid_form_data()
        response = self.client.post(self.new_url, data, follow=True)
        response = self.client.post(response.request['PATH_INFO'], data, follow=True)
        self.assertContains(response, data['content'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Snippet.objects.count(), 2)

    def test_reply_invalid(self):
        data = self.valid_form_data()
        response = self.client.post(self.new_url, data, follow=True)
        del data['content']
        response = self.client.post(response.request['PATH_INFO'], data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Snippet.objects.count(), 1)

    # -------------------------------------------------------------------------
    # Snippet Functions
    # -------------------------------------------------------------------------
    def test_raw(self):
        data = self.valid_form_data()
        self.client.post(self.new_url, data, follow=True)
        response = self.client.get(reverse('snippet_details_raw', kwargs={
            'snippet_id': Snippet.objects.all()[0].secret_id}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, data['content'])

    # -------------------------------------------------------------------------
    # History
    # -------------------------------------------------------------------------
    def test_snippet_history(self):
        response = self.client.get(reverse('snippet_history'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Snippet.objects.count(), 0)

        data = self.valid_form_data()
        self.client.post(self.new_url, data, follow=True)
        response = self.client.get(reverse('snippet_history'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Snippet.objects.count(), 1)

    def test_snippet_history_delete_all(self):
        # Empty list, delete all raises no error
        response = self.client.get(reverse('snippet_history') + '?delete-all', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Snippet.objects.count(), 0)

        # Create two sample pasts
        data = self.valid_form_data()
        self.client.post(self.new_url, data, follow=True)
        data = self.valid_form_data()
        self.client.post(self.new_url, data, follow=True)
        self.assertEqual(Snippet.objects.count(), 2)

        # Delete all of them
        response = self.client.get(reverse('snippet_history') + '?delete-all', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Snippet.objects.count(), 0)

    # -------------------------------------------------------------------------
    # Management Command
    # -------------------------------------------------------------------------
    def test_delete_management(self):
        # Create two snippets
        data = self.valid_form_data()
        self.client.post(self.new_url, data, follow=True)
        data = self.valid_form_data()
        self.client.post(self.new_url, data, follow=True)
        self.assertEqual(Snippet.objects.count(), 2)

        # But the management command will only remove snippets past
        # its expiration date, so change one to last month
        s = Snippet.objects.all()[0]
        s.expires = s.expires - timedelta(days=30)
        s.save()

        # You can call the management command with --dry-run which will
        # list snippets to delete, but wont actually do.
        management.call_command('cleanup_snippets', dry_run=True)
        self.assertEqual(Snippet.objects.count(), 2)

        # Calling the management command will delete this one
        management.call_command('cleanup_snippets')
        self.assertEqual(Snippet.objects.count(), 1)
