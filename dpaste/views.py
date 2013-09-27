import datetime
import difflib
import requests

from django.shortcuts import (render_to_response, get_object_or_404,
    get_list_or_404)
from django.template.context import RequestContext
from django.http import (Http404, HttpResponseRedirect, HttpResponseBadRequest,
    HttpResponse, HttpResponseForbidden)
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.utils import simplejson
from django.db.models import Count
from django.views.defaults import (page_not_found as django_page_not_found,
    server_error as django_server_error)

from dpaste.forms import SnippetForm
from dpaste.models import Snippet
from dpaste.highlight import LEXER_WORDWRAP, LEXER_LIST

# -----------------------------------------------------------------------------
# Snippet Handling
# -----------------------------------------------------------------------------

def snippet_new(request, template_name='dpaste/snippet_new.html'):
    """
    Create a new snippet.
    """
    if request.method == "POST":
        snippet_form = SnippetForm(data=request.POST, request=request)
        if snippet_form.is_valid():
            new_snippet = snippet_form.save()
            url = new_snippet.get_absolute_url()
            return HttpResponseRedirect(url)
    else:
        snippet_form = SnippetForm(request=request)

    template_context = {
        'snippet_form': snippet_form,
        'lexer_list': LEXER_LIST,
        'is_new': True,
    }

    return render_to_response(
        template_name,
        template_context,
        RequestContext(request)
    )


def snippet_details(request, snippet_id, template_name='dpaste/snippet_details.html', is_raw=False):
    """
    Details list view of a snippet. Handles the actual view, reply and
    tree/diff view.
    """
    try:
        snippet = Snippet.objects.get(secret_id=snippet_id)
    except MultipleObjectsReturned:
        raise Http404('Multiple snippets exist for this slug. This should never '
                      'happen but its likely that you are a spam bot, so I dont '
                      'care.')
    except ObjectDoesNotExist:
        raise Http404('This snippet does not exist anymore. Its likely that its '
                      'lifetime is expired.')

    tree = snippet.get_root()
    tree = tree.get_descendants(include_self=True)

    new_snippet_initial = {
        'content': snippet.content,
        'lexer': snippet.lexer,
    }

    if request.method == "POST":
        snippet_form = SnippetForm(data=request.POST, request=request, initial=new_snippet_initial)
        if snippet_form.is_valid():
            new_snippet = snippet_form.save(parent=snippet)
            url = new_snippet.get_absolute_url()
            return HttpResponseRedirect(url)
    else:
        snippet_form = SnippetForm(initial=new_snippet_initial, request=request)

    template_context = {
        'snippet_form': snippet_form,
        'snippet': snippet,
        'lexers': LEXER_LIST,
        'lines': range(snippet.get_linecount()),
        'tree': tree,
        'wordwrap': snippet.lexer in LEXER_WORDWRAP and 'True' or 'False',
    }

    response = render_to_response(
        template_name,
        template_context,
        RequestContext(request)
    )

    if is_raw:
        response['Content-Type'] = 'text/plain;charset=UTF-8'
        return response
    else:
        return response


def snippet_delete(request, snippet_id):
    """
    Delete a snippet. This is allowed by anybody as long as he knows the
    snippet id. I got too many manual requests to do this, mostly for legal
    reasons and the chance to abuse this is not given anyway, since snippets
    always expire.
    """
    snippet = get_object_or_404(Snippet, secret_id=snippet_id)
    snippet.delete()
    return HttpResponseRedirect(reverse('snippet_new') + '?delete=1')


def snippet_history(request, template_name='dpaste/snippet_list.html'):
    """
    Display the last `n` snippets created by this user (and saved in his
    session).
    """
    try:
        snippet_list = get_list_or_404(Snippet, pk__in=request.session.get('snippet_list', None))
    except ValueError:
        snippet_list = None

    template_context = {
        'snippets_max': getattr(settings, 'DPASTE_MAX_SNIPPETS_PER_USER', 10),
        'snippet_list': snippet_list,
    }

    return render_to_response(
        template_name,
        template_context,
        RequestContext(request)
    )


def snippet_diff(request, template_name='dpaste/snippet_diff.html'):
    """
    Display a diff between two given snippet secret ids.
    """
    if request.GET.get('a') and request.GET.get('a').isdigit() \
    and request.GET.get('b') and request.GET.get('b').isdigit():
        try:
            fileA = Snippet.objects.get(pk=int(request.GET.get('a')))
            fileB = Snippet.objects.get(pk=int(request.GET.get('b')))
        except ObjectDoesNotExist:
            return HttpResponseBadRequest(u'Selected file(s) does not exist.')
    else:
        return HttpResponseBadRequest(u'You must select two snippets.')

    class DiffText(object):
        pass

    diff = DiffText()

    if fileA.content != fileB.content:
        d = difflib.unified_diff(
            fileA.content.splitlines(),
            fileB.content.splitlines(),
            'Original',
            'Current',
            lineterm=''
        )

        diff.content = '\n'.join(d).strip()
        diff.lexer = 'diff'
    else:
        diff.content = _(u'No changes were made between this two files.')
        diff.lexer = 'text'

    template_context = {
        'snippet': diff,
        'fileA': fileA,
        'fileB': fileB,
    }

    return render_to_response(
        template_name,
        template_context,
        RequestContext(request)
    )


def snippet_gist(request, snippet_id):
    """
    Put a snippet on Github Gist.
    """
    snippet = get_object_or_404(Snippet, secret_id=snippet_id)
    data = {
        'description': 'the description for this gist',
        'public': False,
        'files': {
            'dpaste.de_snippet.py': {
                'content': snippet.content,
            }
        }
    }

    try:
        payload = simplejson.dumps(data)
        response = requests.post('https://api.github.com/gists', data=payload)
        response_dict = simplejson.loads(response.content)
        gist_url = response_dict.get('html_url')

    # Github could be down, could return invalid JSON, it's rare
    except:
        return HttpResponse('Creating a Github Gist failed. Sorry, please go back and try again.')

    return HttpResponseRedirect(gist_url)


# -----------------------------------------------------------------------------
# Static pages
# -----------------------------------------------------------------------------

def about(request, template_name='dpaste/about.html'):
    """
    A rather static page, we need a view just to display a couple of
    statistics.
    """
    template_context = {
        'total': Snippet.objects.count(),
        'stats': Snippet.objects.values('lexer').annotate(
            count=Count('lexer')).order_by('-count')[:5],
    }

    return render_to_response(
        template_name,
        template_context,
        RequestContext(request)
    )


# -----------------------------------------------------------------------------
# API Handling
# -----------------------------------------------------------------------------

def snippet_api(request, enclose_quotes=True):
    content = request.POST.get('content', '').strip()

    if not content:
        return HttpResponseBadRequest()

    s = Snippet.objects.create(
        content=content,
        expires=datetime.datetime.now()+datetime.timedelta(seconds=60*60*24*30)
    )
    s.save()

    response = 'http://dpaste.de%s' % s.get_absolute_url()
    if enclose_quotes:
        return HttpResponse('"%s"' % response)
    return HttpResponse(response)


# -----------------------------------------------------------------------------
# Custom 404 and 500 views. Its easier to integrate this as a app if we
# handle them here.
# -----------------------------------------------------------------------------

def page_not_found(request, template_name='dpaste/404.html'):
    return django_page_not_found(request, template_name)


def server_error(request, template_name='dpaste/500.html'):
    return django_server_error(request, template_name)
