from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from pastebin.apps.dpaste.models import Snippet, Spamword
from pastebin.apps.dpaste.highlight import LEXER_LIST_ALL, LEXER_LIST, LEXER_DEFAULT
import datetime

#===============================================================================
# Snippet Form and Handling
#===============================================================================

EXPIRE_CHOICES = (
    (3600, _(u'In one hour')),
    (3600*24*7, _(u'In one week')),
    (3600*24*30, _(u'In one month')),
    (3600*24*30*12*100, _(u'Save forever')), # 100 years, I call it forever ;)
)

EXPIRE_DEFAULT = 3600*24*30

class SnippetForm(forms.ModelForm):

    lexer = forms.ChoiceField(
        choices=LEXER_LIST,
        initial=LEXER_DEFAULT,
        label=_(u'Lexer'),
    )
    
    expire_options = forms.ChoiceField(
        choices=EXPIRE_CHOICES,
        initial=EXPIRE_DEFAULT,
        label=_(u'Expires'),
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
        
    def clean_content(self):
        content = self.cleaned_data.get('content')
        if content:
            regex = Spamword.objects.get_regex()
            if regex.findall(content):
                raise forms.ValidationError('This snippet was identified as SPAM.')
        return content
        
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
            'title',
            'content',
            'author',
            'lexer',
        )


#===============================================================================
# User Settings
#===============================================================================

USERPREFS_FONT_CHOICES = [(None, _(u'Default'))] + [
    (i, i) for i in sorted((
        'Monaco',
        'Bitstream Vera Sans Mono',
        'Courier New',
        'Consolas',
    ))
]

USERPREFS_SIZES = [(None, _(u'Default'))] + [(i, '%dpx' % i) for i in range(5, 25)]

class UserSettingsForm(forms.Form):

    default_name = forms.CharField(label=_(u'Default Name'), required=False)
    display_all_lexer = forms.BooleanField(
        label=_(u'Display all lexer'), 
        required=False,
        widget=forms.CheckboxInput,
        help_text=_(u'This also enables the super secret \'guess lexer\' function.'),
    )
    font_family = forms.ChoiceField(label=_(u'Font Family'), required=False, choices=USERPREFS_FONT_CHOICES)
    font_size = forms.ChoiceField(label=_(u'Font Size'), required=False, choices=USERPREFS_SIZES)
    line_height = forms.ChoiceField(label=_(u'Line Height'), required=False, choices=USERPREFS_SIZES)
