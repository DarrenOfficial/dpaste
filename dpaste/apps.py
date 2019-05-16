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
    # This is intentionally missing l and I as they look too similar with
    # sans-serif fonts.
    SLUG_CHOICES = (
        'abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNOPQRSTUVWXYZ1234567890'
    )

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

    # Disable "view Raw" mode.
    RAW_MODE_ENABLED = True

    # Lexers which have wordwrap enabled by default
    LEXER_WORDWRAP = ('rst',)

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
            RestructuredTextHighlighter,
        )

        return [
            (self.PLAIN_TEXT_SYMBOL, 'Plain Text', PlainTextHighlighter),
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

        To get a current list of available lexers in Pygements do:

        >>> from pygments import lexers
        >>> sorted([(i[1][0], i[0]) for i in lexers.get_all_lexers()])
        [('abap', 'ABAP'),
         ('abnf', 'ABNF'),
         ('ada', 'Ada'),
         ...
        """
        from dpaste.highlight import PlainCodeHighlighter

        return [
            (self.PLAIN_CODE_SYMBOL, 'Plain Code', PlainCodeHighlighter),
            # ('abap', 'ABAP'),
            # ('abnf', 'ABNF'),
            # ('ada', 'Ada'),
            # ('adl', 'ADL'),
            # ('agda', 'Agda'),
            # ('aheui', 'Aheui'),
            # ('ahk', 'autohotkey'),
            # ('alloy', 'Alloy'),
            # ('ampl', 'Ampl'),
            # ('antlr', 'ANTLR'),
            # ('antlr-as', 'ANTLR With ActionScript Target'),
            # ('antlr-cpp', 'ANTLR With CPP Target'),
            # ('antlr-csharp', 'ANTLR With C# Target'),
            # ('antlr-java', 'ANTLR With Java Target'),
            # ('antlr-objc', 'ANTLR With ObjectiveC Target'),
            # ('antlr-perl', 'ANTLR With Perl Target'),
            # ('antlr-python', 'ANTLR With Python Target'),
            # ('antlr-ruby', 'ANTLR With Ruby Target'),
            # ('apacheconf', 'ApacheConf'),
            # ('apl', 'APL'),
            ('applescript', 'AppleScript'),
            ('arduino', 'Arduino'),
            # ('as', 'ActionScript'),
            # ('as3', 'ActionScript 3'),
            # ('aspectj', 'AspectJ'),
            # ('aspx-cs', 'aspx-cs'),
            # ('aspx-vb', 'aspx-vb'),
            # ('asy', 'Asymptote'),
            # ('at', 'AmbientTalk'),
            # ('autoit', 'AutoIt'),
            # ('awk', 'Awk'),
            # ('basemake', 'Base Makefile'),
            ('bash', 'Bash'),
            ('bat', 'Batchfile'),
            # ('bbcode', 'BBCode'),
            # ('bc', 'BC'),
            # ('befunge', 'Befunge'),
            # ('bib', 'BibTeX'),
            # ('blitzbasic', 'BlitzBasic'),
            # ('blitzmax', 'BlitzMax'),
            # ('bnf', 'BNF'),
            # ('boo', 'Boo'),
            # ('boogie', 'Boogie'),
            # ('brainfuck', 'Brainfuck'),
            # ('bro', 'Bro'),
            # ('bst', 'BST'),
            # ('bugs', 'BUGS'),
            ('c', 'C'),
            # ('c-objdump', 'c-objdump'),
            # ('ca65', 'ca65 assembler'),
            # ('cadl', 'cADL'),
            # ('camkes', 'CAmkES'),
            # ('capdl', 'CapDL'),
            # ('capnp', "Cap'n Proto"),
            # ('cbmbas', 'CBM BASIC V2'),
            # ('ceylon', 'Ceylon'),
            # ('cfc', 'Coldfusion CFC'),
            # ('cfengine3', 'CFEngine3'),
            # ('cfm', 'Coldfusion HTML'),
            # ('cfs', 'cfstatement'),
            # ('chai', 'ChaiScript'),
            # ('chapel', 'Chapel'),
            # ('cheetah', 'Cheetah'),
            # ('cirru', 'Cirru'),
            # ('clay', 'Clay'),
            # ('clean', 'Clean'),
            ('clojure', 'Clojure'),
            # ('clojurescript', 'ClojureScript'),
            ('cmake', 'CMake'),
            # ('cobol', 'COBOL'),
            # ('cobolfree', 'COBOLFree'),
            ('coffee-script', 'CoffeeScript'),
            ('common-lisp', 'Common Lisp'),
            # ('componentpascal', 'Component Pascal'),
            ('console', 'Console/Bash Session'),
            # ('control', 'Debian Control file'),
            # ('coq', 'Coq'),
            # ('cpp', 'C++'),
            # ('cpp-objdump', 'cpp-objdump'),
            # ('cpsa', 'CPSA'),
            # ('cr', 'Crystal'),
            # ('crmsh', 'Crmsh'),
            # ('croc', 'Croc'),
            # ('cryptol', 'Cryptol'),
            ('csharp', 'C#'),
            # ('csound', 'Csound Orchestra'),
            # ('csound-document', 'Csound Document'),
            # ('csound-score', 'Csound Score'),
            ('css', 'CSS'),
            # ('css+django', 'CSS+Django/Jinja'),
            # ('css+erb', 'CSS+Ruby'),
            # ('css+genshitext', 'CSS+Genshi Text'),
            # ('css+lasso', 'CSS+Lasso'),
            # ('css+mako', 'CSS+Mako'),
            # ('css+mozpreproc', 'CSS+mozpreproc'),
            # ('css+myghty', 'CSS+Myghty'),
            # ('css+php', 'CSS+PHP'),
            # ('css+smarty', 'CSS+Smarty'),
            # ('cucumber', 'Gherkin'),
            ('cuda', 'CUDA'),
            # ('cypher', 'Cypher'),
            # ('cython', 'Cython'),
            # ('d', 'D'),
            # ('d-objdump', 'd-objdump'),
            ('dart', 'Dart'),
            ('delphi', 'Delphi'),
            # ('dg', 'dg'),
            ('diff', 'Diff'),
            ('django', 'Django/Jinja'),
            ('docker', 'Docker'),
            # ('doscon', 'MSDOS Session'),
            # ('dpatch', 'Darcs Patch'),
            # ('dtd', 'DTD'),
            # ('duel', 'Duel'),
            # ('dylan', 'Dylan'),
            # ('dylan-console', 'Dylan session'),
            # ('dylan-lid', 'DylanLID'),
            # ('earl-grey', 'Earl Grey'),
            # ('easytrieve', 'Easytrieve'),
            # ('ebnf', 'EBNF'),
            # ('ec', 'eC'),
            # ('ecl', 'ECL'),
            # ('eiffel', 'Eiffel'),
            ('elixir', 'Elixir'),
            # ('elm', 'Elm'),
            # ('emacs', 'EmacsLisp'),
            # ('erb', 'ERB'),
            # ('erl', 'Erlang erl session'),
            ('erlang', 'Erlang'),
            # ('evoque', 'Evoque'),
            # ('extempore', 'xtlang'),
            # ('ezhil', 'Ezhil'),
            # ('factor', 'Factor'),
            # ('fan', 'Fantom'),
            # ('fancy', 'Fancy'),
            # ('felix', 'Felix'),
            # ('fennel', 'Fennel'),
            # ('fish', 'Fish'),
            # ('flatline', 'Flatline'),
            # ('forth', 'Forth'),
            # ('fortran', 'Fortran'),
            # ('fortranfixed', 'FortranFixed'),
            # ('foxpro', 'FoxPro'),
            # ('fsharp', 'FSharp'),
            # ('gap', 'GAP'),
            # ('gas', 'GAS'),
            # ('genshi', 'Genshi'),
            # ('genshitext', 'Genshi Text'),
            # ('glsl', 'GLSL'),
            # ('gnuplot', 'Gnuplot'),
            ('go', 'Go'),
            # ('golo', 'Golo'),
            # ('gooddata-cl', 'GoodData-CL'),
            # ('gosu', 'Gosu'),
            # ('groff', 'Groff'),
            # ('groovy', 'Groovy'),
            # ('gst', 'Gosu Template'),
            # ('haml', 'Haml'),
            ('handlebars', 'Handlebars'),
            ('haskell', 'Haskell'),
            # ('haxeml', 'Hxml'),
            # ('hexdump', 'Hexdump'),
            # ('hlsl', 'HLSL'),
            # ('hsail', 'HSAIL'),
            ('html', 'HTML'),
            # ('html+cheetah', 'HTML+Cheetah'),
            ('html+django', 'HTML + Django/Jinja'),
            # ('html+evoque', 'HTML+Evoque'),
            # ('html+genshi', 'HTML+Genshi'),
            # ('html+handlebars', 'HTML+Handlebars'),
            # ('html+lasso', 'HTML+Lasso'),
            # ('html+mako', 'HTML+Mako'),
            # ('html+myghty', 'HTML+Myghty'),
            # ('html+ng2', 'HTML + Angular2'),
            # ('html+php', 'HTML+PHP'),
            # ('html+smarty', 'HTML+Smarty'),
            # ('html+twig', 'HTML+Twig'),
            # ('html+velocity', 'HTML+Velocity'),
            # ('http', 'HTTP'),
            # ('hx', 'Haxe'),
            # ('hybris', 'Hybris'),
            # ('hylang', 'Hy'),
            # ('i6t', 'Inform 6 template'),
            # ('idl', 'IDL'),
            # ('idris', 'Idris'),
            # ('iex', 'Elixir iex session'),
            # ('igor', 'Igor'),
            # ('inform6', 'Inform 6'),
            # ('inform7', 'Inform 7'),
            ('ini', 'INI'),
            # ('io', 'Io'),
            # ('ioke', 'Ioke'),
            # ('ipython2', 'IPython'),
            # ('ipython3', 'IPython3'),
            ('ipythonconsole', 'IPython console session'),
            ('irc', 'IRC logs'),
            # ('isabelle', 'Isabelle'),
            # ('j', 'J'),
            # ('jags', 'JAGS'),
            # ('jasmin', 'Jasmin'),
            ('java', 'Java'),
            # ('javascript+mozpreproc', 'Javascript+mozpreproc'),
            # ('jcl', 'JCL'),
            # ('jlcon', 'Julia console'),
            ('js', 'JavaScript'),
            # ('js+cheetah', 'JavaScript+Cheetah'),
            # ('js+django', 'JavaScript+Django/Jinja'),
            # ('js+erb', 'JavaScript+Ruby'),
            # ('js+genshitext', 'JavaScript+Genshi Text'),
            # ('js+lasso', 'JavaScript+Lasso'),
            # ('js+mako', 'JavaScript+Mako'),
            # ('js+myghty', 'JavaScript+Myghty'),
            # ('js+php', 'JavaScript+PHP'),
            # ('js+smarty', 'JavaScript+Smarty'),
            # ('jsgf', 'JSGF'),
            # ('json', 'JSON'),
            # ('json-object', 'JSONBareObject'),
            # ('jsonld', 'JSON-LD'),
            # ('jsp', 'Java Server Page'),
            # ('julia', 'Julia'),
            # ('juttle', 'Juttle'),
            # ('kal', 'Kal'),
            # ('kconfig', 'Kconfig'),
            # ('koka', 'Koka'),
            ('kotlin', 'Kotlin'),
            # ('lagda', 'Literate Agda'),
            # ('lasso', 'Lasso'),
            # ('lcry', 'Literate Cryptol'),
            # ('lean', 'Lean'),
            ('less', 'LessCSS'),
            # ('lhs', 'Literate Haskell'),
            # ('lidr', 'Literate Idris'),
            # ('lighty', 'Lighttpd configuration file'),
            # ('limbo', 'Limbo'),
            # ('liquid', 'liquid'),
            # ('live-script', 'LiveScript'),
            # ('llvm', 'LLVM'),
            # ('logos', 'Logos'),
            # ('logtalk', 'Logtalk'),
            # ('lsl', 'LSL'),
            ('lua', 'Lua'),
            ('make', 'Makefile'),
            # ('mako', 'Mako'),
            # ('maql', 'MAQL'),
            # ('mask', 'Mask'),
            # ('mason', 'Mason'),
            # ('mathematica', 'Mathematica'),
            ('matlab', 'Matlab'),
            # ('matlabsession', 'Matlab session'),
            # ('md', 'markdown'),
            # ('minid', 'MiniD'),
            # ('modelica', 'Modelica'),
            # ('modula2', 'Modula-2'),
            # ('monkey', 'Monkey'),
            # ('monte', 'Monte'),
            # ('moocode', 'MOOCode'),
            # ('moon', 'MoonScript'),
            # ('mozhashpreproc', 'mozhashpreproc'),
            # ('mozpercentpreproc', 'mozpercentpreproc'),
            # ('mql', 'MQL'),
            # ('mscgen', 'Mscgen'),
            # ('mupad', 'MuPAD'),
            # ('mxml', 'MXML'),
            # ('myghty', 'Myghty'),
            # ('mysql', 'MySQL'),
            # ('nasm', 'NASM'),
            # ('ncl', 'NCL'),
            # ('nemerle', 'Nemerle'),
            # ('nesc', 'nesC'),
            # ('newlisp', 'NewLisp'),
            # ('newspeak', 'Newspeak'),
            # ('ng2', 'Angular2'),
            ('nginx', 'Nginx configuration file'),
            # ('nim', 'Nimrod'),
            # ('nit', 'Nit'),
            # ('nixos', 'Nix'),
            # ('nsis', 'NSIS'),
            ('numpy', 'NumPy'),
            # ('nusmv', 'NuSMV'),
            # ('objdump', 'objdump'),
            # ('objdump-nasm', 'objdump-nasm'),
            ('objective-c', 'Objective-C'),
            # ('objective-c++', 'Objective-C++'),
            # ('objective-j', 'Objective-J'),
            # ('ocaml', 'OCaml'),
            # ('octave', 'Octave'),
            # ('odin', 'ODIN'),
            # ('ooc', 'Ooc'),
            # ('opa', 'Opa'),
            # ('openedge', 'OpenEdge ABL'),
            # ('pacmanconf', 'PacmanConf'),
            # ('pan', 'Pan'),
            # ('parasail', 'ParaSail'),
            # ('pawn', 'Pawn'),
            ('perl', 'Perl'),
            # ('perl6', 'Perl6'),
            ('php', 'PHP'),
            # ('pig', 'Pig'),
            # ('pike', 'Pike'),
            # ('pkgconfig', 'PkgConfig'),
            # ('plpgsql', 'PL/pgSQL'),
            ('postgresql', 'PostgreSQL SQL dialect'),
            # ('postscript', 'PostScript'),
            # ('pot', 'Gettext Catalog'),
            # ('pov', 'POVRay'),
            # ('powershell', 'PowerShell'),
            # ('praat', 'Praat'),
            # ('prolog', 'Prolog'),
            # ('properties', 'Properties'),
            # ('protobuf', 'Protocol Buffer'),
            # ('ps1con', 'PowerShell Session'),
            # ('psql', 'PostgreSQL console (psql)'),
            # ('pug', 'Pug'),
            # ('puppet', 'Puppet'),
            # ('py3tb', 'Python 3.0 Traceback'),
            # ('pycon', 'Python console session'),
            # ('pypylog', 'PyPy Log'),
            # ('pytb', 'Python Traceback'),
            ('python', 'Python'),
            # ('python3', 'Python 3'),
            # ('qbasic', 'QBasic'),
            # ('qml', 'QML'),
            # ('qvto', 'QVTO'),
            # ('racket', 'Racket'),
            # ('ragel', 'Ragel'),
            # ('ragel-c', 'Ragel in C Host'),
            # ('ragel-cpp', 'Ragel in CPP Host'),
            # ('ragel-d', 'Ragel in D Host'),
            # ('ragel-em', 'Embedded Ragel'),
            # ('ragel-java', 'Ragel in Java Host'),
            # ('ragel-objc', 'Ragel in Objective C Host'),
            # ('ragel-ruby', 'Ragel in Ruby Host'),
            # ('raw', 'Raw token data'),
            ('rb', 'Ruby'),
            # ('rbcon', 'Ruby irb session'),
            # ('rconsole', 'RConsole'),
            # ('rd', 'Rd'),
            # ('rebol', 'REBOL'),
            # ('red', 'Red'),
            # ('redcode', 'Redcode'),
            # ('registry', 'reg'),
            # ('resource', 'ResourceBundle'),
            # ('rexx', 'Rexx'),
            # ('rhtml', 'RHTML'),
            # ('rnc', 'Relax-NG Compact'),
            # ('roboconf-graph', 'Roboconf Graph'),
            # ('roboconf-instances', 'Roboconf Instances'),
            # ('robotframework', 'RobotFramework'),
            # ('rql', 'RQL'),
            # ('rsl', 'RSL'),
            ('rst', 'reStructuredText'),
            # ('rts', 'TrafficScript'),
            ('rust', 'Rust'),
            # ('sas', 'SAS'),
            ('sass', 'Sass'),
            # ('sc', 'SuperCollider'),
            # ('scala', 'Scala'),
            # ('scaml', 'Scaml'),
            # ('scheme', 'Scheme'),
            # ('scilab', 'Scilab'),
            ('scss', 'SCSS'),
            # ('shen', 'Shen'),
            # ('silver', 'Silver'),
            # ('slim', 'Slim'),
            # ('smali', 'Smali'),
            # ('smalltalk', 'Smalltalk'),
            # ('smarty', 'Smarty'),
            # ('sml', 'Standard ML'),
            # ('snobol', 'Snobol'),
            # ('snowball', 'Snowball'),
            ('sol', 'Solidity'),
            # ('sourceslist', 'Debian Sourcelist'),
            # ('sp', 'SourcePawn'),
            # ('sparql', 'SPARQL'),
            # ('spec', 'RPMSpec'),
            # ('splus', 'S'),
            ('sql', 'SQL'),
            # ('sqlite3', 'sqlite3con'),
            # ('squidconf', 'SquidConf'),
            # ('ssp', 'Scalate Server Page'),
            # ('stan', 'Stan'),
            # ('stata', 'Stata'),
            ('swift', 'Swift'),
            # ('swig', 'SWIG'),
            # ('systemverilog', 'systemverilog'),
            # ('tads3', 'TADS 3'),
            # ('tap', 'TAP'),
            # ('tasm', 'TASM'),
            # ('tcl', 'Tcl'),
            # ('tcsh', 'Tcsh'),
            # ('tcshcon', 'Tcsh Session'),
            # ('tea', 'Tea'),
            # ('termcap', 'Termcap'),
            # ('terminfo', 'Terminfo'),
            # ('terraform', 'Terraform'),
            ('tex', 'TeX'),
            # ('text', 'Text only'),
            # ('thrift', 'Thrift'),
            # ('todotxt', 'Todotxt'),
            # ('trac-wiki', 'MoinMoin/Trac Wiki markup'),
            # ('treetop', 'Treetop'),
            # ('ts', 'TypeScript'),
            # ('tsql', 'Transact-SQL'),
            # ('turtle', 'Turtle'),
            # ('twig', 'Twig'),
            ('typoscript', 'TypoScript'),
            # ('typoscriptcssdata', 'TypoScriptCssData'),
            # ('typoscripthtmldata', 'TypoScriptHtmlData'),
            # ('urbiscript', 'UrbiScript'),
            # ('vala', 'Vala'),
            # ('vb.net', 'VB.net'),
            # ('vcl', 'VCL'),
            # ('vclsnippets', 'VCLSnippets'),
            # ('vctreestatus', 'VCTreeStatus'),
            # ('velocity', 'Velocity'),
            # ('verilog', 'verilog'),
            # ('vgl', 'VGL'),
            # ('vhdl', 'vhdl'),
            ('vim', 'VimL'),
            # ('wdiff', 'WDiff'),
            # ('whiley', 'Whiley'),
            # ('x10', 'X10'),
            ('xml', 'XML'),
            # ('xml+cheetah', 'XML+Cheetah'),
            # ('xml+django', 'XML+Django/Jinja'),
            # ('xml+erb', 'XML+Ruby'),
            # ('xml+evoque', 'XML+Evoque'),
            # ('xml+lasso', 'XML+Lasso'),
            # ('xml+mako', 'XML+Mako'),
            # ('xml+myghty', 'XML+Myghty'),
            # ('xml+php', 'XML+PHP'),
            # ('xml+smarty', 'XML+Smarty'),
            # ('xml+velocity', 'XML+Velocity'),
            # ('xorg.conf', 'Xorg'),
            # ('xquery', 'XQuery'),
            ('xslt', 'XSLT'),
            # ('xtend', 'Xtend'),
            # ('xul+mozpreproc', 'XUL+mozpreproc'),
            ('yaml', 'YAML'),
            # ('yaml+jinja', 'YAML+Jinja'),
            # ('zephir', 'Zephir')
        ]

    @staticmethod
    def get_base_url(request=None):
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
