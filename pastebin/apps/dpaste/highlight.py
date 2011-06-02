from pygments.lexers import get_all_lexers, get_lexer_by_name, guess_lexer, PythonLexer
from pygments.styles import get_all_styles
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound
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

def pygmentize(code_string, lexer_name='text'):
    try:
        lexer = get_lexer_by_name(lexer_name)
    except (TypeError, ClassNotFound):
        logger.warning('Could not find lexer for name "%s"' %  lexer_name)
        lexer = PythonLexer()

    try:
        return highlight(code_string, lexer, NakedHtmlFormatter())
    except TypeError:
        logger.warning('Could not highlight code with lexer "%s"' %  lexer_name)
        return escape(code_string)

def guess_code_lexer(code_string, default_lexer='unknown'):
    try:
        return guess_lexer(code_string).name
    except ClassNotFound:
        return default_lexer
