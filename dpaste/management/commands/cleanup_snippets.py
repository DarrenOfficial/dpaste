from datetime import timedelta

from django.apps import apps
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
        ),

    def handle(self, *args, **options):
        deleteable_snippets = (
            # Snippets which are expired but haven't been deleted by
            # the view.
            Snippet.objects.filter(
                expires__isnull=False,
                expire_type=Snippet.EXPIRE_TIME,
                expires__lte=timezone.now(),
            )
            # Snipoets which are Onetime snippets but have never been viewed
            # the second time. Delete them if they are older than our default
            # expiration.
            | Snippet.objects.filter(
                expire_type=Snippet.EXPIRE_ONETIME,
                published__lte=(
                    timezone.now() - timedelta(seconds=config.EXPIRE_DEFAULT)
                ),
            )
        )

        if len(deleteable_snippets) == 0:
            self.stdout.write(u"No snippets to delete.")
            return None
        self.stdout.write(
            u"Will delete %s snippet(s):\n" % deleteable_snippets.count()
        )

        for d in deleteable_snippets:
            self.stdout.write(u"- %s (%s)\n" % (d.secret_id, d.expires))

        if options.get("dry_run"):
            self.stdout.write("Dry run - Not actually deleting snippets!\n")
        else:
            deleteable_snippets.delete()
