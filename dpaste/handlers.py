import datetime
from piston.utils import rc
from piston.handler import AnonymousBaseHandler
from dpaste.models import Snippet

class SnippetHandler(AnonymousBaseHandler):
    allowed_methods = ('POST',)
    fields = ('content',)
    model = Snippet

    def create(self, request):
        content = request.POST.get('content', '').strip()

        if not content:
            return rc.BAD_REQUEST

        s = Snippet.objects.create(
            content=content,
            expires=datetime.datetime.now()+datetime.timedelta(seconds=60*60*24*30)
        )
        s.save()
        return 'http://dpaste.de%s' % s.get_absolute_url()
