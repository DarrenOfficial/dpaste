from django.template import Library
from dpaste.highlight import pygmentize

register = Library()

@register.filter
def in_list(value, arg):
    return value in arg

@register.filter
def highlight(snippet):
    h = pygmentize(snippet.content, snippet.lexer)
    h = h.replace(u'  ', u' &nbsp;')
    return h.splitlines()
