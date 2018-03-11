from django.template import Library

from ..highlight import pygmentize

register = Library()

@register.filter
def in_list(value, arg):
    return value in arg

@register.filter
def highlight(snippet):
    h = pygmentize(snippet.content, snippet.lexer)
    h = h.replace(u'\t', '&nbsp;&nbsp;&nbsp;&nbsp;')

    # see https://github.com/bartTC/dpaste/issues/88
    h = h.replace(u' ', u'&nbsp;')
    h = h.replace(u'<span&nbsp;class', u'<span class')

    return h.splitlines()
