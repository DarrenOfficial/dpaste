# -*- encoding: utf-8 -*-

from datetime import timedelta

from django.core import management
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from django.test.utils import override_settings

from ..forms import EXPIRE_DEFAULT
from ..highlight import LEXER_DEFAULT, PLAIN_CODE, PLAIN_TEXT
from ..models import Snippet


class SnippetTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.new_url = reverse('snippet_new')

    def valid_form_data(self, **kwargs):
        data = {
            'content': u"Hello Wörld.\n\tGood Bye",
            'lexer': LEXER_DEFAULT,
            'expires': EXPIRE_DEFAULT,
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
        self.assertTrue(snippet.secret_id in snippet.__unicode__())

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
        data['title'] = u'Any content'
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
    # Delete
    # -------------------------------------------------------------------------
    def test_snippet_delete_post(self):
        """
        You can delete a snippet by passing the slug in POST.snippet_id
        """
        data = self.valid_form_data()
        self.client.post(self.new_url, data, follow=True)
        snippet_id = Snippet.objects.all()[0].secret_id
        response = self.client.post(reverse('snippet_delete'),
            {'snippet_id': snippet_id}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Snippet.objects.count(), 0)

    def test_snippet_delete_urlarg(self):
        """
        You can delete a snippet by having the snippet id in the URL.
        """
        data = self.valid_form_data()
        self.client.post(self.new_url, data, follow=True)
        snippet_id = Snippet.objects.all()[0].secret_id
        response = self.client.get(reverse('snippet_delete',
            kwargs={'snippet_id': snippet_id}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Snippet.objects.count(), 0)

    def test_snippet_delete_that_doesnotexist_returns_404(self):
        data = self.valid_form_data()
        self.client.post(self.new_url, data, follow=True)

        # Pass a random snippet id
        response = self.client.post(reverse('snippet_delete'),
            {'snippet_id': 'doesnotexist'}, follow=True)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Snippet.objects.count(), 1)

        # Do not pass any snippet_id
        response = self.client.post(reverse('snippet_delete'), follow=True)
        self.assertEqual(response.status_code, 404)
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
    # The diff function takes two snippet primary keys via GET.a and GET.b
    # and compares them.
    # -------------------------------------------------------------------------
    def test_snippet_diff_no_args(self):
        # Do not pass `a` or `b` is a bad request.
        response = self.client.get(reverse('snippet_diff'))
        self.assertEqual(response.status_code, 400)


    def test_snippet_diff_invalid_args(self):
        # Random snippet ids that dont exist
        url = '%s?a=%s&b=%s' % (reverse('snippet_diff'), 123, 456)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)

    def test_snippet_diff_valid_nochanges(self):
        # A diff of two snippets is which are the same is OK.
        data = self.valid_form_data()
        self.client.post(self.new_url, data, follow=True)
        self.client.post(self.new_url, data, follow=True)

        self.assertEqual(Snippet.objects.count(), 2)
        a = Snippet.objects.all()[0].id
        b = Snippet.objects.all()[1].id
        url = '%s?a=%s&b=%s' % (reverse('snippet_diff'), a, b)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_snippet_diff_valid(self):
        # Create two valid snippets with different content.
        data = self.valid_form_data()
        self.client.post(self.new_url, data, follow=True)
        data['content'] = 'new content'
        self.client.post(self.new_url, data, follow=True)

        self.assertEqual(Snippet.objects.count(), 2)
        a = Snippet.objects.all()[0].id
        b = Snippet.objects.all()[1].id
        url = '%s?a=%s&b=%s' % (reverse('snippet_diff'), a, b)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    # -------------------------------------------------------------------------
    # XSS and correct escaping
    # -------------------------------------------------------------------------
    XSS_ORIGINAL = u'<script>hello</script>'
    XSS_ESCAPED = u'&lt;script&gt;hello&lt;/script&gt;'

    def test_xss_text_lexer(self):
        # Simple 'text' lexer
        data = self.valid_form_data(content=self.XSS_ORIGINAL, lexer=PLAIN_TEXT)
        response = self.client.post(self.new_url, data, follow=True)
        self.assertContains(response, self.XSS_ESCAPED)

    def test_xss_code_lexer(self):
        # Simple 'code' lexer
        data = self.valid_form_data(content=self.XSS_ORIGINAL, lexer=PLAIN_CODE)
        response = self.client.post(self.new_url, data, follow=True)
        self.assertContains(response, self.XSS_ESCAPED)

    def test_xss_pygments_lexer(self):
        # Pygments based lexer
        data = self.valid_form_data(content=self.XSS_ORIGINAL,
            lexer='python')
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

    @override_settings(DPASTE_MAX_SNIPPETS_PER_USER=2)
    def test_snippet_that_exceed_history_limit_get_trashed(self):
        """
        The maximum number of snippets a user can save in the session are
        defined by `DPASTE_MAX_SNIPPETS_PER_USER`. Exceed that number will
        remove the oldest snippet from the list.
        """
        # Create three snippets but since the setting is 2 only the latest two
        # will displayed on the history.
        data = self.valid_form_data()
        self.client.post(self.new_url, data, follow=True)
        self.client.post(self.new_url, data, follow=True)
        self.client.post(self.new_url, data, follow=True)

        response = self.client.get(reverse('snippet_history'), follow=True)
        one, two, three = Snippet.objects.order_by('published')

        # Only the last two are saved in the session
        self.assertEqual(len(self.client.session['snippet_list']), 2)
        self.assertFalse(one.id in self.client.session['snippet_list'])
        self.assertTrue(two.id in self.client.session['snippet_list'])
        self.assertTrue(three.id in self.client.session['snippet_list'])

        # And only the last two are displayed on the history page
        self.assertNotContains(response, one.secret_id)
        self.assertContains(response, two.secret_id)
        self.assertContains(response, three.secret_id)


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

    def test_delete_management_snippet_that_never_expires_will_not_get_deleted(self):
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
        from ..highlight import pygmentize
        pygmentize('code', lexer_name='python')
        pygmentize('code', lexer_name='doesnotexist')

    @override_settings(DPASTE_SLUG_LENGTH=1)
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
            'secret_id', flat=True).order_by('published')
        self.assertEqual(len(set(slug_list)), 100)
