from __future__ import unicode_literals

from logging import getLogger

from django.conf import settings
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


class NakedHtmlFormatter(HtmlFormatter):
    """Pygments HTML formatter with no further HTML tags."""
    def wrap(self, source, outfile):
        return self._wrap_code(source)

    def _wrap_code(self, source):
        for i, t in source:
            yield i, t


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
        for l in TEXT_FORMATTER + CODE_FORMATTER:
            if l[0] == lexer_name:
                return l[1]
        return fallback

    def render(self, code_string, lexer_name, **kwargs):
        highlighted_string = self.highlight(code_string, lexer_name)
        context = {
            'highlighted': highlighted_string,
            'highlighted_splitted': highlighted_string.splitlines(),
            'lexer_name': lexer_name,
            'lexer_display_name': self.get_lexer_display_name(lexer_name),
        }
        context.update(kwargs)
        return render_to_string(self.template_name, context)


class PlainTextHighlighter(Highlighter):
    """Plain Text. Just replace linebreaks."""
    template_name = 'dpaste/highlight/text.html'

    def highlight(self, code_string, lexer_name=None):
        return linebreaksbr(code_string)



class MarkdownHighlighter(PlainTextHighlighter):
    """Markdown"""
    extensions = ('tables', 'fenced-code', 'footnotes', 'autolink,',
                  'strikethrough', 'underline', 'quote', 'superscript',
                  'math')
    render_flags = ('skip-html',)

    def highlight(self, code_string, lexer_name=None):
        import misaka
        return mark_safe(misaka.html(code_string,
                                     extensions=self.extensions,
                                     render_flags=self.render_flags))


class RestructuredTextHighlighter(PlainTextHighlighter):
    """Restructured Text"""
    rst_part_name = 'html_body'
    publish_args = {
        'writer_name': 'html5_polyglot',
        'settings_overrides': {
            'raw_enabled': False,
            'file_insertion_enabled': False,
            'report_level': 3,
            'warning_stream': '/dev/null',
        }
    }

    def highlight(self, code_string, lexer_name=None):
        from docutils.core import publish_parts
        self.publish_args['source'] = code_string
        parts = publish_parts(**self.publish_args)
        return mark_safe(parts[self.rst_part_name])


# -----------------------------------------------------------------------------


class PlainCodeHighlighter(Highlighter):
    """Plain Code. No highlighting but Pygments like span tags around each line."""

    def highlight(self, code_string, lexer_name=None):
        return '\n'.join(['<span class="plain">{}</span>'.format(escape(l) or '&#8203;')
            for l in code_string.splitlines()])


class PygmentsHighlighter(Highlighter):
    """
    Highlight code string with Pygments. The lexer is automaticially
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
    for c in TEXT_FORMATTER + CODE_FORMATTER:
        if c[0] == lexer_name:
            if len(c) == 3:
                return c[2]
            return PygmentsHighlighter
    return PlainCodeHighlighter


# -----------------------------------------------------------------------------
# Lexer List
# -----------------------------------------------------------------------------

# Lexer list. Each list contains a lexer tuple of:
#
#   (Lexer key,
#    Lexer Display Name,
#    Lexer Highlight Class)
#
# If the Highlight Class is not given, PygmentsHighlighter is used.

# Default Highlight Types
PLAIN_TEXT = '_text' # lexer name whats rendered as text (paragraphs)
PLAIN_CODE = '_code' # lexer name of code with no hihglighting

TEXT_FORMATTER = [
    (PLAIN_TEXT, 'Plain Text',  PlainTextHighlighter),
    ('_markdown', 'Markdown', MarkdownHighlighter),
    ('_rst', 'reStructuredText', RestructuredTextHighlighter),
    #('_textile', 'Textile', MarkdownHighlighter),
]

CODE_FORMATTER = [
    (PLAIN_CODE, 'Plain Code', PlainCodeHighlighter),
    ('abap', 'ABAP'),
    ('apacheconf', 'ApacheConf'),
    ('applescript', 'AppleScript'),
    ('as', 'ActionScript'),
    ('bash', 'Bash'),
    ('bbcode', 'BBCode'),
    ('c', 'C'),
    ('cpp', 'C++'),
    ('clojure', 'Clojure'),
    ('cobol', 'COBOL'),
    ('css', 'CSS'),
    ('cuda', 'CUDA'),
    ('dart', 'Dart'),
    ('delphi', 'Delphi'),
    ('diff', 'Diff'),
    ('django', 'Django'),
    ('erlang', 'Erlang'),
    ('fortran', 'Fortran'),
    ('go', 'Go'),
    ('groovy', 'Groovy'),
    ('haml', 'Haml'),
    ('haskell', 'Haskell'),
    ('html', 'HTML'),
    ('http', 'HTTP'),
    ('ini', 'INI'),
    ('irc', 'IRC'),
    ('java', 'Java'),
    ('js', 'JavaScript'),
    ('json', 'JSON'),
    ('lua', 'Lua'),
    ('make', 'Makefile'),
    ('mako', 'Mako'),
    ('mason', 'Mason'),
    ('matlab', 'Matlab'),
    ('modula2', 'Modula'),
    ('monkey', 'Monkey'),
    ('mysql', 'MySQL'),
    ('numpy', 'NumPy'),
    ('objc', 'Obj-C'),
    ('ocaml', 'OCaml'),
    ('perl', 'Perl'),
    ('php', 'PHP'),
    ('postscript', 'PostScript'),
    ('powershell', 'PowerShell'),
    ('prolog', 'Prolog'),
    ('properties', 'Properties'),
    ('puppet', 'Puppet'),
    ('python', 'Python'),
    ('r', 'R'),
    ('rb', 'Ruby'),
    ('rst', 'reStructuredText'),
    ('rust', 'Rust'),
    ('sass', 'Sass'),
    ('scala', 'Scala'),
    ('scheme', 'Scheme'),
    ('scilab', 'Scilab'),
    ('scss', 'SCSS'),
    ('smalltalk', 'Smalltalk'),
    ('smarty', 'Smarty'),
    ('solidity', 'Solidity', SolidityHighlighter),
    ('sql', 'SQL'),
    ('tcl', 'Tcl'),
    ('tcsh', 'Tcsh'),
    ('tex', 'TeX'),
    ('text', 'Text'),
    ('vb.net', 'VB.net'),
    ('vim', 'VimL'),
    ('xml', 'XML'),
    ('xquery', 'XQuery'),
    ('xslt', 'XSLT'),
    ('yaml', 'YAML'),
]

# Generat a list of Form choices of all lexer.
LEXER_CHOICES = (
    (_('Text'), [i[:2] for i in TEXT_FORMATTER]),
    (_('Code'), [i[:2] for i in CODE_FORMATTER])
)

# List of all Lexer Keys
LEXER_KEYS = [i[0] for i in TEXT_FORMATTER] + [i[0] for i in CODE_FORMATTER]

# The default lexer which we fallback in case of
# an error or if not supplied in an API call.
LEXER_DEFAULT = getattr(settings, 'DPASTE_LEXER_DEFAULT', 'python')

# Lexers which have wordwrap enabled by default
LEXER_WORDWRAP = getattr(settings, 'DPASTE_LEXER_WORDWRAP',
    ('rst',)
)
