from pygments import highlight
from pygments.lexers import *
from pygments.formatters import HtmlFormatter

from dpaste.conf import settings

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
LEXER_LIST = settings.DPASTE_LEXER_LIST

LEXER_KEYS = dict(LEXER_LIST).keys()

# The default lexer is python
LEXER_DEFAULT = settings.DPASTE_LEXER_DEFAULT

# Lexers which have wordwrap enabled by default
LEXER_WORDWRAP = settings.DPASTE_LEXER_WORDWRAP


class NakedHtmlFormatter(HtmlFormatter):
    def wrap(self, source, outfile):
        return self._wrap_code(source)

    def _wrap_code(self, source):
        for i, t in source:
            yield i, t

def pygmentize(code_string, lexer_name=LEXER_DEFAULT):
    try:
        lexer = lexer_name and get_lexer_by_name(lexer_name) \
                            or PythonLexer()
    except Exception:
        lexer = PythonLexer()
    return highlight(code_string, lexer, NakedHtmlFormatter())
