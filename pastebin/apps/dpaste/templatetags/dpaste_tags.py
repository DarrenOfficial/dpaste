from django.template import Library

register = Library()

@register.filter
def in_list(value,arg):
    return value in arg
