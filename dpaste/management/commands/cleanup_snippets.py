from datetime import timedelta

from django.apps import apps
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils import timezone

from dpaste.models import Snippet

config = apps.get_app_config("dpaste")


class Command(BaseCommand):
    help = "Purges snippets that are expired"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            dest="dry_run",
            help="Don't do anything.",
        )
        parser.add_argument(
            "--skip-abuse-filter",
            action="store_true",
            dest="skip_abuse_filter",
            help="Don't delete the snippets detected by the abuse filter.",
        )

    def handle(self, *args, **options):
        self.cleanup_expired(**options)

        # Snippets which have been fine when they were created, but link to
        # a domain which was blocked in the meantime.
        if config.ABUSE_FILTER_ENABLED and not options.get("skip_abuse_filter"):
            call_command(
                "purge_abuse",
                dry_run=bool(options.get("dry_run")),
                stdout=self.stdout,
                stderr=self.stderr,
            )

    def cleanup_expired(self, **options):
        # Snippets which are expired but haven't been deleted by
        # the view.
        deleteable_snippets = Snippet.objects.filter(
                expires__isnull=False,
                expire_type=Snippet.EXPIRE_TIME,
                expires__lte=timezone.now(),
            )

        # Snipets which are Onetime snippets but have never been viewed
        # the second time. Delete them if they are older than our default
        # expiration, unless that default is not an integer (e.g., 'never')
        if isinstance(config.EXPIRE_DEFAULT, int):
            onetime_unviewed_snippets = Snippet.objects.filter(
                    expire_type=Snippet.EXPIRE_ONETIME,
                    published__lte=(
                        timezone.now() - timedelta(seconds=config.EXPIRE_DEFAULT)
                    ),
                )
            deleteable_snippets = (deleteable_snippets | onetime_unviewed_snippets)

        if len(deleteable_snippets) == 0:
            self.stdout.write(u"No snippets to delete.")
            return None
        self.stdout.write(u"Will delete %s snippet(s):\n" % deleteable_snippets.count())

        for d in deleteable_snippets:
            self.stdout.write(u"- %s (%s)\n" % (d.secret_id, d.expires))

        if options.get("dry_run"):
            self.stdout.write("Dry run - Not actually deleting snippets!\n")
        else:
            deleteable_snippets.delete()
