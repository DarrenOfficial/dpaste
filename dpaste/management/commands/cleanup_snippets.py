import datetime
import sys
from optparse import make_option
from django.core.management.base import LabelCommand
from dpaste.models import Snippet

class Command(LabelCommand):
    option_list = LabelCommand.option_list + (
        make_option('--dry-run', '-d', action='store_true', dest='dry_run',
            help='Don\'t do anything.'),
    )
    help = "Purges snippets that are expired"

    def handle(self, *args, **options):
        deleteable_snippets = Snippet.objects.filter(
            expires__isnull=False,
            expire_type=Snippet.EXPIRE_TIME,
            expires__lte=datetime.datetime.now()
        )
        sys.stdout.write(u"%s snippets gets deleted:\n" % deleteable_snippets.count())
        for d in deleteable_snippets:
            sys.stdout.write(u"- %s (%s)\n" % (d.secret_id, d.expires))
        if options.get('dry_run'):
            sys.stdout.write(u'Dry run - Not actually deleting snippets!\n')
        else:
            deleteable_snippets.delete()
