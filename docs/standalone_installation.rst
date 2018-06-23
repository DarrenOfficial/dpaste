.. _standalone_installation:

==============================================
Standalone Installation (or local development)
==============================================

.. important:: This documentation describes the installation of dpaste
    as a standalone project, primarily for local development. If you want
    to integrate the application into your existing Django project, see
    :ref:`project_installation`.

The project uses `pipenv`_ to maintain and install dependencies. Install it
once globally with pip:

.. code:: bash

    $ pip install pipenv

Then checkout the Git project code from Github and install the Node and
Python dependencies.

.. code-block:: bash

    $ cd dpaste/
    $ pipenv install --dev      # Installs the project and Python dependencies
    $ npm install               # Installs the node dependencies and compiles
                                # the static files (JS/CSS).

Copy the sample settings file and edit it, to meet your needs:

.. code-block:: bash

    $ cp dpaste/settings/local.py.example dpaste/settings/local.py

Run the testsuite to make sure everything was built correctly:

.. code-block:: bash

    $ pipenv run ./runtests.py

Finally, to run the project on your local machine:

.. code-block:: bash

    $ pipenv run ./manage.py migrate
    $ pipenv run ./manage.py runserver

If this is a public, standalone installation, make sure you purge
the expired snippets regularly. See :ref:`purge_expired_snippets`.

CSS and Javascript development
==============================

Both CSS and Javascript files need to be compiled and compressed. The resulting
files are not commited with the project code.

There are some helper scripts you can invoke with ``npm``

``npm start``
    Compile the static files and run the Django runserver.
``npm run build``
    Compile static files.
``npm run build-js``
    Compile only JS files.
``npm run build-css``
    Compile only CSS files.
``npm run watch-css``
    Same as ``build-css`` but it automatically watches for changes in the
    CSS files and re-compiles it.
``npm run docs``
    Compile this documentation. The result will be in ``docs/_build/html``.
``npm run watch-docs``
    Same as ``docs`` but it automatically watches for changes in the
    documentation files and re-compiles the docs.


.. note:: See ``npm run --list`` for the full and most recent list of
    helper scripts.

Testing with Tox
================

dpaste is continuously tested online with Travis_. You can also run the test
suite locally with tox_. Tox automatically tests the project against multiple
Python and Django versions.

Similar to ``pipenv`` it's useful to have tox installed globally:

.. code-block:: bash

    $ pip install tox

Then simply call it from the project directory.

.. code-block:: bash

    $ cd dpaste/
    $ tox

.. code-block:: text
    :caption: Example tox output:

    $ tox

    py35-django-111 create: /tmp/tox/dpaste/py35-django-111
    SKIPPED:InterpreterNotFound: python3.5
    py36-django-111 create: /tmp/tox/dpaste/py36-django-111
    py36-django-111 installdeps: django>=1.11,<1.12
    py36-django-111 inst: /tmp/tox/dpaste/dist/dpaste-3.0a1.zip

    ...................
    ----------------------------------------------------------------------
    Ran 48 tests in 1.724s
    OK


    SKIPPED:  py35-django-111: InterpreterNotFound: python3.5
    SKIPPED:  py35-django-20: InterpreterNotFound: python3.5
    py36-django-111: commands succeeded
    py36-django-20: commands succeeded
    congratulations :)

.. _Travis: https://travis-ci.org/bartTC/dpaste
.. _tox: http://tox.readthedocs.org/en/latest/
.. _pipenv: https://docs.pipenv.org/
