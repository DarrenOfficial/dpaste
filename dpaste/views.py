import datetime
import difflib
import json

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.http import (Http404, HttpResponse, HttpResponseBadRequest,
                         HttpResponseRedirect)
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.defaults import page_not_found as django_page_not_found
from django.views.defaults import server_error as django_server_error
from django.views.generic.base import View, TemplateView
from django.views.generic.detail import DetailView
from pygments.lexers import get_lexer_for_filename
from pygments.util import ClassNotFound

from .forms import EXPIRE_CHOICES, get_expire_values, SnippetForm
from .highlight import (LEXER_DEFAULT, LEXER_KEYS, LEXER_LIST,
                              LEXER_WORDWRAP, PLAIN_CODE, pygmentize)
from .models import ONETIME_LIMIT, Snippet

template_globals = {
    'site_name': getattr(settings, 'DPASTE_SITE_NAME', 'dpaste.de'),
    'jquery_url': getattr(settings, 'DPASTE_JQUERY_URL',
        '//ajax.googleapis.com/ajax/libs/jquery/1/jquery.js'),
}

# -----------------------------------------------------------------------------
# Snippet Handling
# -----------------------------------------------------------------------------

from django.views.generic import FormView

class SnippetView(FormView):
    """
    Create a new snippet.
    """
    form_class = SnippetForm
    template_name = 'dpaste/snippet_new.html'

    def get_form_kwargs(self):
        kwargs = super(SnippetView, self).get_form_kwargs()
        kwargs.update({
            'request': self.request,
        })
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super(SnippetView, self).get_context_data(**kwargs)
        ctx.update(template_globals)
        ctx.update({
            'lexer_list': LEXER_LIST,
        })
        return ctx

    def form_valid(self, form):
        snippet = form.save()
        return HttpResponseRedirect(snippet.get_absolute_url())


class SnippetDetailView(SnippetView, DetailView):
    """
    Details list view of a snippet. Handles the actual view, reply and
    tree/diff view.
    """
    queryset = Snippet.objects.all()
    template_name = 'dpaste/snippet_details.html'
    slug_url_kwarg = 'snippet_id'
    slug_field = 'secret_id'

    def get(self, *args, **kwargs):
        snippet = self.get_object()

        # One-Time snippet get deleted if the view count matches our limit
        if snippet.expire_type == Snippet.EXPIRE_ONETIME \
        and snippet.view_count >= ONETIME_LIMIT:
            snippet.delete()
            raise Http404()

        # Increase the view count of the snippet
        snippet.view_count += 1
        snippet.save()

        return super(SnippetDetailView, self).get(*args, **kwargs)

    def get_initial(self):
        snippet = self.get_object()
        return {
            'content': snippet.content,
            'lexer': snippet.lexer,
        }

    def form_valid(self, form):
        snippet = form.save(parent=self.get_object())
        return HttpResponseRedirect(snippet.get_absolute_url())

    def get_context_data(self, **kwargs):
        self.object = snippet = self.get_object()
        tree = snippet.get_root().get_descendants(include_self=True)

        ctx = super(SnippetDetailView, self).get_context_data(**kwargs)
        ctx.update(template_globals)
        ctx.update({
            'highlighted': self.highlight_snippet().splitlines(),
            'tree': tree,
            'wordwrap': snippet.lexer in LEXER_WORDWRAP and 'True' or 'False',
        })
        return ctx

    def highlight_snippet(self):
        snippet = self.get_object()
        h = pygmentize(snippet.content, snippet.lexer)
        h = h.replace(u'  ', u'&nbsp;&nbsp;')
        h = h.replace(u'\t', '&nbsp;&nbsp;&nbsp;&nbsp;')
        return h

class SnippetRawView(SnippetDetailView):
    """
    Display the raw content of a snippet
    """
    template_name = 'dpaste/snippet_details_raw.html'

    def render_to_response(self, context, **response_kwargs):
        snippet = self.get_object()
        response = HttpResponse(snippet.content)
        response['Content-Type'] = 'text/plain;charset=UTF-8'
        response['X-Content-Type-Options'] = 'nosniff'
        return response


class SnippetDeleteView(View):
    """
    Delete a snippet. This is allowed by anybody as long as he knows the
    snippet id. I got too many manual requests to do this, mostly for legal
    reasons and the chance to abuse this is not given anyway, since snippets
    always expire.
    """
    def dispatch(self, request, *args, **kwargs):
        snippet_id = self.kwargs.get('snippet_id') or request.POST.get('snippet_id')
        if not snippet_id:
            raise Http404('No snippet id given')
        snippet = get_object_or_404(Snippet, secret_id=snippet_id)
        snippet.delete()
        return HttpResponseRedirect(reverse('snippet_new'))


class SnippetHistory(TemplateView):
    """
    Display the last `n` snippets created by this user (and saved in his
    session).
    """
    template_name = 'dpaste/snippet_list.html'

    def get(self, request, *args, **kwargs):
        snippet_id_list = request.session.get('snippet_list', [])
        self.snippet_list = Snippet.objects.filter(pk__in=snippet_id_list)

        if 'delete-all' in request.GET:
            self.snippet_list.delete()
            return HttpResponseRedirect(reverse('snippet_history'))
        return super(SnippetHistory, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(SnippetHistory, self).get_context_data(**kwargs)
        ctx.update(template_globals)
        ctx.update({
            'snippets_max': getattr(settings, 'DPASTE_MAX_SNIPPETS_PER_USER', 10),
            'snippet_list': self.snippet_list,
        })
        return ctx


class SnippetDiffView(TemplateView):
    """
    Display a diff between two given snippet secret ids.
    """
    template_name = 'dpaste/snippet_diff.html'

    def get(self, request, *args, **kwargs):
        """
        Some validation around input files we will compare later.
        """
        if request.GET.get('a') and request.GET.get('a').isdigit() \
        and request.GET.get('b') and request.GET.get('b').isdigit():
            try:
                self.fileA = Snippet.objects.get(pk=int(request.GET.get('a')))
                self.fileB = Snippet.objects.get(pk=int(request.GET.get('b')))
            except ObjectDoesNotExist:
                return HttpResponseBadRequest(u'Selected file(s) does not exist.')
        else:
            return HttpResponseBadRequest(u'You must select two snippets.')

        return super(SnippetDiffView, self).get(request, *args, **kwargs)

    def get_diff(self):
        class DiffText(object):
            pass

        diff = DiffText()

        if self.fileA.content != self.fileB.content:
            d = difflib.unified_diff(
                self.fileA.content.splitlines(),
                self.fileB.content.splitlines(),
                'Original',
                'Current',
                lineterm=''
            )

            diff.content = '\n'.join(d).strip()
            diff.lexer = 'diff'
        else:
            diff.content = _(u'No changes were made between this two files.')
            diff.lexer = 'text'

        return diff

    def highlight_snippet(self, content):
        h = pygmentize(content, 'diff')
        h = h.replace(u'  ', u'&nbsp;&nbsp;')
        h = h.replace(u'\t', '&nbsp;&nbsp;&nbsp;&nbsp;')
        return h

    def get_context_data(self, **kwargs):
        diff = self.get_diff()
        highlighted = self.highlight_snippet(diff.content)
        ctx = super(SnippetDiffView, self).get_context_data(**kwargs)
        ctx.update(template_globals)
        ctx.update({
            'snippet': diff,
            'highlighted': highlighted.splitlines(),
            'fileA': self.fileA,
            'fileB': self.fileB,
        })
        return ctx


# -----------------------------------------------------------------------------
# Static pages
# -----------------------------------------------------------------------------

class AboutView(TemplateView):
    """
    A rather static page, we need a view just to display a couple of
    statistics.
    """
    template_name = 'dpaste/about.html'

    def get_context_data(self, **kwargs):
        ctx = super(AboutView, self).get_context_data(**kwargs)
        ctx.update(template_globals)
        ctx.update({
            'total': Snippet.objects.count(),
            'stats': Snippet.objects.values('lexer').annotate(
                count=Count('lexer')).order_by('-count')[:5],
        })
        return ctx


# -----------------------------------------------------------------------------
# API Handling
# -----------------------------------------------------------------------------

def _format_default(s):
    """The default response is the snippet URL wrapped in quotes."""
    return u'"%s%s"' % (BASE_URL, s.get_absolute_url())

def _format_url(s):
    """The `url` format returns the snippet URL, no quotes, but a linebreak after."""
    return u'%s%s\n' % (BASE_URL, s.get_absolute_url())

def _format_json(s):
    """The `json` format export."""
    return json.dumps({
        'url': u'%s%s' % (BASE_URL, s.get_absolute_url()),
        'content': s.content,
        'lexer': s.lexer,
    })

BASE_URL = getattr(settings, 'DPASTE_BASE_URL', 'https://dpaste.de')

FORMAT_MAPPING = {
    'default': _format_default,
    'url': _format_url,
    'json': _format_json,
}


class APIView(View):
    """
    API View
    """
    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        content = request.POST.get('content', '').strip()
        lexer = request.POST.get('lexer', LEXER_DEFAULT).strip()
        filename = request.POST.get('filename', '').strip()
        expires = request.POST.get('expires', '').strip()
        format = request.POST.get('format', 'default').strip()

        if not content:
            return HttpResponseBadRequest('No content given')

        # We need at least a lexer or a filename
        if not lexer and not filename:
            return HttpResponseBadRequest('No lexer or filename given. Unable to '
                'determine a highlight. Valid lexers are: %s' % ', '.join(LEXER_KEYS))

        # A lexer is given, check if its valid at all
        if lexer and lexer not in LEXER_KEYS:
            return HttpResponseBadRequest('Invalid lexer "%s" given. Valid lexers are: %s' % (
                lexer, ', '.join(LEXER_KEYS)))

        # No lexer is given, but we have a filename, try to get the lexer out of it.
        # In case Pygments cannot determine the lexer of the filename, we fallback
        # to 'plain' code.
        if not lexer and filename:
            try:
                lexer_cls = get_lexer_for_filename(filename)
                lexer = lexer_cls.aliases[0]
            except (ClassNotFound, IndexError):
                lexer = PLAIN_CODE

        if expires:
            expire_options = [str(i) for i in dict(EXPIRE_CHOICES).keys()]
            if not expires in expire_options:
                return HttpResponseBadRequest('Invalid expire choice "{}" given. '
                    'Valid values are: {}'.format(expires, ', '.join(expire_options)))
            expires, expire_type = get_expire_values(expires)
        else:
            expires = datetime.datetime.now() + datetime.timedelta(seconds=60 * 60 * 24 * 30)
            expire_type = Snippet.EXPIRE_TIME

        s = Snippet.objects.create(
            content=content,
            lexer=lexer,
            expires=expires,
            expire_type=expire_type,
        )
        s.save()

        if not format in FORMAT_MAPPING:
            response = _format_default(s)
        else:
            response = FORMAT_MAPPING[format](s)

        return HttpResponse(response)


# -----------------------------------------------------------------------------
# Custom 404 and 500 views. Its easier to integrate this as a app if we
# handle them here.
# -----------------------------------------------------------------------------

def page_not_found(request, template_name='dpaste/404.html'):
    return django_page_not_found(request, template_name) # pragma: no cover

def server_error(request, template_name='dpaste/500.html'):
    return django_server_error(request, template_name) # pragma: no cover
