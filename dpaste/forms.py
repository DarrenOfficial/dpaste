import datetime

from django import forms
from django.utils.translation import ugettext_lazy as _

from dpaste.conf import settings
from dpaste.models import Snippet
from dpaste.highlight import LEXER_LIST, LEXER_DEFAULT, LEXER_KEYS


class SnippetForm(forms.ModelForm):
    content = forms.CharField(
        label=_('Content'),
        widget=forms.Textarea(attrs={'placeholder': _('Awesome code goes here...')}),
        max_length=settings.DPASTE_MAX_CONTENT_LENGTH,
    )

    lexer = forms.ChoiceField(
        label=_(u'Lexer'),
        initial=LEXER_DEFAULT,
        choices=LEXER_LIST,
    )

    expires = forms.ChoiceField(
        label=_(u'Expires'),
        choices=settings.DPASTE_EXPIRE_CHOICES,
        initial=settings.DPASTE_EXPIRE_DEFAULT,
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
            raise forms.ValidationError(_('Plesae fill out this field.'))
        return content

    def clean(self):
        # The `title` field is a hidden honeypot field. If its filled,
        # this is likely spam.
        if self.cleaned_data.get('title'):
            raise forms.ValidationError('This snippet was identified as Spam.')
        return self.cleaned_data

    def clean_expires(self):
        expires = self.cleaned_data['expires']

        if expires == u'never':
            self.cleaned_data['expire_type'] = Snippet.EXPIRE_KEEP
            return None

        if expires == u'onetime':
            self.cleaned_data['expire_type'] = Snippet.EXPIRE_ONETIME
            return None

        self.cleaned_data['expire_type'] = Snippet.EXPIRE_TIME
        return expires

    def save(self, parent=None, *args, **kwargs):
        # Set parent snippet
        if parent:
            self.instance.parent = parent

        # Add expire datestamp. None indicates 'keep forever', use the default
        # null state of the db column for that.
        self.instance.expire_type = self.cleaned_data['expire_type']

        expires = self.cleaned_data['expires']
        if expires:
            self.instance.expires = datetime.datetime.now() + \
                datetime.timedelta(seconds=int(expires))

        # Save snippet in the db
        super(SnippetForm, self).save(*args, **kwargs)

        # Add the snippet to the user session list
        if self.request.session.get('snippet_list', False):
            if len(self.request.session['snippet_list']) >= settings.DPASTE_MAX_SNIPPETS_PER_USER:
                self.request.session['snippet_list'].pop(0)
            self.request.session['snippet_list'] += [self.instance.pk]
        else:
            self.request.session['snippet_list'] = [self.instance.pk]

        # Save the lexer in the session so we can use it later again
        self.request.session['lexer'] = self.cleaned_data['lexer']

        return self.instance
