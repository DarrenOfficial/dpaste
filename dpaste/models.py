from random import SystemRandom

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .highlight import LEXER_DEFAULT

R = SystemRandom()
ONETIME_LIMIT = getattr(settings, 'DPASTE_ONETIME_LIMIT', 2)

def generate_secret_id(length=None, alphabet=None, tries=0):
    length = length or getattr(settings, 'DPASTE_SLUG_LENGTH', 4)
    alphabet = alphabet or getattr(settings, 'DPASTE_SLUG_CHOICES',
        'abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNOPQRSTUVWXYZ1234567890')
    secret_id = ''.join([R.choice(alphabet) for i in range(length)])

    # Check if this slug already exists, if not, return this new slug
    try:
        Snippet.objects.get(secret_id=secret_id)
    except Snippet.DoesNotExist:
        return secret_id

    # Otherwise create a new slug which is +1 character longer than the
    # regular one.
    return generate_secret_id(length=length+1, tries=tries)

class Snippet(models.Model):
    EXPIRE_TIME = 1
    EXPIRE_KEEP = 2
    EXPIRE_ONETIME = 3
    EXPIRE_CHOICES = (
        (EXPIRE_TIME, _(u'Expire by timestamp')),
        (EXPIRE_KEEP, _(u'Keep Forever')),
        (EXPIRE_ONETIME, _(u'One-Time snippet')),
    )

    secret_id = models.CharField(_(u'Secret ID'), max_length=255, blank=True, null=True,
        unique=True)
    content = models.TextField(_(u'Content'))
    lexer = models.CharField(_(u'Lexer'), max_length=30, default=LEXER_DEFAULT)
    published = models.DateTimeField(_(u'Published'), auto_now_add=True)
    expire_type = models.PositiveSmallIntegerField(_(u'Expire Type'),
        choices=EXPIRE_CHOICES, default=EXPIRE_CHOICES[0][0])
    expires = models.DateTimeField(_(u'Expires'), blank=True, null=True)
    view_count = models.PositiveIntegerField(_('View count'), default=0)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children')

    class Meta:
        ordering = ('-published',)
        db_table = 'dpaste_snippet'

    def get_linecount(self):
        return len(self.content.splitlines())

    @property
    def remaining_views(self):
        if self.expire_type == self.EXPIRE_ONETIME:
            remaining = ONETIME_LIMIT - self.view_count
            return remaining > 0 and remaining or 0
        return None

    def save(self, *args, **kwargs):
        if not self.secret_id:
            self.secret_id = generate_secret_id()
        super(Snippet, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('snippet_details', kwargs={'snippet_id': self.secret_id})

    def __unicode__(self):
        return self.secret_id
