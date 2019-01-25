# -*- encoding: utf-8 -*-

from datetime import timedelta

from django.apps import apps
from django.core import management
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse

from ..highlight import PygmentsHighlighter
from ..models import Snippet

config = apps.get_app_config('dpaste')


class SnippetTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.new_url = reverse('snippet_new')

    def valid_form_data(self, **kwargs):
        data = {
            'content': u"Hello Wörld.\n\tGood Bye",
            'lexer': config.LEXER_DEFAULT,
            'expires': config.EXPIRE_DEFAULT,
        }
        if kwargs:
            data.update(kwargs)
        return data

    def test_about(self):
        response = self.client.get(reverse('dpaste_about'))
        self.assertEqual(response.status_code, 200)

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

        # The unicode method contains the snippet id so we can easily print
        # the id using {{ snippet }}
        snippet = Snippet.objects.all()[0]
        self.assertTrue(snippet.secret_id in snippet.__str__())

    def test_new_snippet_custom_lexer(self):
        # You can pass a lexer key in GET.l
        data = self.valid_form_data()
        url = '%s?l=haskell' % self.new_url
        response = self.client.post(url, data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Snippet.objects.count(), 1)

        # If you pass an invalid key it wont fail and just fallback
        # to the default lexer.
        data = self.valid_form_data()
        url = '%s?l=invalid-lexer' % self.new_url
        response = self.client.post(url, data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Snippet.objects.count(), 2)

    def test_new_spam_snippet(self):
        """
        The form has a `title` field acting as a honeypot, if its filled,
        the snippet is considered as spam. We let the user know its spam.
        """
        data = self.valid_form_data()
        data['title'] = 'Any content'
        response = self.client.post(self.new_url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Snippet.objects.count(), 0)

    def test_new_snippet_onetime(self):
        """
        One-Time snippets get deleted after two views.
        """
        # POST data
        data = self.valid_form_data()
        data['expires'] = 'onetime'

        # First view, the author gets redirected after posting
        response = self.client.post(self.new_url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Snippet.objects.count(), 1)
        self.assertContains(response, data['content'])

        # Second View, another user looks at the snippet
        response = self.client.get(response.request['PATH_INFO'], follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Snippet.objects.count(), 1)
        self.assertContains(response, data['content'])

        # Third/Further View, another user looks at the snippet but it was deleted
        response = self.client.get(response.request['PATH_INFO'], follow=True)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Snippet.objects.count(), 0)

    def test_snippet_notfound(self):
        url = reverse('snippet_details', kwargs={'snippet_id': 'abcd'})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 404)

    # -------------------------------------------------------------------------
    # Reply
    # -------------------------------------------------------------------------
    def test_reply(self):
        data = self.valid_form_data()
        response = self.client.post(self.new_url, data, follow=True)
        response = self.client.post(
            response.request['PATH_INFO'], data, follow=True
        )
        self.assertContains(response, data['content'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Snippet.objects.count(), 2)

    def test_reply_invalid(self):
        data = self.valid_form_data()
        response = self.client.post(self.new_url, data, follow=True)
        del data['content']
        response = self.client.post(
            response.request['PATH_INFO'], data, follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Snippet.objects.count(), 1)

    # -------------------------------------------------------------------------
    # Delete
    # -------------------------------------------------------------------------
    def test_snippet_delete_post(self):
        """
        You can delete a snippet by passing the slug in POST.snippet_id
        """
        data = self.valid_form_data()
        self.client.post(self.new_url, data, follow=True)

        snippet_id = Snippet.objects.all()[0].secret_id
        url = reverse('snippet_details', kwargs={'snippet_id': snippet_id})
        response = self.client.post(url, {'delete': 1}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Snippet.objects.count(), 0)

    def test_snippet_delete_that_doesnotexist_returns_404(self):
        data = self.valid_form_data()
        self.client.post(self.new_url, data, follow=True)

        url = reverse('snippet_details', kwargs={'snippet_id': 'doesnotexist'})
        response = self.client.post(url, {'delete': 1}, follow=True)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(Snippet.objects.count(), 1)

    def test_snippet_delete_do_not_pass_delete_action(self):
        data = self.valid_form_data()
        self.client.post(self.new_url, data, follow=True)

        # Do not pass delete=1
        snippet_id = Snippet.objects.all()[0].secret_id
        url = reverse('snippet_details', kwargs={'snippet_id': snippet_id})
        response = self.client.post(url, {}, follow=True)

        # Returns regular snippet details page
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Snippet.objects.count(), 1)

    # -------------------------------------------------------------------------
    # Snippet Functions
    # -------------------------------------------------------------------------
    def test_raw(self):
        data = self.valid_form_data()
        self.client.post(self.new_url, data, follow=True)
        response = self.client.get(
            reverse(
                'snippet_details_raw',
                kwargs={'snippet_id': Snippet.objects.all()[0].secret_id},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, data['content'])

    # -------------------------------------------------------------------------
    # XSS and correct escaping
    # -------------------------------------------------------------------------
    XSS_ORIGINAL = '<script>hello</script>'
    XSS_ESCAPED = '&lt;script&gt;hello&lt;/script&gt;'

    def test_xss_text_lexer(self):
        # Simple 'text' lexer
        data = self.valid_form_data(
            content=self.XSS_ORIGINAL, lexer=config.PLAIN_TEXT_SYMBOL
        )
        response = self.client.post(self.new_url, data, follow=True)
        self.assertContains(response, self.XSS_ESCAPED)

    def test_xss_code_lexer(self):
        # Simple 'code' lexer
        data = self.valid_form_data(
            content=self.XSS_ORIGINAL, lexer=config.PLAIN_CODE_SYMBOL
        )
        response = self.client.post(self.new_url, data, follow=True)
        self.assertContains(response, self.XSS_ESCAPED)

    def test_xss_pygments_lexer(self):
        # Pygments based lexer
        data = self.valid_form_data(content=self.XSS_ORIGINAL, lexer='python')
        response = self.client.post(self.new_url, data, follow=True)
        self.assertContains(response, self.XSS_ESCAPED)

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
        response = self.client.post(
            reverse('snippet_history'), {'delete': 1}, follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Snippet.objects.count(), 0)

        # Create two sample pasts
        data = self.valid_form_data()
        self.client.post(self.new_url, data, follow=True)
        data = self.valid_form_data()
        self.client.post(self.new_url, data, follow=True)
        self.assertEqual(Snippet.objects.count(), 2)

        # Delete all of them
        response = self.client.post(
            reverse('snippet_history'), {'delete': 1}, follow=True
        )
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

    def test_delete_management_snippet_that_never_expires_will_not_get_deleted(
        self
    ):
        """
        Snippets without an expiration date wont get deleted automatically.
        """
        data = self.valid_form_data()
        data['expires'] = 'never'
        self.client.post(self.new_url, data, follow=True)

        self.assertEqual(Snippet.objects.count(), 1)
        management.call_command('cleanup_snippets')
        self.assertEqual(Snippet.objects.count(), 1)

    def test_highlighting(self):
        # You can pass any lexer to the pygmentize function and it will
        # never fail loudly.
        PygmentsHighlighter().highlight('code', 'python')
        PygmentsHighlighter().highlight('code', 'doesnotexist')

    def test_random_slug_generation(self):
        """
        Set the max length of a slug to 1, so we wont have more than 60
        different slugs (with the default slug choice string). With 100
        random slug generation we will run into duplicates, but those
        slugs are extended now.
        """
        for i in range(0, 100):
            Snippet.objects.create(content='foobar')
        slug_list = Snippet.objects.values_list(
            'secret_id', flat=True
        ).order_by('published')
        self.assertEqual(len(set(slug_list)), 100)

    def test_leading_white_is_retained_in_db(self):
        """
        Leading Whitespace is retained in the db.
        """
        content = ' one\n  two\n   three\n    four'
        data = self.valid_form_data(content=content)
        self.client.post(self.new_url, data, follow=True)
        self.assertEqual(Snippet.objects.all()[0].content, content)
