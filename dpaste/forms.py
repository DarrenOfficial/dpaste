import datetime

from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from .highlight import LEXER_DEFAULT, LEXER_KEYS, LEXER_LIST
from .models import Snippet

EXPIRE_CHOICES = getattr(settings, 'DPASTE_EXPIRE_CHOICES', (
    ('onetime', _(u'One-Time snippet')),
    (3600, _(u'In one hour')),
    (3600 * 24 * 7, _(u'In one week')),
    (3600 * 24 * 30, _(u'In one month')),
    ('never', _(u'Never')),
))
EXPIRE_DEFAULT = getattr(settings, 'DPASTE_EXPIRE_DEFAULT', 3600)
MAX_CONTENT_LENGTH = getattr(settings, 'DPASTE_MAX_CONTENT_LENGTH', 250*1024*1024)

def get_expire_values(expires):
    if expires == u'never':
        expire_type = Snippet.EXPIRE_KEEP
        expires = None
    elif expires == u'onetime':
        expire_type = Snippet.EXPIRE_ONETIME
        expires = None
    else:
        expire_type = Snippet.EXPIRE_TIME
        expires = expires and expires or EXPIRE_DEFAULT
        expires = datetime.datetime.now() + datetime.timedelta(seconds=int(expires))
    return expires, expire_type


class SnippetForm(forms.ModelForm):
    content = forms.CharField(
        label=_('Content'),
        widget=forms.Textarea(attrs={'placeholder': _('Awesome code goes here...'), 'class': 'form-control'}),
        max_length=MAX_CONTENT_LENGTH,
    )

    lexer = forms.ChoiceField(
        label=_(u'Lexer'),
        initial=LEXER_DEFAULT,
        choices=LEXER_LIST,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    expires = forms.ChoiceField(
        label=_(u'Expires'),
        choices=EXPIRE_CHOICES,
        initial=EXPIRE_DEFAULT,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    # Honeypot field
    title = forms.CharField(
        label=_(u'Title'),
        required=False,
        widget=forms.TextInput(attrs={'autocomplete': 'off'}),
    )

    class Meta:
        model = Snippet
        fields = (
            'content',
            'lexer',
        )

    def __init__(self, request, *args, **kwargs):
        super(SnippetForm, self).__init__(*args, **kwargs)
        self.request = request

        # Set the recently used lexer if we have any
        session_lexer = self.request.session.get('lexer')
        if session_lexer and session_lexer in LEXER_KEYS:
            self.fields['lexer'].initial = session_lexer

        # if the lexer is given via GET, set it
        if 'l' in request.GET and request.GET['l'] in LEXER_KEYS:
            self.fields['lexer'].initial = request.GET['l']

    def clean_content(self):
        content = self.cleaned_data.get('content', '')
        if content.strip() == '':
            raise forms.ValidationError(_('This field is required.'))
        return content

    def clean_expires(self):
        """
        Extract the 'expire_type' from the choice of expire choices.
        """
        expires = self.cleaned_data['expires']
        expires, expire_type = get_expire_values(expires)
        self.cleaned_data['expire_type'] = expire_type
        return expires

    def clean(self):
        """
        The `title` field is a hidden honeypot field. If its filled,
        this is likely spam.
        """
        if self.cleaned_data.get('title'):
            raise forms.ValidationError('This snippet was identified as Spam.')
        return self.cleaned_data

    def save(self, parent=None, *args, **kwargs):
        MAX_SNIPPETS_PER_USER = getattr(settings, 'DPASTE_MAX_SNIPPETS_PER_USER', 10)

        # Set parent snippet
        self.instance.parent = parent

        # Add expire datestamp. None indicates 'keep forever', use the default
        # null state of the db column for that.
        self.instance.expires = self.cleaned_data['expires']
        self.instance.expire_type = self.cleaned_data['expire_type']

        # Save snippet in the db
        super(SnippetForm, self).save(*args, **kwargs)

        # Add the snippet to the user session list
        if self.request.session.get('snippet_list', False):
            if len(self.request.session['snippet_list']) >= MAX_SNIPPETS_PER_USER:
                self.request.session['snippet_list'].pop(0)
            self.request.session['snippet_list'] += [self.instance.pk]
        else:
            self.request.session['snippet_list'] = [self.instance.pk]

        # Save the lexer in the session so we can use it later again
        self.request.session['lexer'] = self.cleaned_data['lexer']

        return self.instance
