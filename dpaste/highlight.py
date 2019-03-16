from logging import getLogger

from django.apps import apps
from django.template.defaultfilters import escape, linebreaksbr
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.lexers.python import PythonLexer
from pygments.util import ClassNotFound

logger = getLogger(__file__)
config = apps.get_app_config('dpaste')


# -----------------------------------------------------------------------------
# Highlight Code Snippets
# -----------------------------------------------------------------------------


class Highlighter(object):
    template_name = 'dpaste/highlight/code.html'

    def highlight(self, code_string, lexer_name=None):
        """Subclasses need to override this."""
        return code_string

    @staticmethod
    def get_lexer_display_name(lexer_name, fallback=_('(Deprecated Lexer)')):
        for l in config.TEXT_FORMATTER + config.CODE_FORMATTER:
            if l[0] == lexer_name:
                return l[1]
        return fallback

    def render(self, code_string, lexer_name, direction=None, **kwargs):
        highlighted_string = self.highlight(code_string, lexer_name=lexer_name)
        context = {
            'highlighted': highlighted_string,
            'highlighted_splitted': highlighted_string.splitlines(),
            'lexer_name': lexer_name,
            'lexer_display_name': self.get_lexer_display_name(lexer_name),
            'direction': direction,
        }
        context.update(kwargs)
        return render_to_string(self.template_name, context)


class PlainTextHighlighter(Highlighter):
    """Plain Text. Just replace linebreaks."""

    template_name = 'dpaste/highlight/text.html'

    def highlight(self, code_string, **kwargs):
        return linebreaksbr(code_string)


class MarkdownHighlighter(PlainTextHighlighter):
    """Markdown"""

    extensions = (
        'tables',
        'fenced-code',
        'footnotes',
        'autolink,',
        'strikethrough',
        'underline',
        'quote',
        'superscript',
        'math',
    )
    render_flags = ('skip-html',)

    def highlight(self, code_string, **kwargs):
        import misaka

        return mark_safe(
            misaka.html(
                code_string,
                extensions=self.extensions,
                render_flags=self.render_flags,
            )
        )


class RestructuredTextHighlighter(PlainTextHighlighter):
    """Restructured Text"""

    rst_part_name = 'html_body'
    publish_args = {
        'writer_name': 'html5_polyglot',
        'settings_overrides': {
            'raw_enabled': False,
            'file_insertion_enabled': False,
            'halt_level': 5,
            'report_level': 2,
            'warning_stream': '/dev/null',
        },
    }

    def highlight(self, code_string, **kwargs):
        from docutils.core import publish_parts

        self.publish_args['source'] = code_string
        parts = publish_parts(**self.publish_args)
        return mark_safe(parts[self.rst_part_name])


# -----------------------------------------------------------------------------


class NakedHtmlFormatter(HtmlFormatter):
    """Pygments HTML formatter with no further HTML tags."""

    def wrap(self, source, outfile):
        return self._wrap_code(source)

    def _wrap_code(self, source):
        yield from source


class PlainCodeHighlighter(Highlighter):
    """
    Plain Code. No highlighting but Pygments like span tags around each line.
    """

    def highlight(self, code_string, **kwargs):
        return '\n'.join(
            [
                '<span class="plain">{}</span>'.format(escape(l) or '&#8203;')
                for l in code_string.splitlines()
            ]
        )


class PygmentsHighlighter(Highlighter):
    """
    Highlight code string with Pygments. The lexer is automatically
    determined by the lexer name.
    """

    formatter = NakedHtmlFormatter()
    lexer = None
    lexer_fallback = PythonLexer()

    def highlight(self, code_string, lexer_name):
        if not self.lexer:
            try:
                self.lexer = get_lexer_by_name(lexer_name)
            except ClassNotFound:
                logger.warning('Lexer for given name %s not found', lexer_name)
                self.lexer = self.lexer_fallback

        return highlight(code_string, self.lexer, self.formatter)


class SolidityHighlighter(PygmentsHighlighter):
    """Solidity Specific Highlighter. This uses a 3rd party Pygments  lexer."""

    def __init__(self):
        # SolidityLexer does not necessarily need to be installed
        # since its imported here and not used later.
        from pygments_lexer_solidity import SolidityLexer

        self.lexer = SolidityLexer()


def get_highlighter_class(lexer_name):
    """
    Get Highlighter for lexer name.

    If the found lexer tuple does not provide a Highlighter class,
    use the generic Pygments highlighter.

    If no suitable highlighter is found, return the generic
    PlainCode Highlighter.
    """
    for c in config.TEXT_FORMATTER + config.CODE_FORMATTER:
        if c[0] == lexer_name:
            if len(c) == 3:
                return c[2]
            return PygmentsHighlighter
    return PlainCodeHighlighter


# -----------------------------------------------------------------------------
# Lexer List
# -----------------------------------------------------------------------------

# Generate a list of Form choices of all lexer.
LEXER_CHOICES = (
    (_('Text'), [i[:2] for i in config.TEXT_FORMATTER]),
    (_('Code'), [i[:2] for i in config.CODE_FORMATTER]),
)

# List of all Lexer Keys
LEXER_KEYS = [i[0] for i in config.TEXT_FORMATTER] + [
    i[0] for i in config.CODE_FORMATTER
]

# The default lexer which we fallback in case of
# an error or if not supplied in an API call.
LEXER_DEFAULT = config.LEXER_DEFAULT

# Lexers which have wordwrap enabled by default
LEXER_WORDWRAP = config.LEXER_WORDWRAP
