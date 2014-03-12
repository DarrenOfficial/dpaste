"""Default settings for dpaste."""

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

import appconf
from . import enums


class DPasteConf(appconf.AppConf):
    class Meta:
        prefix = 'dpaste'

    BASE_URL = 'https://dpaste.de'

    # Expiry
    EXPIRE_CHOICES = (
        (enums.EXPIRE_ONETIME, _(u'One Time Snippet')),
        (enums.EXPIRE_ONE_HOUR, _(u'In one hour')),
        (enums.EXPIRE_ONE_WEEK, _(u'In one week')),
        (enums.EXPIRE_ONE_MONTH, _(u'In one month')),
        # ('never', _(u'Never')),
    )
    EXPIRE_DEFAULT = enums.EXPIRE_ONE_MONTH

    # Lexer
    LEXER_DEFAULT = 'python'
    LEXER_LIST = enums.DEFAULT_LEXER_LIST
    LEXER_WORDWRAP = ('text', 'rst')

    # Snippets
    SLUG_LENGTH = 4
    SLUG_CHOICES = 'abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNOPQRSTUVWXYZ1234567890'
    MAX_CONTENT_LENGTH = 250 * 1024 * 1024

    # Users
    MAX_SNIPPETS_PER_USER = 15
    ONETIME_LIMIT = 2
