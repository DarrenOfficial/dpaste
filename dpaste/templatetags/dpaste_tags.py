from __future__ import unicode_literals

import os
from logging import getLogger

from django.conf import settings
from django.contrib.staticfiles.finders import find
from django.template.defaulttags import register
from django.utils.safestring import mark_safe
from django.contrib.staticfiles.storage import staticfiles_storage

logger = getLogger(__file__)


@register.simple_tag()
def inlinestatic(path):
    """
    Similiar to Django's native `static` templatetag, but this includes
    the file directly in the template, rather than a link to it.

    Example:

        <style type="text/css">{% inlinestatic "dpaste.css" %}</style>
        <script>{% inlinestatic "dpaste.js" %}</script>

    Becomes:

        <style type="text/css">body{ color: red; }</style>
        <script>alert("Hello World");</script>

    Raises a ValueError if the the file does not exist, and
    DEBUG is enabled.

    :param path: (string) Filename of the file to include.
    :return: (string) The included File or an empty string `''` if the
        file was not found, and DEBUG is disabled.
    """
    # Filename in build/ directory (when in Watch mode)
    filename = find(path)

    # File in collectstatic target directory (regular deployment)
    if not filename:
        if staticfiles_storage.exists(path):
            filename = staticfiles_storage.path(path)

    # If it wasn't found, raise an error if in DEBUG mode.
    if not filename or not os.path.exists(filename):
        logger.error('Unable to include inline static file "%s", '
                     'file not found.', filename)
        if settings.DEBUG:
            raise ValueError('Unable to include inline static file "{0}", '
                             'file not found.'.format(filename))
        return ''

    return mark_safe(open(filename).read())

