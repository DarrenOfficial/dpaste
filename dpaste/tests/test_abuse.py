from io import StringIO
from tempfile import NamedTemporaryFile

from django.apps import apps
from django.core import management
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse

from .. import abuse
from ..models import BlockedDomain, Snippet

config = apps.get_app_config("dpaste")

ONION = "abcdefghijklmnopqrstuvwxyz234567abcdefghijklmnopqrstuvwxyz.onion"


class AbuseFilterTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.new_url = reverse("snippet_new")
        self.api_url = reverse("dpaste_api_create_snippet")
        abuse.clear_cache()

    def tearDown(self):
        abuse.clear_cache()

    def post(self, content, **kwargs):
        data = {
            "content": content,
            "lexer": config.LEXER_DEFAULT,
            "expires": config.EXPIRE_DEFAULT,
        }
        data.update(kwargs)
        return self.client.post(self.new_url, data, follow=True)

    def details_url(self, snippet):
        return reverse("snippet_details", kwargs={"snippet_id": snippet.secret_id})

    # -------------------------------------------------------------------------
    # Detection
    # -------------------------------------------------------------------------
    def test_regular_content_is_not_detected(self):
        content = (
            "import os.path\n"
            "self.request.session['foo'] = my_file.io.read()\n"
            "See https://docs.djangoproject.com/en/stable/ and https://github.com/\n"
            "mail me at someone@example.com\n"
        )
        self.assertIsNone(abuse.scan_text(content))

    def test_onion(self):
        match = abuse.scan_text(f"http://{ONION}/foo")
        self.assertEqual(match.reason, abuse.REASON_ONION)

        # No scheme, uppercase, behind a tor2web gateway
        self.assertIsNotNone(abuse.scan_text(f"go to {ONION.upper()} now"))
        self.assertIsNotNone(abuse.scan_text(f"https://{ONION}.ws/foo"))

        # Too short to be a hidden service
        self.assertIsNone(abuse.scan_text("http://abcdef.onion/"))

    def test_pastebin(self):
        match = abuse.scan_text("more at https://pastebin.com/raw/abcd")
        self.assertEqual(match.reason, abuse.REASON_PASTEBIN)
        self.assertEqual(match.domain, "pastebin.com")

    def test_filehost(self):
        match = abuse.scan_text("https://mega.nz/folder/abcd#efgh")
        self.assertEqual(match.reason, abuse.REASON_FILEHOST)

    def test_subdomain_and_bare_domain(self):
        self.assertIsNotNone(abuse.scan_text("files.catbox.moe/abcd.zip"))
        self.assertIsNotNone(abuse.scan_text("WWW.MediaFire.com/file/abcd"))

    def test_similar_domain_is_not_detected(self):
        self.assertIsNone(abuse.scan_text("https://notmega.nz/"))
        self.assertIsNone(abuse.scan_text("https://mega.nz.example.com/"))

    def test_defanged_links(self):
        self.assertIsNotNone(abuse.scan_text("hxxps://mega[.]nz/folder/abcd"))
        self.assertIsNotNone(abuse.scan_text("pastebin (dot) com/abcd"))
        self.assertIsNotNone(abuse.scan_text("mega​.nz/folder/abcd"))
        self.assertIsNotNone(abuse.scan_text("ｍｅｇａ．ｎｚ/folder/abcd"))

    def test_blocklist(self):
        self.assertIsNone(abuse.scan_text("https://evil.example/abcd"))
        BlockedDomain.objects.create(domain="https://www.Evil.example/some/path")
        self.assertEqual(BlockedDomain.objects.get().domain, "evil.example")

        match = abuse.scan_text("https://cdn.evil.example/abcd")
        self.assertEqual(match.reason, abuse.REASON_BLOCKLIST)
        self.assertEqual(match.domain, "evil.example")

        BlockedDomain.objects.get().delete()
        self.assertIsNone(abuse.scan_text("https://evil.example/abcd"))

    def test_allowed_domains(self):
        config.ALLOWED_LINK_DOMAINS = ("pastebin.com",)
        try:
            self.assertIsNone(abuse.scan_text("https://pastebin.com/abcd"))
        finally:
            config.ALLOWED_LINK_DOMAINS = ()

    def test_disabled(self):
        config.ABUSE_FILTER_ENABLED = False
        try:
            self.assertIsNone(abuse.scan_text("https://mega.nz/folder/abcd"))
        finally:
            config.ABUSE_FILTER_ENABLED = True

    # -------------------------------------------------------------------------
    # Snippets are not stored
    # -------------------------------------------------------------------------
    def test_form_rejects_snippet(self):
        response = self.post("get it at https://gofile.io/d/abcd")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "rejected by the abuse filter")
        self.assertEqual(Snippet.objects.count(), 0)

    def test_form_rejects_title(self):
        self.post("Hello", title=f"{ONION}")
        self.assertEqual(Snippet.objects.count(), 0)

    def test_form_allows_link_to_itself(self):
        BlockedDomain.objects.create(domain="paste.example.org")
        data = {
            "content": "as seen in https://paste.example.org/abcd",
            "lexer": config.LEXER_DEFAULT,
            "expires": config.EXPIRE_DEFAULT,
        }
        self.client.post(self.new_url, data)
        self.assertEqual(Snippet.objects.count(), 0)

        self.client.post(self.new_url, data, headers={"host": "paste.example.org"})
        self.assertEqual(Snippet.objects.count(), 1)

    def test_api_rejects_snippet(self):
        response = self.client.post(
            self.api_url, {"content": "https://pastebin.com/abcd"}
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Snippet.objects.count(), 0)

    def test_reply_is_rejected(self):
        self.post("Hello")
        snippet = Snippet.objects.get()
        data = {
            "content": "https://mega.nz/folder/abcd",
            "lexer": config.LEXER_DEFAULT,
            "expires": config.EXPIRE_DEFAULT,
        }
        self.client.post(self.details_url(snippet), data, follow=True)
        self.assertEqual(Snippet.objects.count(), 1)

    def test_hit_is_counted(self):
        BlockedDomain.objects.create(domain="evil.example")
        self.post("https://evil.example/abcd")
        blocked = BlockedDomain.objects.get()
        self.assertEqual(blocked.hits, 1)
        self.assertIsNotNone(blocked.last_hit)

    # -------------------------------------------------------------------------
    # Existing snippets are deleted
    # -------------------------------------------------------------------------
    def test_snippet_is_deleted_when_viewed(self):
        self.post("https://evil.example/abcd")
        snippet = Snippet.objects.get()
        self.assertEqual(self.client.get(self.details_url(snippet)).status_code, 200)

        # The domain is blocked after the snippet was created
        BlockedDomain.objects.create(domain="evil.example")
        self.assertEqual(self.client.get(self.details_url(snippet)).status_code, 404)
        self.assertEqual(Snippet.objects.count(), 0)

    def test_raw_snippet_is_deleted_when_viewed(self):
        self.post("https://evil.example/abcd")
        snippet = Snippet.objects.get()
        BlockedDomain.objects.create(domain="evil.example")
        url = reverse("snippet_details_raw", kwargs={"snippet_id": snippet.secret_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.assertNotContains(response, "evil.example", status_code=404)
        self.assertEqual(Snippet.objects.count(), 0)

    def test_referer_of_pastebin_deletes_snippet(self):
        self.post("Hello")
        snippet = Snippet.objects.get()
        response = self.client.get(
            self.details_url(snippet), headers={"referer": "https://pastebin.com/abcd"}
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Snippet.objects.count(), 0)

    def test_referer_of_onion_deletes_snippet(self):
        self.post("Hello")
        snippet = Snippet.objects.get()
        response = self.client.get(
            self.details_url(snippet), headers={"referer": f"http://{ONION}/links"}
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Snippet.objects.count(), 0)

    def test_referer_of_blocked_domain_deletes_snippet(self):
        BlockedDomain.objects.create(domain="evil.example")
        self.post("Hello")
        snippet = Snippet.objects.get()
        response = self.client.get(
            self.details_url(snippet), headers={"referer": "https://evil.example/"}
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Snippet.objects.count(), 0)

    def test_regular_referer_keeps_snippet(self):
        self.post("Hello")
        snippet = Snippet.objects.get()
        for referer in (
            "https://www.google.com/",
            "http://testserver/history/",
            "garbage",
            "",
        ):
            response = self.client.get(
                self.details_url(snippet), headers={"referer": referer}
            )
            self.assertEqual(response.status_code, 200)
        self.assertEqual(Snippet.objects.count(), 1)

    def test_referer_check_disabled(self):
        config.ABUSE_CHECK_REFERER = False
        try:
            self.post("Hello")
            snippet = Snippet.objects.get()
            response = self.client.get(
                self.details_url(snippet),
                headers={"referer": "https://pastebin.com/abcd"},
            )
            self.assertEqual(response.status_code, 200)
        finally:
            config.ABUSE_CHECK_REFERER = True

    # -------------------------------------------------------------------------
    # Management Commands
    # -------------------------------------------------------------------------
    def create_snippets(self):
        Snippet.objects.create(content="Hello")
        Snippet.objects.create(content="https://evil.example/abcd")
        parent = Snippet.objects.create(content="https://other.example/abcd")
        Snippet.objects.create(content="A harmless reply", parent=parent)

    def test_purge_abuse(self):
        self.create_snippets()
        BlockedDomain.objects.create(domain="evil.example")

        management.call_command("purge_abuse", dry_run=True, stdout=StringIO())
        self.assertEqual(Snippet.objects.count(), 4)

        management.call_command("purge_abuse", stdout=StringIO())
        self.assertEqual(Snippet.objects.count(), 3)
        self.assertEqual(BlockedDomain.objects.get().hits, 1)

    def test_cleanup_snippets_purges_abuse(self):
        self.create_snippets()
        BlockedDomain.objects.create(domain="evil.example")

        management.call_command(
            "cleanup_snippets", skip_abuse_filter=True, stdout=StringIO()
        )
        self.assertEqual(Snippet.objects.count(), 4)

        management.call_command("cleanup_snippets", dry_run=True, stdout=StringIO())
        self.assertEqual(Snippet.objects.count(), 4)

        management.call_command("cleanup_snippets", stdout=StringIO())
        self.assertEqual(Snippet.objects.count(), 3)

    def test_blocklist_add_purges_snippets(self):
        self.create_snippets()
        out = StringIO()
        management.call_command(
            "blocklist", "add", "evil.example", "https://Other.example/x", stdout=out
        )
        self.assertEqual(BlockedDomain.objects.count(), 2)
        # The reply to a deleted snippet is deleted with it.
        self.assertEqual(Snippet.objects.count(), 1)

        # Adding it twice is fine
        management.call_command("blocklist", "add", "evil.example", stdout=out)
        self.assertEqual(BlockedDomain.objects.count(), 2)

    def test_blocklist_add_no_purge(self):
        self.create_snippets()
        management.call_command(
            "blocklist", "add", "evil.example", no_purge=True, stdout=StringIO()
        )
        self.assertEqual(Snippet.objects.count(), 4)

    def test_blocklist_import_list_remove(self):
        with NamedTemporaryFile("w", suffix=".txt") as f:
            f.write("# nasty domains\n\nevil.example\nhttps://other.example/abcd\n")
            f.flush()
            management.call_command(
                "blocklist", "import", f.name, note="imported", stdout=StringIO()
            )
        self.assertEqual(
            list(BlockedDomain.objects.values_list("domain", "note")),
            [("evil.example", "imported"), ("other.example", "imported")],
        )

        out = StringIO()
        management.call_command("blocklist", "list", stdout=out)
        self.assertIn("evil.example", out.getvalue())

        self.assertIsNotNone(abuse.scan_text("https://evil.example/"))
        management.call_command("blocklist", "remove", "evil.example", stdout=out)
        self.assertEqual(BlockedDomain.objects.count(), 1)
        self.assertIsNone(abuse.scan_text("https://evil.example/"))
