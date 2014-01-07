===
API
===

dpaste provides a simple API endpoint to create new snippets. All you need to
do is a simple ``POST`` request to the API endpoint ``/api/``::


    POST http://dpaste.de/api/


Available POST data for an API call:
----------------------------------------

``content`` (required)
~~~~~~~~~~~~~~~~~~~~~~

Required. The UTF-8 encoded string you want to paste.

``lexer`` (optional)
~~~~~~~~~~~~~~~~~~~~

Optional. The lexer string key used for highlighting. See `lexer list`_  for
a full list of choices. Default: ``python``.

``format`` (optional)
~~~~~~~~~~~~~~~~~~~~~

Optional. The format of the API response. Choices are:

* ``default`` — Returns a full qualified URL wrapped in quotes. Example::

    "https://dpaste.de/xsWd"

* ``url`` — Returns the full qualified URL to the snippet, without breaks,
  but with a line break. Example::

    https://dpaste.de/xsWd\n

* ``json`` — Returns a JSON object containing the URL, lexer and content of the
  the snippet. Example::


    {
        "url": "https://dpaste.de/xsWd",
        "lexer": "python",
        "conent": "The text body of the snippet."
    }

.. hint:: You need to adjust the setting ``DPASTE_BASE_URL`` which is used
    to generate the full qualified URL in the API response. See :doc:`settings`.

.. note:: When creating new snippets via the API, they won't be listed on the
    history page since they are related to a browser session.

.. _lexer list: https://github.com/bartTC/dpaste/blob/master/dpaste/highlight.py#L25
