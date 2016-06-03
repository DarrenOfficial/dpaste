from django.conf import settings
from django.template.defaultfilters import escape
from django.utils.translation import ugettext_lazy as _
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import *

"""
# Get a list of all lexer, and then remove all lexer which have '-' or '+'
# or 'with' in the name. Those are too specific and never used. This produces a
# tuple list of [(lexer, Lexer Display Name) ...] lexers.
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

# The list of lexers. Its not worth to autogenerate this. See above how to
# retrieve this.
PLAIN_TEXT = 'text'  # lexer name whats rendered as text (paragraphs)
PLAIN_CODE = 'plain' # lexer name of code with no hihglighting

LEXER_LIST = getattr(settings, 'DPASTE_LEXER_LIST', (
    (PLAIN_TEXT, 'Text'),
    (PLAIN_CODE, 'Code'),
    (_('Highlighted'), (
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

LEXER_KEYS = [PLAIN_TEXT, PLAIN_CODE] + [i for i in dict(LEXER_LIST[2][1]).keys()]

# The default lexer is python
LEXER_DEFAULT = getattr(settings, 'DPASTE_LEXER_DEFAULT', 'python')

# Lexers which have wordwrap enabled by default
LEXER_WORDWRAP = getattr(settings, 'DPASTE_LEXER_WORDWRAP', ('text', 'rst'))

class NakedHtmlFormatter(HtmlFormatter):
    def wrap(self, source, outfile):
        return self._wrap_code(source)

    def _wrap_code(self, source):
        for i, t in source:
            yield i, t

def pygmentize(code_string, lexer_name=LEXER_DEFAULT):
    # Plain code is noth hihglighted
    if lexer_name == PLAIN_CODE:
        return '\n'.join([u'<span class="nn">{}</span>'.format(escape(l))
            for l in code_string.splitlines()])

    try:
        lexer = lexer_name and get_lexer_by_name(lexer_name) \
                            or PythonLexer()
    except Exception:
        lexer = PythonLexer()
    return highlight(code_string, lexer, NakedHtmlFormatter())
