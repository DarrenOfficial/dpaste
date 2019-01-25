import datetime

from django import forms
from django.apps import apps
from django.utils.translation import ugettext_lazy as _

from .highlight import LEXER_CHOICES, LEXER_DEFAULT, LEXER_KEYS
from .models import Snippet

config = apps.get_app_config('dpaste')


def get_expire_values(expires):
    if expires == 'never':
        expire_type = Snippet.EXPIRE_KEEP
        expires = None
    elif expires == 'onetime':
        expire_type = Snippet.EXPIRE_ONETIME
        expires = None
    else:
        expire_type = Snippet.EXPIRE_TIME
        expires = expires and expires or config.EXPIRE_DEFAULT
        expires = datetime.datetime.now() + datetime.timedelta(
            seconds=int(expires)
        )
    return expires, expire_type


class SnippetForm(forms.ModelForm):
    content = forms.CharField(
        label=_('Content'),
        widget=forms.Textarea(
            attrs={'placeholder': _('Awesome code goes here...')}
        ),
        max_length=config.MAX_CONTENT_LENGTH,
        strip=False,
    )

    lexer = forms.ChoiceField(
        label=_('Lexer'), initial=LEXER_DEFAULT, choices=LEXER_CHOICES
    )

    expires = forms.ChoiceField(
        label=_('Expires'),
        choices=config.EXPIRE_CHOICES,
        initial=config.EXPIRE_DEFAULT,
    )

    rtl = forms.BooleanField(label=_('Right to Left'), required=False)

    # Honeypot field
    title = forms.CharField(
        label=_('Title'),
        required=False,
        widget=forms.TextInput(attrs={'autocomplete': 'off'}),
    )

    class Meta:
        model = Snippet
        fields = ('content', 'lexer', 'rtl')

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
        if not content.strip():
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
        # Set parent snippet
        self.instance.parent = parent

        # Add expire timestamp. None indicates 'keep forever', use the default
        # null state of the db column for that.
        self.instance.expires = self.cleaned_data['expires']
        self.instance.expire_type = self.cleaned_data['expire_type']

        # Save snippet in the db
        super(SnippetForm, self).save(*args, **kwargs)

        # Add the snippet to the user session list
        self.request.session.setdefault('snippet_list', [])
        self.request.session['snippet_list'] += [self.instance.pk]

        # Save the lexer in the session so we can use it later again
        self.request.session['lexer'] = self.cleaned_data['lexer']

        return self.instance
