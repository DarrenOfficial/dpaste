.. _standalone_installation:

==============================================
Standalone Installation (or local development)
==============================================

.. important:: This documentation describes the installation of dpaste
    as a standalone project, primarily for local development. If you want
    to integrate the application into your existing Django project, see
    :ref:`project_installation`.

The project uses Docker for local development. Start it with:

.. code:: bash

    $ make up

Or if you're more familiar with docker-compose

.. code:: bash

    $ docker-compose run --rm app ./manage.py migrate
    $ docker-compose up

This will open the Django runserver on http://127.0.0.1:8000. Changes to the
code are automatically reflected in the Docker container and the runserver
will reload automatically.

Local development using virtualenv
==================================

If you prefer the classic local installation using Virtualenv then you can
do so. There's nothing magic involved:

.. code:: bash

    $ python3 -m venv .venv
    $ source .venv/bin/activate
    $ pip install -e .[dev]

CSS and Javascript development
==============================

Both [S]CSS and Javascript files need to be compiled and compressed.

Install the necessary node dependencies first:

.. code:: bash

    $ npm install

There are some helper scripts you can invoke with ``make``

``npm js``
    Compile only JS files.
``npm css``
    Compile only CSS files.
``make css-watch``
    Same as ``build-css`` but it automatically watches for changes in the
    CSS files and re-compiles it.
``make docs``
    Compile this documentation. The result will be in ``docs/_build/html``.
``make docs-watch``
    Same as ``docs`` but it automatically watches for changes in the
    documentation files and re-compiles the docs.

.. note:: See ``make help`` for the full and most recent list of
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
