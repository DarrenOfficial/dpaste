from django.apps import AppConfig, apps
from django.utils.translation import ugettext_lazy as _

class dpasteAppConfig(AppConfig):
    name = 'dpaste'
    verbose_name = 'dpaste'

    # Integer. Length of the random slug for each new snippet. In the rare
    # case an existing slug is generated again, the length will increase by
    # one more character.
    SLUG_LENGTH = 4

    # String. A string of characters which are used to create the random slug.
    SLUG_CHOICES = 'abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNOPQRSTUVWXYZ1234567890'

    # String. The lexer key that is pre-selected in the dropdown. Note that
    # this is only used if the user has not saved a snippet before, otherwise
    LEXER_DEFAULT = 'python'

    # Integer. Maximum number of bytes per snippet.
    MAX_CONTENT_LENGTH = 250 * 1024 * 1024

    # A tuple of seconds and a descriptive string used in the lexer
    # expiration dropdown. Example::
    #
    #     from django.utils.translation import ugettext_lazy as _
    #     DPASTE_EXPIRE_CHOICES = (
    #         (3600, _('In one hour')),
    #         (3600 * 24 * 7, _('In one week')),
    #         (3600 * 24 * 30, _('In one month')),
    #         (3600 * 24 * 30 * 12 * 100, _('100 Years')),
    #     )
    #

    # **Infinite snippets** are supported. You can keep snippets forever when
    # you set the choice key to ``never``. The management command will ignore
    # these snippets::
    #
    #     from django.utils.translation import ugettext_lazy as _
    #     DPASTE_EXPIRE_CHOICES = (
    #         (3600, _('In one hour')),
    #         ('never', _('Never')),
    #     )
    EXPIRE_CHOICES = (
        ('onetime', _('One-Time snippet')),
        (3600, _('In one hour')),
        (3600 * 24 * 7, _('In one week')),
        (3600 * 24 * 30, _('In one month')),
        ('never', _('Never')),
    )

    # Default value for ``EXPIRE_CHOICES``
    EXPIRE_DEFAULT = 3600 * 24 * 7

    # **One-Time snippets** are supported. One-Time snippets are automatically
    # deleted once a defined view count has reached (Default: ``2``). To
    # enable one-time snippets you have to add a choice ``onetime`` to the
    # expire choices::
    #
    #     from django.utils.translation import ugettext_lazy as _
    #     DPASTE_EXPIRE_CHOICES = (
    #         ('onetime', _('One-Time snippet')),
    #         (3600, _('In one hour')),
    #         (3600 * 24 * 7, _('In one week')),
    #         (3600 * 24 * 30, _('In one month')),
    #     )
    #
    # You can also set the maximum view count after what the snippet gets
    # deleted. The default is ``2``. One view is from the author, one view
    # is from another user.
    ONETIME_LIMIT = 2

    # Lexers which have wordwrap enabled by default
    LEXER_WORDWRAP = ('rst',)

    @property
    def BASE_URL(self, request=None):
        """
        String. The full qualified hostname and path to the dpaste instance.
        This is used to generate a link in the API response. If the "Sites"
        framework is installed, it uses the current Site domain. Otherwise
        it falls back to 'https://dpaste.de'
        """
        if apps.is_installed('django.contrib.sites'):
            from django.contrib.sites.shortcuts import get_current_site
            site = get_current_site(request)
            if site:
                return 'https://{0}'.format(site.domain)
        return 'https://dpaste.de'


    # Key names of the default text and code lexer.
    PLAIN_TEXT_SYMBOL = '_text'
    PLAIN_CODE_SYMBOL = '_code'

    @property
    def TEXT_FORMATTER(self):
        """
        Choices list with all "Text" lexer. Prepend keys with an underscore
        so they don't accidentally clash with a Pygments Lexer name.

        Each list contains a lexer tuple of:

           (Lexer key,
            Lexer Display Name,
            Lexer Highlight Class)

        If the Highlight Class is not given, PygmentsHighlighter is used.
        """
        from dpaste.highlight import (
            PlainTextHighlighter,
            MarkdownHighlighter,
            RestructuredTextHighlighter
        )
        return [
            (self.PLAIN_TEXT_SYMBOL, 'Plain Text',  PlainTextHighlighter),
            ('_markdown', 'Markdown', MarkdownHighlighter),
            ('_rst', 'reStructuredText', RestructuredTextHighlighter),
        ]

    @property
    def CODE_FORMATTER(self):
        """
        Choices list with all "Code" Lexer. Each list
        contains a lexer tuple of:

           (Lexer key,
            Lexer Display Name,
            Lexer Highlight Class)

        If the Highlight Class is not given, PygmentsHighlighter is used.
        """
        from dpaste.highlight import (
            PlainCodeHighlighter,
            SolidityHighlighter
        )
        return [
            (self.PLAIN_CODE_SYMBOL, 'Plain Code', PlainCodeHighlighter),
            ('abap', 'ABAP'),
            ('apacheconf', 'ApacheConf'),
            ('applescript', 'AppleScript'),
            ('as', 'ActionScript'),
            ('bash', 'Bash'),
            ('bbcode', 'BBCode'),
            ('c', 'C'),
            ('cpp', 'C++'),
            ('clojure', 'Clojure'),
            ('cobol', 'COBOL'),
            ('css', 'CSS'),
            ('cuda', 'CUDA'),
            ('dart', 'Dart'),
            ('delphi', 'Delphi'),
            ('diff', 'Diff'),
            ('django', 'Django'),
            ('erlang', 'Erlang'),
            ('fortran', 'Fortran'),
            ('go', 'Go'),
            ('groovy', 'Groovy'),
            ('haml', 'Haml'),
            ('haskell', 'Haskell'),
            ('html', 'HTML'),
            ('http', 'HTTP'),
            ('ini', 'INI'),
            ('irc', 'IRC'),
            ('java', 'Java'),
            ('js', 'JavaScript'),
            ('json', 'JSON'),
            ('lua', 'Lua'),
            ('make', 'Makefile'),
            ('mako', 'Mako'),
            ('mason', 'Mason'),
            ('matlab', 'Matlab'),
            ('modula2', 'Modula'),
            ('monkey', 'Monkey'),
            ('mysql', 'MySQL'),
            ('numpy', 'NumPy'),
            ('objc', 'Obj-C'),
            ('ocaml', 'OCaml'),
            ('perl', 'Perl'),
            ('php', 'PHP'),
            ('postscript', 'PostScript'),
            ('powershell', 'PowerShell'),
            ('prolog', 'Prolog'),
            ('properties', 'Properties'),
            ('puppet', 'Puppet'),
            ('python', 'Python'), # Default lexer
            ('r', 'R'),
            ('rb', 'Ruby'),
            ('rst', 'reStructuredText'),
            ('rust', 'Rust'),
            ('sass', 'Sass'),
            ('scala', 'Scala'),
            ('scheme', 'Scheme'),
            ('scilab', 'Scilab'),
            ('scss', 'SCSS'),
            ('smalltalk', 'Smalltalk'),
            ('smarty', 'Smarty'),
            ('solidity', 'Solidity', SolidityHighlighter),
            ('sql', 'SQL'),
            ('tcl', 'Tcl'),
            ('tcsh', 'Tcsh'),
            ('tex', 'TeX'),
            ('vb.net', 'VB.net'),
            ('vim', 'VimL'),
            ('xml', 'XML'),
            ('xquery', 'XQuery'),
            ('xslt', 'XSLT'),
            ('yaml', 'YAML'),
        ]
