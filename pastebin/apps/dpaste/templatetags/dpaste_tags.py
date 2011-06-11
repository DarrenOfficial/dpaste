from django.template import Library
from django.utils.safestring import mark_safe

from pastebin.apps.dpaste.highlight import pygmentize

register = Library()

@register.filter
def in_list(value,arg):
    return value in arg

@register.filter
def highlight(snippet):
    h = pygmentize(snippet.content, snippet.lexer)
    if not h:
        return snippet.content.splitlines()
    return h.splitlines()