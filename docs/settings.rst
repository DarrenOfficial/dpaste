====================
Settings to override
====================

When dpaste is installed as a standalone service or integrated into an existing
project there are various settings you can override to adjust dpaste's
behavior without touching the code:

.. glossary::

    ``DPASTE_SLUG_LENGTH``
        Integer. Length of the random slug for each new snippet.
        Default: ``4``

    ``DPASTE_SLUG_CHOICES``
        String. A string of characters which are used to create the random slug.
        Default: ``abcdefghijkmnopqrstuvwwxyzABCDEFGHIJKLOMNOPQRSTUVWXYZ1234567890``

    ``DPASTE_LEXER_DEFAULT``
        String. The lexer key that is pre-selected in the dropdown. Note that
        this is only used if the user has not saved a snippet before, otherwise
        we use the last-used lexer. Default: ``python``

    ``DPASTE_MAX_CONTENT_LENGTH``
        Integer. Maximum number of bytes per snippet. Default: ``250 * 1024 * 1024``

    ``DPASTE_MAX_SNIPPETS_PER_USER``
        Integer. Maximum number of snippets we save in teh user session and
        display on the history page. Default: ``10``

    ``DPASTE_BASE_URL``
        String. The full qualified hostname and path to the dpaste instance.
        This is used to generate a link in the API response. Default: ``https://dpaste.de``

    ``DPASTE_LEXER_LIST``
        Choices. A tuple of choices of Pygments lexers used in the lexer
        dropdown. Here is the full `lexer list`_ which is currently used.
        Example::

            DPASTE_LEXER_LIST = (
                ('delphi', 'Delphi'),
                ('php', 'PHP'),
                ('text', 'Text'),
            )

    ``DPASTE_EXPIRE_CHOICES``
        Choices. A tuple of seconds and a descriptive string used in the lexer
        expiration dropdown. Example::

            ugettext = lambda s: s
            DPASTE_EXPIRE_CHOICES = (
                (3600, ugettext(u'In one hour')),
                (3600 * 24 * 7, ugettext(u'In one week')),
                (3600 * 24 * 30, ugettext(u'In one month')),
                (3600 * 24 * 30 * 12 * 100, ugettext(u'100 Years')),
            )

        **One-time snippets** are supported. One time snippets are automatically
        deleted once a defined view count has reached (Default: ``2``). To
        enable one-time snippets you have to add a choice ``onetime`` to the
        expire choices::

            ugettext = lambda s: s
            DPASTE_EXPIRE_CHOICES = (
                ('onetime', ugettext(u'One-Time snippet')),
                (3600, ugettext(u'In one hour')),
                (3600 * 24 * 7, ugettext(u'In one week')),
                (3600 * 24 * 30, ugettext(u'In one month')),
            )

        You can also set the maximum view count after what the snippet gets
        deleted. The default is ``2``. One view is from the author, one view
        is from another user::

            DPASTE_ONETIME_LIMIT = 2

        **Infinite snippets** are supported. You can keep snippets forever when
        you set the choice key to ``never``. The management command will ignore
        these snippets::

            ugettext = lambda s: s
            DPASTE_EXPIRE_CHOICES = (
                (3600, ugettext(u'In one hour')),
                (u'never', ugettext(u'Never')),
            )

    ``DPASTE_EXPIRE_DEFAULT``
        The key of the default value of ``DPASTE_EXPIRE_CHOICES``. Default:
        ``3600 * 24 * 30 * 12 * 100`` or simpler: ``DPASTE_EXPIRE_CHOICES[2][0]``.



.. _lexer list: https://github.com/bartTC/dpaste/blob/master/dpaste/highlight.py#L25
