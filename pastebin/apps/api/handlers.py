import datetime
import re
from piston.utils import rc
from piston.handler import AnonymousBaseHandler
from pastebin.apps.dpaste.models import Snippet

class SnippetHandler(AnonymousBaseHandler):
    allowed_methods = ('POST',)
    fields = ('title', 'content',)
    model = Snippet

    def create(self, request):
        if not request.POST.get('content'):
            return rc.BAD_REQUEST

        s = Snippet.objects.create(
            content=request.POST.get('content'),
            expires=datetime.datetime.now()+datetime.timedelta(seconds=60*60*24*30)
        )
        s.save()
        return 'http://dpaste.de%s' % s.get_absolute_url()
