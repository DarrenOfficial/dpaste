from django.template import Library
from dpaste.highlight import pygmentize

register = Library()

@register.filter
def in_list(value, arg):
    return value in arg

@register.filter
def highlight(snippet, maxlines=None):
    h = pygmentize(snippet.content, snippet.lexer)
    if not h:
        s = snippet.content.splitlines()
    s = h.splitlines()

    if maxlines:
        return s[:maxlines]
    return s