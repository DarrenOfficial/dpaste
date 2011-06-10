import datetime
import difflib
import random
import mptt
import re
from django.db import models
from django.core.urlresolvers import reverse
from django.db.models import permalink
from django.utils.translation import ugettext_lazy as _
from pastebin.apps.dpaste.highlight import LEXER_DEFAULT, pygmentize

t = 'abcdefghijkmnopqrstuvwwxyzABCDEFGHIJKLOMNOPQRSTUVWXYZ1234567890'
def generate_secret_id(length=3):
    return ''.join([random.choice(t) for i in range(length)])

class Snippet(models.Model):
    secret_id = models.CharField(_(u'Secret ID'), max_length=4, blank=True)
    title = models.CharField(_(u'Title'), max_length=120, blank=True)
    author = models.CharField(_(u'Author'), max_length=30, blank=True)
    content = models.TextField(_(u'Content'), )
    content_highlighted = models.TextField(_(u'Highlighted Content'), blank=True)
    lexer = models.CharField(_(u'Lexer'), max_length=30, default=LEXER_DEFAULT)
    published = models.DateTimeField(_(u'Published'), blank=True)
    expires = models.DateTimeField(_(u'Expires'), blank=True, help_text='asdf')
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children')

    class Meta:
        ordering = ('-published',)

    def get_linecount(self):
        return len(self.content.splitlines())

    def content_splitted(self):
        return self.content_highlighted.splitlines()

    def save(self, *args, **kwargs):
        if not self.pk:
            self.published = datetime.datetime.now()
            self.secret_id = generate_secret_id()
        if self.content and self.lexer:
            self.content_highlighted = pygmentize(self.content, self.lexer)
        super(Snippet, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('snippet_details', kwargs={'snippet_id': self.secret_id})

    def __unicode__(self):
        return '%s' % self.secret_id

mptt.register(Snippet, order_insertion_by=['content'])


class SpamwordManager(models.Manager):
    def get_regex(self):
        return re.compile(r'|'.join((i[1] for i in self.values_list())),
            re.MULTILINE)

class Spamword(models.Model):
    word = models.CharField(max_length=100)
    objects = SpamwordManager()

    def __unicode__(self):
        return self.word
