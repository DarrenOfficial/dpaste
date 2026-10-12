# -*- encoding: utf-8 -*-

from datetime import timedelta

from django.apps import apps
from django.core import management
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse

from ..highlight import PygmentsHighlighter
from ..models import Snippet

config = apps.get_app_config("dpaste")


class SnippetTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.new_url = reverse("snippet_new")

    def valid_form_data(self, **kwargs):
        data = {
            "content": u"Hello Wörld.\n\tGood Bye",
            "lexer": config.LEXER_DEFAULT,
            "expires": config.EXPIRE_DEFAULT,
        }
        if kwargs:
            data.update(kwargs)
        return data

    def test_about(self):
        response = self.client.get(reverse("dpaste_about"))
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
        data["content"] = ""
        self.client.post(self.new_url, data)
        self.assertEqual(Snippet.objects.count(), 0)

        # Just some spaces
        data["content"] = "   "
        self.client.post(self.new_url, data)
        self.assertEqual(Snippet.objects.count(), 0)

        # Linebreaks or tabs only are not valid either
        data["content"] = "\n\t "
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
        self.assertContains(response, data["content"])

        # The unicode method contains the snippet id so we can easily print
        # the id using {{ snippet }}
        snippet = Snippet.objects.all()[0]
        self.assertTrue(snippet.secret_id in snippet.__str__())

    def test_new_snippet_custom_lexer(self):
        # You can pass a lexer key in GET.l
        data = self.valid_form_data()
        url = "%s?l=haskell" % self.new_url
        response = self.client.post(url, data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Snippet.objects.count(), 1)

        # If you pass an invalid key it wont fail and just fallback
        # to the default lexer.
        data = self.valid_form_data()
        url = "%s?l=invalid-lexer" % self.new_url
        response = self.client.post(url, data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Snippet.objects.count(), 2)

    def test_new_spam_snippet(self):
        """
        The form has a `website` field acting as a honeypot, if its filled,
        the snippet is considered as spam. We let the user know its spam.
        """
        data = self.valid_form_data()
        data["website"] = "Any content"
        response = self.client.post(self.new_url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Snippet.objects.count(), 0)

    def test_new_snippet_onetime(self):
        """
        One-Time snippets get deleted after two views.
        """
        # POST data
        data = self.valid_form_data()
        data["expires"] = "onetime"

        # First view, the author gets redirected after posting
        response = self.client.post(self.new_url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Snippet.objects.count(), 1)
        self.assertContains(response, data["content"])

        # Second View, another user looks at the snippet
        response = self.client.get(response.request["PATH_INFO"], follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Snippet.objects.count(), 1)
        self.assertContains(response, data["content"])

        # Third/Further View, another user looks at the snippet but it was deleted
        response = self.client.get(response.request["PATH_INFO"], follow=True)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Snippet.objects.count(), 0)

    def test_snippet_notfound(self):
        url = reverse("snippet_details", kwargs={"snippet_id": "abcd"})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_random_slug_generation(self):
        """
        The default slug length is 4 so with 10000 random slug generation we
        will run into duplicates, but those slugs are extended now.
        """
        config.SLUG_LENGTH = 1

        for i in range(0, 100):
            Snippet.objects.create(content="foobar")
        slug_list = Snippet.objects.values_list("secret_id", flat=True).order_by(
            "published"
        )

        # All 1001 Snippets have been created
        self.assertEqual(len(set(slug_list)), 100)

        # There will be a couple of snippets with at least 2 characters
        # in slug length
        extended_snippet = (
            Snippet.objects.extra(select={"length": "Length(secret_id)"})
            .order_by("-length")
            .first()
        )
        self.assertTrue(len(extended_snippet.secret_id) > 1)

        # Set back to default
        config.SLUG_LENGTH = 4

    # -------------------------------------------------------------------------
    # Reply
    # -------------------------------------------------------------------------
    def test_reply(self):
        data = self.valid_form_data()
        response = self.client.post(self.new_url, data, follow=True)
        response = self.client.post(response.request["PATH_INFO"], data, follow=True)
        self.assertContains(response, data["content"])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Snippet.objects.count(), 2)

    def test_reply_invalid(self):
        data = self.valid_form_data()
        response = self.client.post(self.new_url, data, follow=True)
        del data["content"]
        response = self.client.post(response.request["PATH_INFO"], data, follow=True)
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
        url = reverse("snippet_details", kwargs={"snippet_id": snippet_id})
        response = self.client.post(url, {"delete": 1}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Snippet.objects.count(), 0)

    def test_snippet_delete_that_doesnotexist_returns_404(self):
        data = self.valid_form_data()
        self.client.post(self.new_url, data, follow=True)

        url = reverse("snippet_details", kwargs={"snippet_id": "doesnotexist"})
        response = self.client.post(url, {"delete": 1}, follow=True)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(Snippet.objects.count(), 1)

    def test_snippet_delete_do_not_pass_delete_action(self):
        data = self.valid_form_data()
        self.client.post(self.new_url, data, follow=True)

        # Do not pass delete=1
        snippet_id = Snippet.objects.all()[0].secret_id
        url = reverse("snippet_details", kwargs={"snippet_id": snippet_id})
        response = self.client.post(url, {}, follow=True)

        # Returns regular snippet details page
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Snippet.objects.count(), 1)

    def test_snippet_is_removed_when_expired_and_as_soon_as_fetched(self):
        data = self.valid_form_data()
        self.client.post(self.new_url, data, follow=True)

        # Set the expire time of the snippet to the past.
        s = Snippet.objects.all()[0]
        s.expires = s.expires - timedelta(days=30)
        s.save()

        # Next time its fetched its automatically deleted.
        snippet_id = Snippet.objects.all()[0].secret_id
        url = reverse("snippet_details", kwargs={"snippet_id": snippet_id})
        response = self.client.get(url, follow=True)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(Snippet.objects.count(), 0)

    # -------------------------------------------------------------------------
    # Snippet Functions
    # -------------------------------------------------------------------------
    def test_raw(self):
        data = self.valid_form_data()
        self.client.post(self.new_url, data, follow=True)
        response = self.client.get(
            reverse(
                "snippet_details_raw",
                kwargs={"snippet_id": Snippet.objects.all()[0].secret_id},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, data["content"])

    def test_slim(self):
        data = self.valid_form_data()
        self.client.post(self.new_url, data, follow=True)
        response = self.client.get(
            reverse(
                "snippet_details_slim",
                kwargs={"snippet_id": Snippet.objects.all()[0].secret_id},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hello")

    # -------------------------------------------------------------------------
    # Title
    # -------------------------------------------------------------------------
    def test_title(self):
        data = self.valid_form_data(title="  My   <b>Title</b> ")
        response = self.client.post(self.new_url, data, follow=True)
        self.assertEqual(Snippet.objects.get().title, "My <b>Title</b>")
        self.assertContains(response, "<title>My &lt;b&gt;Title&lt;/b&gt; - dpaste/")
        self.assertContains(response, 'class="snippet-title"')

    def test_title_falls_back_to_first_line(self):
        data = self.valid_form_data(content="\n  first line\nsecond line")
        response = self.client.post(self.new_url, data, follow=True)
        self.assertEqual(Snippet.objects.get().title, "")
        self.assertContains(response, "<title>first line - dpaste/")
        self.assertNotContains(response, 'class="snippet-title"')

    def test_title_of_onetime_snippet_does_not_leak_content(self):
        data = self.valid_form_data(content="secret", expires="onetime")
        response = self.client.post(self.new_url, data, follow=True)
        self.assertContains(response, "<title>dpaste/")

    def test_title_too_long(self):
        data = self.valid_form_data(title="a" * (config.TITLE_MAX_LENGTH + 1))
        self.client.post(self.new_url, data, follow=True)
        self.assertEqual(Snippet.objects.count(), 0)

    # -------------------------------------------------------------------------
    # View count and link previews
    # -------------------------------------------------------------------------
    PREVIEW_USER_AGENTS = (
        "TelegramBot (like TwitterBot)",
        "WhatsApp/2.23.20.0",
        "Mozilla/5.0 (compatible; Discordbot/2.0; +https://discordapp.com)",
        "Slackbot-LinkExpanding 1.0 (+https://api.slack.com/robots)",
        "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/601.2.4 "
        "(KHTML, like Gecko) Version/9.0.1 Safari/601.2.4 "
        "facebookexternalhit/1.1 Facebot Twitterbot/1.0",
    )

    def test_view_count(self):
        data = self.valid_form_data()
        response = self.client.post(self.new_url, data, follow=True)
        self.assertContains(response, "1 view")
        response = self.client.get(response.request["PATH_INFO"])
        self.assertContains(response, "2 views")

    def test_link_preview_is_not_a_view(self):
        data = self.valid_form_data()
        response = self.client.post(self.new_url, data, follow=True)
        url = response.request["PATH_INFO"]
        for user_agent in self.PREVIEW_USER_AGENTS:
            response = self.client.get(url, headers={"user-agent": user_agent})
            self.assertContains(response, data["content"])
        self.client.head(url)
        self.assertEqual(Snippet.objects.get().view_count, 1)

        # Regular browsers and tools are views
        self.client.get(url, headers={"user-agent": "curl/8.5.0"})
        self.client.get(
            url,
            headers={
                "user-agent": "Mozilla/5.0 (X11; Linux x86_64; rv:130.0) "
                "Gecko/20100101 Firefox/130.0"
            },
        )
        self.assertEqual(Snippet.objects.get().view_count, 3)

    def test_link_preview_does_not_destroy_onetime_snippet(self):
        data = self.valid_form_data(expires="onetime")
        response = self.client.post(self.new_url, data, follow=True)
        url = response.request["PATH_INFO"]

        # The link is posted in a messenger, which fetches it right away.
        for user_agent in self.PREVIEW_USER_AGENTS:
            response = self.client.get(url, headers={"user-agent": user_agent})
            self.assertEqual(response.status_code, 200)
            self.assertNotContains(response, "Hello")
        self.assertEqual(self.client.head(url).status_code, 200)
        raw_url = reverse(
            "snippet_details_raw",
            kwargs={"snippet_id": Snippet.objects.get().secret_id},
        )
        response = self.client.get(
            raw_url, headers={"user-agent": self.PREVIEW_USER_AGENTS[0]}
        )
        self.assertNotContains(response, "Hello")

        # The recipient still gets to see it, once.
        response = self.client.get(url)
        self.assertContains(response, "Hello")
        self.assertEqual(self.client.get(url).status_code, 404)

    # -------------------------------------------------------------------------
    # Snippet URL
    # -------------------------------------------------------------------------
    def test_snippet_url_uses_request_host(self):
        data = self.valid_form_data()
        response = self.client.post(
            self.new_url, data, follow=True, headers={"host": "paste.example.org"}
        )
        snippet = Snippet.objects.get()
        self.assertContains(
            response, f'value="http://paste.example.org/{snippet.secret_id}"'
        )

    def test_snippet_url_uses_base_url(self):
        config.BASE_URL = "https://paste.example.org/"
        try:
            data = self.valid_form_data()
            response = self.client.post(self.new_url, data, follow=True)
            snippet = Snippet.objects.get()
            self.assertContains(
                response, f'value="https://paste.example.org/{snippet.secret_id}"'
            )
        finally:
            config.BASE_URL = ""

    # -------------------------------------------------------------------------
    # XSS and correct escaping
    # -------------------------------------------------------------------------
    XSS_ORIGINAL = "<script>hello</script>"
    XSS_ESCAPED = "&lt;script&gt;hello&lt;/script&gt;"

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
        data = self.valid_form_data(content=self.XSS_ORIGINAL, lexer="python")
        response = self.client.post(self.new_url, data, follow=True)
        self.assertContains(response, self.XSS_ESCAPED)

    def test_leading_white_is_retained_in_db(self):
        """
        Leading Whitespace is retained in the db.
        """
        content = " one\n  two\n   three\n    four"
        data = self.valid_form_data(content=content)
        self.client.post(self.new_url, data, follow=True)
        self.assertEqual(Snippet.objects.all()[0].content, content)

    def test_highlighting(self):
        # You can pass any lexer to the pygmentize function and it will
        # never fail loudly.
        PygmentsHighlighter().highlight("code", "python")
        PygmentsHighlighter().highlight("code", "doesnotexist")

    # -------------------------------------------------------------------------
    # History
    # -------------------------------------------------------------------------
    def test_snippet_history(self):
        response = self.client.get(reverse("snippet_history"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Snippet.objects.count(), 0)

        data = self.valid_form_data()
        self.client.post(self.new_url, data, follow=True)
        response = self.client.get(reverse("snippet_history"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Snippet.objects.count(), 1)

    def test_snippet_history_delete_all(self):
        # Empty list, delete all raises no error
        response = self.client.post(
            reverse("snippet_history"), {"delete": 1}, follow=True
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
            reverse("snippet_history"), {"delete": 1}, follow=True
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
        management.call_command("cleanup_snippets", dry_run=True)
        self.assertEqual(Snippet.objects.count(), 2)

        # Calling the management command will delete this one
        management.call_command("cleanup_snippets")
        self.assertEqual(Snippet.objects.count(), 1)

    def test_delete_management_snippet_never_expires_not_get_deleted(
        self,
    ):
        """
        Snippets without an expiration date wont get deleted automatically.
        """
        data = self.valid_form_data()
        data["expires"] = "never"
        self.client.post(self.new_url, data, follow=True)

        self.assertEqual(Snippet.objects.count(), 1)
        management.call_command("cleanup_snippets")
        self.assertEqual(Snippet.objects.count(), 1)
