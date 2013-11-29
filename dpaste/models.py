import datetime
import random
import mptt

from django.db import models
from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from dpaste.highlight import LEXER_DEFAULT

L = getattr(settings, 'DPASTE_SLUG_LENGTH', 4)
T = getattr(settings, 'DPASTE_SLUG_CHOICES',
    'abcdefghijkmnopqrstuvwwxyzABCDEFGHIJKLOMNOPQRSTUVWXYZ1234567890')

def generate_secret_id(length=L):
    return ''.join([random.choice(T) for i in range(length)])

class Snippet(models.Model):
    secret_id = models.CharField(_(u'Secret ID'), max_length=255, blank=True)
    content = models.TextField(_(u'Content'), )
    lexer = models.CharField(_(u'Lexer'), max_length=30, default=LEXER_DEFAULT)
    published = models.DateTimeField(_(u'Published'), blank=True)
    expires = models.DateTimeField(_(u'Expires'), blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children')

    class Meta:
        ordering = ('-published',)
        db_table = 'dpaste_snippet'

    def get_linecount(self):
        return len(self.content.splitlines())

    def content_splitted(self):
        return self.content.splitlines()

    @property
    def is_single(self):
        return self.is_root_node() and not self.get_children()

    def save(self, *args, **kwargs):
        if not self.pk:
            self.published = datetime.datetime.now()
            self.secret_id = generate_secret_id()
        super(Snippet, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('snippet_details', kwargs={'snippet_id': self.secret_id})

    def __unicode__(self):
        return self.secret_id

mptt.register(Snippet, order_insertion_by=['content'])
