from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from dpaste.models import Snippet
from dpaste.highlight import LEXER_LIST_ALL, LEXER_LIST, LEXER_DEFAULT
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


class SnippetForm(forms.ModelForm):
    lexer = forms.ChoiceField(
        label=_(u'Lexer'),
        choices=LEXER_LIST,
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

        try:
            if self.request.session['userprefs'].get('display_all_lexer', False):
                self.fields['lexer'].choices = LEXER_LIST_ALL
        except KeyError:
            pass

        try:
            self.fields['author'].initial = self.request.session['userprefs'].get('default_name', '')
        except KeyError:
            pass

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

        return self.request, self.instance

    class Meta:
        model = Snippet
        fields = (
            'content',
            'lexer',
        )
