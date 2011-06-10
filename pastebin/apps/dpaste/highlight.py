from pygments.lexers import get_all_lexers, get_lexer_by_name, guess_lexer, PythonLexer
from pygments.formatters import HtmlFormatter
from pygments import highlight

from django.utils.html import escape

import logging
logger = logging.getLogger(__name__)

LEXER_LIST_ALL = sorted([(i[1][0], i[0]) for i in get_all_lexers()])
LEXER_LIST = (
    ('bash', 'Bash'),
    ('c', 'C'),
    ('css', 'CSS'),
    ('diff', 'Diff'),
    ('django', 'Django/Jinja'),
    ('html', 'HTML'),
    ('irc', 'IRC logs'),
    ('js', 'JavaScript'),
    ('php', 'PHP'),
    ('pycon', 'Python console session'),
    ('pytb', 'Python Traceback'),
    ('python', 'Python'),
    ('python3', 'Python 3'),
    ('rst', 'Restructured Text'),
    ('sql', 'SQL'),
    ('text', 'Text only'),
)
LEXER_DEFAULT = 'python'


class NakedHtmlFormatter(HtmlFormatter):
    def wrap(self, source, outfile):
        return self._wrap_code(source)
    def _wrap_code(self, source):
        for i, t in source:
            yield i, t

def pygmentize(code_string, lexer_name=LEXER_DEFAULT):
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
