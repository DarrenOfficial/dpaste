import datetime

from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from dpaste.models import Snippet
from dpaste.highlight import LEXER_LIST, LEXER_DEFAULT

EXPIRE_CHOICES = (
    (3600, _(u'In one hour')),
    (3600 * 24 * 7, _(u'In one week')),
    (3600 * 24 * 30, _(u'In one month')),
)
EXPIRE_DEFAULT = EXPIRE_CHOICES[2][0]
MAX_CONTENT_LENGTH = getattr(settings, 'DPASTE_MAX_CONTENT_LENGTH', 250*1024*1024)
MAX_SNIPPETS_PER_USER = getattr(settings, 'DPASTE_MAX_SNIPPETS_PER_USER', 15)


class SnippetForm(forms.ModelForm):
    content = forms.CharField(
        label=_('Content'),
        widget=forms.Textarea(attrs={'placeholder': _('Awesome code goes here...')}),
        max_length=MAX_CONTENT_LENGTH,
    )

    lexer = forms.ChoiceField(
        label=_(u'Lexer'),
        initial=LEXER_DEFAULT,
        choices=LEXER_LIST,
    )

    expire_options = forms.ChoiceField(
        label=_(u'Expires'),
        choices=EXPIRE_CHOICES,
        initial=EXPIRE_DEFAULT,
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
        if session_lexer and session_lexer in dict(LEXER_LIST).keys():
            self.fields['lexer'].initial = session_lexer

        # if the lexer is given via GET, set it
        if 'l' in request.GET and request.GET['l'] in dict(LEXER_LIST).keys():
            self.fields['lexer'].initial = request.GET['l']


    def clean_content(self):
        return self.cleaned_data.get('content', '').strip()

    def clean(self):
        # The `title` field is a hidden honeypot field. If its filled,
        # this is likely spam.
        if self.cleaned_data.get('title'):
            raise forms.ValidationError('This snippet was identified as Spam.')
        return self.cleaned_data

    def save(self, parent=None, *args, **kwargs):
        # Set parent snippet
        if parent:
            self.instance.parent = parent

        # Add expire datestamp
        self.instance.expires = datetime.datetime.now() + \
            datetime.timedelta(seconds=int(self.cleaned_data['expire_options']))

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
