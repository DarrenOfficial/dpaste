from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from dpaste import abuse
from dpaste.models import BlockedDomain


class Command(BaseCommand):
    help = (
        "Manages the domain blocklist. Snippets which link to a blocked "
        "domain, or one of its subdomains, are rejected and deleted."
    )

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="action", required=True)

        add = subparsers.add_parser("add", help="Block one or more domains.")
        add.add_argument("domains", nargs="+", help="Domain or URL.")

        load = subparsers.add_parser(
            "import",
            help="Block all domains listed in a file, one domain or URL per "
            "line. Quotes, trailing commas and comments (# or //) are ignored.",
        )
        load.add_argument("file")

        for subparser in (add, load):
            subparser.add_argument("--note", default="", help="Why it is blocked.")
            subparser.add_argument(
                "--no-purge",
                action="store_true",
                dest="no_purge",
                help="Don't delete the existing snippets linking to these domains.",
            )

        remove = subparsers.add_parser("remove", help="Unblock one or more domains.")
        remove.add_argument("domains", nargs="+", help="Domain or URL.")

        subparsers.add_parser("list", help="List all blocked domains.")

    def handle(self, *args, **options):
        return getattr(self, "handle_%s" % options["action"])(**options)

    def block(self, values, note, no_purge):
        added = 0
        for value in values:
            domain = abuse.normalize_domain(value)
            if not domain:
                self.stderr.write("Not a domain: %s\n" % value)
                continue
            _, created = BlockedDomain.objects.get_or_create(
                domain=domain, defaults={"note": note}
            )
            added += created
        self.stdout.write("%s domain(s) added to the blocklist.\n" % added)

        if not no_purge:
            call_command("purge_abuse", stdout=self.stdout, stderr=self.stderr)

    def handle_add(self, domains, note, no_purge, **options):
        self.block(domains, note, no_purge)

    def handle_import(self, file, note, no_purge, **options):
        try:
            with open(file, encoding="utf-8") as f:
                entries = abuse.parse_list(f.read())
        except OSError as e:
            raise CommandError("Can't read %s: %s" % (file, e))
        self.block(entries, note, no_purge)

    def handle_remove(self, domains, **options):
        domains = [abuse.normalize_domain(d) for d in domains]
        # Delete one by one, so the cached blocklist is cleared.
        removed = 0
        for blocked in BlockedDomain.objects.filter(domain__in=domains):
            blocked.delete()
            removed += 1
        self.stdout.write("%s domain(s) removed from the blocklist.\n" % removed)

    def handle_list(self, **options):
        for blocked in BlockedDomain.objects.all():
            self.stdout.write(
                "%s\t%s hit(s)\t%s\n" % (blocked.domain, blocked.hits, blocked.note)
            )
        self.stdout.write(
            "%s blocked domain(s), %s keyword(s).\n"
            % (BlockedDomain.objects.count(), len(abuse.get_keywords()))
        )
