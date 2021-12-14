import datetime
import difflib
import json

from django.apps import apps
from django.http import (
    Http404,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
    HttpResponseRedirect,
)
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.utils.cache import add_never_cache_headers, patch_cache_control
from django.utils.translation import gettext
from django.views.generic import FormView
from django.views.generic.base import TemplateView, View
from django.views.generic.detail import DetailView
from pygments.lexers import get_lexer_for_filename
from pygments.util import ClassNotFound

from dpaste import highlight
from dpaste.forms import SnippetForm, get_expire_values
from dpaste.highlight import PygmentsHighlighter
from dpaste.models import Snippet

config = apps.get_app_config("dpaste")


# -----------------------------------------------------------------------------
# Snippet Handling
# -----------------------------------------------------------------------------


class SnippetView(FormView):
    """
    Create a new snippet.
    """

    form_class = SnippetForm
    template_name = "dpaste/new.html"

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        return response

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"request": self.request})
        return kwargs

    def form_valid(self, form):
        snippet = form.save()
        return HttpResponseRedirect(snippet.get_absolute_url())

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(config.extra_template_context)
        return ctx


class SnippetDetailView(DetailView, FormView):
    """
    Details list view of a snippet. Handles the actual view, reply and
    tree/diff view.
    """

    form_class = SnippetForm
    queryset = Snippet.objects.all()
    template_name = "dpaste/details.html"
    slug_url_kwarg = "snippet_id"
    slug_field = "secret_id"

    def post(self, request, *args, **kwargs):
        """
        Delete a snippet. This is allowed by anybody as long as he knows the
        snippet id. I got too many manual requests to do this, mostly for legal
        reasons and the chance to abuse this is not given anyway, since snippets
        always expire.
        """
        if "delete" in self.request.POST:
            snippet = get_object_or_404(Snippet, secret_id=self.kwargs["snippet_id"])
            snippet.delete()

            # Append `#` so #delete goes away in Firefox
            url = "{0}#".format(reverse("snippet_new"))
            return HttpResponseRedirect(url)

        return super().post(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        snippet = self.get_object()

        # One-Time snippet get deleted if the view count matches our limit
        if (
            snippet.expire_type == Snippet.EXPIRE_TIME
            and snippet.expires < timezone.now()
        ) or (
            snippet.expire_type == Snippet.EXPIRE_ONETIME
            and snippet.view_count >= config.ONETIME_LIMIT
        ):
            snippet.delete()
            raise Http404()

        # Increase the view count of the snippet
        snippet.view_count += 1
        snippet.save(update_fields=["view_count"])

        return super().get(request, *args, **kwargs)

    def get_initial(self):
        snippet = self.get_object()
        return {
            "content": snippet.content,
            "lexer": snippet.lexer,
            "rtl": snippet.rtl,
        }

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"request": self.request})
        return kwargs

    def form_valid(self, form):
        snippet = form.save(parent=self.get_object())
        return HttpResponseRedirect(snippet.get_absolute_url())

    def get_snippet_diff(self):
        snippet = self.get_object()

        if not snippet.parent_id:
            return None

        if snippet.content == snippet.parent.content:
            return None

        d = difflib.unified_diff(
            snippet.parent.content.splitlines(),
            snippet.content.splitlines(),
            gettext("Previous Snippet"),
            gettext("Current Snippet"),
            n=1,
        )
        diff_code = "\n".join(d).strip()
        highlighted = PygmentsHighlighter().render(diff_code, "diff")

        # Remove blank lines
        return highlighted

    def get_context_data(self, **kwargs):
        self.object = self.get_object()

        ctx = super().get_context_data(**kwargs)
        ctx.update(
            {
                "wordwrap": self.object.lexer in highlight.LEXER_WORDWRAP,
                "diff": self.get_snippet_diff(),
                "raw_mode": config.RAW_MODE_ENABLED,
            }
        )
        ctx.update(config.extra_template_context)
        return ctx


class SnippetRawView(SnippetDetailView):
    """
    Display the raw content of a snippet
    """

    template_name = "dpaste/raw.html"

    def dispatch(self, request, *args, **kwargs):
        if not config.RAW_MODE_ENABLED:
            return HttpResponseForbidden(
                gettext("This dpaste installation has Raw view mode disabled.")
            )
        return super().dispatch(request, *args, **kwargs)

    def render_plain_text(self, context, **response_kwargs):
        snippet = self.get_object()
        response = HttpResponse(snippet.content)
        response["Content-Type"] = "text/plain;charset=UTF-8"
        response["X-Content-Type-Options"] = "nosniff"
        return response

    def render_to_response(self, context, **response_kwargs):
        if config.RAW_MODE_PLAIN_TEXT:
            return self.render_plain_text(config, **response_kwargs)
        return super().render_to_response(context, **response_kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(config.extra_template_context)
        return ctx


class SnippetHistory(TemplateView):
    """
    Display the last `n` snippets created by this user (and saved in his
    session).
    """

    template_name = "dpaste/history.html"

    def get_user_snippets(self):
        snippet_id_list = self.request.session.get("snippet_list", [])
        return Snippet.objects.filter(pk__in=snippet_id_list)

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        add_never_cache_headers(response)
        return response

    def post(self, request, *args, **kwargs):
        """
        Delete all user snippets at once.
        """
        if "delete" in self.request.POST:
            self.get_user_snippets().delete()

        # Append `#` so #delete goes away in Firefox
        url = "{0}#".format(reverse("snippet_history"))
        return HttpResponseRedirect(url)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({"snippet_list": self.get_user_snippets()})
        ctx.update(config.extra_template_context)
        return ctx


# -----------------------------------------------------------------------------
# API Handling
# -----------------------------------------------------------------------------


class APIView(View):
    """
    API View
    """

    def _format_default(self, s):
        """
        The default response is the snippet URL wrapped in quotes.
        """
        base_url = config.get_base_url(request=self.request)
        return f'"{base_url}{s.get_absolute_url()}"'

    def _format_url(self, s):
        """
        The `url` format returns the snippet URL,
        no quotes, but a linebreak at the end.
        """
        base_url = config.get_base_url(request=self.request)
        return f"{base_url}{s.get_absolute_url()}\n"

    def _format_json(self, s):
        """
        The `json` format export.
        """
        base_url = config.get_base_url(request=self.request)
        return json.dumps(
            {
                "url": f"{base_url}{s.get_absolute_url()}",
                "content": s.content,
                "lexer": s.lexer,
            }
        )

    def post(self, request, *args, **kwargs):
        content = request.POST.get("content", "")
        lexer = request.POST.get("lexer", highlight.LEXER_DEFAULT).strip()
        filename = request.POST.get("filename", "").strip()
        expires = request.POST.get("expires", "").strip()
        response_format = request.POST.get("format", "default").strip()

        if not content.strip():
            return HttpResponseBadRequest("No content given")

        # We need at least a lexer or a filename
        if not lexer and not filename:
            return HttpResponseBadRequest(
                "No lexer or filename given. Unable to "
                "determine a highlight. Valid lexers are: %s"
                % ", ".join(highlight.LEXER_KEYS)
            )

        # A lexer is given, check if its valid at all
        if lexer and lexer not in highlight.LEXER_KEYS:
            return HttpResponseBadRequest(
                'Invalid lexer "%s" given. Valid lexers are: %s'
                % (lexer, ", ".join(highlight.LEXER_KEYS))
            )

        # No lexer is given, but we have a filename, try to get the lexer
        #  out of it. In case Pygments cannot determine the lexer of the
        # filename, we fallback to 'plain' code.
        if not lexer and filename:
            try:
                lexer_cls = get_lexer_for_filename(filename)
                lexer = lexer_cls.aliases[0]
            except (ClassNotFound, IndexError):
                lexer = config.PLAIN_CODE_SYMBOL

        if expires:
            expire_options = [str(i) for i in dict(config.EXPIRE_CHOICES)]
            if expires not in expire_options:
                return HttpResponseBadRequest(
                    'Invalid expire choice "{}" given. Valid values are: {}'.format(
                        expires, ", ".join(expire_options)
                    )
                )
            expires, expire_type = get_expire_values(expires)
        else:
            expires = datetime.datetime.now() + datetime.timedelta(seconds=60 * 60 * 24)
            expire_type = Snippet.EXPIRE_TIME

        snippet = Snippet.objects.create(
            content=content,
            lexer=lexer,
            expires=expires,
            expire_type=expire_type,
        )

        # Custom formatter for the API response
        formatter = getattr(self, f"_format_{response_format}", None)
        if callable(formatter):
            return HttpResponse(formatter(snippet))

        # Otherwise use the default one.
        return HttpResponse(self._format_default(snippet))


# -----------------------------------------------------------------------------
# Custom 404 and 500 views. Its easier to integrate this as a app if we
# handle them here.
# -----------------------------------------------------------------------------


def handler404(request, exception=None, template_name="dpaste/404.html"):
    context = {}
    context.update(config.extra_template_context)
    response = render(request, template_name, context, status=404)
    patch_cache_control(response, max_age=config.CACHE_TIMEOUT)
    return response


def handler500(request, template_name="dpaste/500.html"):
    context = {}
    context.update(config.extra_template_context)
    response = render(request, template_name, context, status=500)
    add_never_cache_headers(response)
    return response
