from pygments import highlight
from pygments.lexers import *
from pygments.lexers import get_all_lexers
from pygments.formatters import HtmlFormatter

from django.utils.html import escape

import logging
logger = logging.getLogger(__name__)

# Python 3: python3
LEXER_LIST = sorted([(i[0], i[0]) for i in get_all_lexers() if not (
    '+' in i[0] or
    'with' in i[0].lower() or
    i[0].islower()
)])
LEXER_LIST_NAME = dict([(i[0], i[1][0]) for i in get_all_lexers()])

LEXER_DEFAULT = 'Python'
LEXER_WORDWRAP = ('text', 'rst')

class NakedHtmlFormatter(HtmlFormatter):
    def wrap(self, source, outfile):
        return self._wrap_code(source)

    def _wrap_code(self, source):
        for i, t in source:
            yield i, t

def pygmentize(code_string, lexer_name=LEXER_DEFAULT):
    lexer_name = LEXER_LIST_NAME.get(lexer_name, None)
    try:
        if lexer_name:
            lexer = get_lexer_by_name(lexer_name)
        else:
            raise Exception
    except:
        try:
            lexer = guess_lexer(code_string)
        except:
            lexer = PythonLexer()

    try:
        return highlight(code_string, lexer, NakedHtmlFormatter())
    except:
        return escape(code_string)

def guess_code_lexer(code_string, default_lexer='unknown'):
    try:
        return guess_lexer(code_string).name
    except ValueError:
        return default_lexer
