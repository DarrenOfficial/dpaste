"""
List of all available lexers.

To get a list of all lexers, and remove some dupes, do:

from pygments.lexers import get_all_lexers
ALL_LEXER = set([(i[1][0], i[0]) for i in get_all_lexers()])
LEXER_LIST = [l for l in ALL_LEXER if not (
       '-' in l[0]
    or '+' in l[0]
    or '+' in l[1]
    or 'with' in l[1].lower()
    or ' ' in l[1]
    or l[0] in IGNORE_LEXER
)]
LEXER_LIST = sorted(LEXER_LIST)
"""


from __future__ import unicode_literals

from logging import getLogger

from django.conf import settings
from django.template.defaultfilters import escape
from django.utils.translation import ugettext_lazy as _
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.lexers.python import PythonLexer
from pygments.util import ClassNotFound

logger = getLogger(__file__)


PLAIN_TEXT = '_text' # lexer name whats rendered as text (paragraphs)
PLAIN_CODE = '_code' # lexer name of code with no hihglighting

LEXER_LIST = getattr(settings, 'DPASTE_LEXER_LIST', (
    (_('Text'), (
        (PLAIN_TEXT, 'Plain Text'),
        # ('_markdown', 'Markdown'),
        # ('_rst', 'reStructuredText'),
        # ('_textile', 'Textile'),
    )),
    (_('Code'), (
        (PLAIN_CODE, 'Plain Code'),
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
    ))
))

# Generate a list of all keys of all lexer
LEXER_KEYS = []
for i in LEXER_LIST:
    for j, k in i[1]:
        LEXER_KEYS.append(j)

# The default lexer is python
LEXER_DEFAULT = getattr(settings, 'DPASTE_LEXER_DEFAULT', 'python')

# Lexers which have wordwrap enabled by default
LEXER_WORDWRAP = getattr(settings, 'DPASTE_LEXER_WORDWRAP', 
    ('_text', 'rst')
)


class NakedHtmlFormatter(HtmlFormatter):
    def wrap(self, source, outfile):
        return self._wrap_code(source)

    def _wrap_code(self, source):
        for i, t in source:
            yield i, t


def pygmentize(code_string, lexer_name=LEXER_DEFAULT):
    """
    Run given code in ``code string`` through pygments.
    """

    # Plain code is not highlighted, but we wrap with with regular
    # Pygments syntax to keep the frontend aligned.
    if lexer_name == PLAIN_CODE:
        return '\n'.join(['<span class="plain">{}</span>'.format(escape(l) or '&#8203;')
            for l in code_string.splitlines()])

    # Everything else is handled by Pygments.
    lexer = None
    try:
        lexer = get_lexer_by_name(lexer_name)
    except ClassNotFound as e:
        if settings.DEBUG:
            logger.warning('Lexer for given name %s not found', lexer_name)
            logger.exception(e)
        pass

    # If yet no lexer is defined, fallback to Python
    if not lexer:
        lexer = PythonLexer()

    formatter = NakedHtmlFormatter()

    return highlight(code_string, lexer, formatter)

