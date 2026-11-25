from django.core.management.base import BaseCommand

from dpaste import abuse


class Command(BaseCommand):
    help = "Deletes all snippets which are detected by the abuse filter"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            dest="dry_run",
            help="Don't do anything.",
        )

    def handle(self, *args, **options):
        # The blocklist might have been changed by another process.
        abuse.clear_cache()
        detected = abuse.purge_snippets(dry_run=options.get("dry_run"))

        if not detected:
            self.stdout.write("No snippets detected by the abuse filter.")
            return None
        self.stdout.write("Abuse filter detected %s snippet(s):\n" % len(detected))

        for secret_id, match in detected:
            self.stdout.write("- %s (%s: %s)\n" % (secret_id, match.reason, match.domain))

        if options.get("dry_run"):
            self.stdout.write("Dry run - Not actually deleting snippets!\n")
        else:
            self.stdout.write("Deleted.\n")
