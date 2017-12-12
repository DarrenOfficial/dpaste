===
API
===

dpaste provides a simple API endpoint to create new snippets. All you need to
do is a simple ``POST`` request to the API endpoint ``/api/``::


    POST http://dpaste.de/api/


Available POST data for an API call:
====================================

``content`` (required)
~~~~~~~~~~~~~~~~~~~~~~

The UTF-8 encoded string you want to paste.

``lexer`` (optional)
~~~~~~~~~~~~~~~~~~~~

The lexer string key used for highlighting. See `lexer list`_  for a full list
of choices. Default: ``text``.

``format`` (optional)
~~~~~~~~~~~~~~~~~~~~~

The format of the API response. Choices are:

* ``default`` — Returns a full qualified URL wrapped in quotes. Example::

    "https://dpaste.de/xsWd"

* ``url`` — Returns the full qualified URL to the snippet, without surrounding
  quotes, but with a line break. Example::

    https://dpaste.de/xsWd\n

* ``json`` — Returns a JSON object containing the URL, lexer and content of the
  the snippet. Example::


    {
        "url": "https://dpaste.de/xsWd",
        "lexer": "python",
        "content": "The text body of the snippet."
    }


``expires`` (optional)
~~~~~~~~~~~~~~~~~~~~~~

A keyword to indicate the lifetime of a snippetn in seconds. The values are
predefined by the server. Calling this with an invalid value returns a HTTP 400
BadRequest together with a list of valid values. Default: ``2592000``. In the
default configuration valid values are:

* onetime
* never
* 3600
* 604800
* 2592000

``filename`` (optional)
~~~~~~~~~~~~~~~~~~~~~~~

A filename which we use to determine a lexer, if ``lexer`` is not set. In case
we can't determine a file, the lexer will fallback to ``plain`` code (no
highlighting). A given ``lexer`` will overwrite any filename! Example::

    {
        "url": "https://dpaste.de/xsWd",
        "lexer": "",
        "filename": "python",
        "content": "The text body of the snippet."
    }

This will create a ``python`` highlighted snippet. However in this example::

    {
        "url": "https://dpaste.de/xsWd",
        "lexer": "php",
        "filename": "python",
        "content": "The text body of the snippet."
    }

Since the lexer is set too, we will create a ``php`` highlighted snippet.

.. note:: Since ``lexer`` defaults to ``python`` you have to specifically
    unset it when using ``filename``.

.. hint:: You need to adjust the setting ``DPASTE_BASE_URL`` which is used
    to generate the full qualified URL in the API response. See :doc:`settings`.

.. note:: When creating new snippets via the API, they won't be listed on the
    history page since they are related to a browser session.

.. _lexer list: https://github.com/bartTC/dpaste/blob/master/dpaste/highlight.py#L25

Example code snippets:
======================

A sample Python 2 script to publish snippets::

    #!/usr/bin/env python

    import urllib
    import urllib2
    import sys

    def paste_code():
        request = urllib2.Request(
            'https://dpaste.de/api/',
            urllib.urlencode([('content', sys.stdin.read())]),
        )
        response = urllib2.urlopen(request)
        # Strip surrounding quotes (NB: response has no trailing newline)
        print response.read()[1:-1]

    if __name__ == '__main__':
        paste_code()

You can simply use curl to publish a whole file::

    $ alias dpaste="curl -F 'format=url' -F 'content=<-' https://dpaste.de/api/"
    $ cat foo.txt | dpaste
    https://dpaste.de/ke2pB
