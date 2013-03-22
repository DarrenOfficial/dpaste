from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from dpaste.models import Snippet
from dpaste.highlight import LEXER_LIST, LEXER_DEFAULT
import datetime

#===============================================================================
# Snippet Form and Handling
#===============================================================================

EXPIRE_CHOICES = (
    (3600, _(u'In one hour')),
    (3600 * 24 * 7, _(u'In one week')),
    (3600 * 24 * 30, _(u'In one month')),
)

EXPIRE_DEFAULT = 3600 * 24 * 30

MAX_CONTENT_LENGTH = 250*1024*1024

class SnippetForm(forms.ModelForm):
    content = forms.CharField(
        label=_('Content'),
        widget=forms.Textarea(attrs={'placeholder': _('Awesome code goes here...')}),
        max_length=MAX_CONTENT_LENGTH,
    )

    lexer = forms.ChoiceField(
        label=_(u'Lexer'),
        initial=LEXER_DEFAULT,
        widget=forms.TextInput,
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

    def __init__(self, request, *args, **kwargs):
        super(SnippetForm, self).__init__(*args, **kwargs)
        self.request = request
        self.fields['lexer'].choices = LEXER_LIST
        self.fields['lexer'].widget.attrs = {
            'autocomplete': 'off',
            'data-provide': 'typeahead',
            'data-source': '["%s"]' % '","'.join(dict(LEXER_LIST).keys())
        }

        # Set the recently used lexer if we have any
        session_lexer = self.request.session.get('lexer')
        if session_lexer and session_lexer in dict(LEXER_LIST).keys():
            self.fields['lexer'].initial = session_lexer

    def clean_lexer(self):
        lexer = self.cleaned_data.get('lexer')
        if not lexer:
            return LEXER_DEFAULT
        lexer = dict(LEXER_LIST).get(lexer, LEXER_DEFAULT)
        return lexer

    def clean(self):
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
            if len(self.request.session['snippet_list']) >= getattr(settings, 'MAX_SNIPPETS_PER_USER', 10):
                self.request.session['snippet_list'].pop(0)
            self.request.session['snippet_list'] += [self.instance.pk]
        else:
            self.request.session['snippet_list'] = [self.instance.pk]

        # Save the lexer in the session so we can use it later again
        self.request.session['lexer'] = self.cleaned_data['lexer']

        return self.request, self.instance

    class Meta:
        model = Snippet
        fields = (
            'content',
            'lexer',
        )
