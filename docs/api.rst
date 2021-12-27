===
API
===

API endpoint
============

dpaste provides a simple API endpoint to create new snippets. All you need to
do is a simple ``POST`` request to the API endpoint, usually ``/api/``:

.. http:post:: /api/

   Create a new Snippet on this dpaste installation. It returns the full
   URL that snippet was created.

   **Example request**:

   .. code-block:: bash

      $ curl -X POST -F "format=url" -F "content=ABC" https:/dpaste.org/api/

      Host: dpaste.org
      User-Agent: curl/7.54.0
      Accept: */*

   **Example response**:

   .. sourcecode:: json

      {
        "lexer": "python",
        "url": "https://dpaste.org/EBKU",
        "content": "ABC"
      }

   :form content: (required) The UTF-8 encoded string you want to paste.

   :form lexer: (optional) The lexer string key used for highlighting. See
    the ``CODE_FORMATTER`` property in :ref:`settings` for a full list
    of choices. Default: ``_code``.

   :form format: (optional) The format of the API response. Choices are:

    * ``default`` — Returns a full qualified URL wrapped in quotes.
      Example: ``"https://dpaste.org/xsWd"``

    * ``url`` — Returns the full qualified URL to the snippet, without surrounding
      quotes, but with a line break. Example: ``https://dpaste.org/xsWd\n``

    * ``json`` — Returns a JSON object containing the URL, lexer and content of the
      the snippet. Example:

      .. code-block:: json

          {
            "url": "https://dpaste.org/xsWd",
            "lexer": "python",
            "content": "The text body of the snippet."
          }


   :form expires: (optional) A keyword to indicate the lifetime of a snippet in
    seconds. The values are
    predefined by the server. Calling this with an invalid value returns a HTTP 400
    BadRequest together with a list of valid values. Default: ``2592000``. In the
    default configuration valid values are:

    * onetime
    * never
    * 3600
    * 604800
    * 2592000

   :form filename: (optional) A filename which we use to determine a lexer, if
    ``lexer`` is not set. In case we can't determine a file, the lexer will
    fallback to ``plain`` code (no highlighting). A given ``lexer`` will overwrite
    any filename! Example:

    .. code-block:: json

        {
          "url": "https://dpaste.org/xsWd",
          "lexer": "",
          "filename": "python",
          "content": "The text body of the snippet."
        }

    This will create a ``python`` highlighted snippet. However in this example:

    .. code-block:: json

        {
          "url": "https://dpaste.org/xsWd",
          "lexer": "php",
          "filename": "python",
          "content": "The text body of the snippet."
        }

    Since the lexer is set too, we will create a ``php`` highlighted snippet.

   :statuscode 200: No Error.
   :statuscode 400: One of the above form options was invalid,
    the response will contain a meaningful error message.

.. hint:: If you have a standalone installation and your API returns
    ``https://dpaste-base-url.example.org`` as the domain, you need to adjust
    the setting ``get_base_url`` property. See :ref:`settings`.


Third party API integration
===========================

subdpaste
    a Sublime Editor plugin: https://github.com/bartTC/SubDpaste
Marmalade
    an Emacs plugin: http://marmalade-repo.org/packages/dpaste_de
atom-dpaste
    for the Atom editor: https://atom.io/packages/atom-dpaste
dpaste-magic
    an iPython extension: https://pypi.org/project/dpaste-magic/

You can also paste your file content to the API via curl, directly from the
command line:

.. code-block:: bash

    $ alias dpaste="curl -F 'format=url' -F 'content=<-' https://dpaste.org/api/"
    $ cat foo.txt | dpaste
    https://dpaste.org/ke2pB

.. note:: If you wrote or know a third party dpaste plugin or extension,
    please open an *Issue* on Github_ and it's added here.

.. _Github: https://github.com/bartTC/dpaste
