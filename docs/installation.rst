.. _installation:

============
Installation
============

There are various ways to install and deploy dpaste. See the guides below:

dpaste with Docker
==================

dpaste Docker images are available to pull from the `Docker Hub`_.

Quickstart to run a dpaste container image:

.. code:: bash

    $ docker run --rm -p 8000:8000 barttc/dpaste:latest

The dpaste image serves the project using uWSGi and is ready for production-like
environments. However it's encouraged to use an external database to store the
data. See the example below for all available options, specifically
``DATABASE_URL``:

.. code:: bash

    $ docker run --rm --name db1 --detach postgres:latest
    $ docker run --rm -p 12345:12345 \
          --link db1 \
          -e DATABASE_URL=postgres://postgres@db1:5432/postgres \
          -e DEBUG=True \
          -e SECRET_KEY=very-secret-key \
          -e PORT=12345 \
          barttc/dpaste:latest

.. _Docker Hub: https://hub.docker.com/r/barttc/dpaste

Integration into an existing Django project
===========================================

Install the latest dpaste release in your environment. This will install all
necessary dependencies of dpaste as well:

.. code-block:: bash

    $ pip install dpaste

Add ``dpaste.apps.dpasteAppConfig`` to your ``INSTALLED_APPS`` list:

.. code-block:: python

    INSTALLED_APPS = (
        'django.contrib.sessions',
        # ...
        'dpaste.apps.dpasteAppConfig',
    )

Add ``dpaste`` and the (optiona) ``dpaste_api`` url patterns:

.. code-block:: python

    urlpatterns = patterns('',
        # ...

        url(r'my-pastebin/', include('dpaste.urls.dpaste')),
        url(r'my-pastebin/api/', include('dpaste.urls.dpaste_api')),
    )

Finally, migrate the database schema:

.. code-block:: bash

    $ manage.py migrate dpaste

dpaste with docker-compose for local development
================================================

The project's preferred way for local development is docker-compose:

.. code:: bash

    $ docker-compose up

This will open the Django runserver on http://127.0.0.1:8000. Changes to the
code are automatically reflected in the Docker container and the runserver
will reload automatically.

Upon first run you will need to migrate the database. Do that in a separate
terminal window:

.. code:: bash

    $ docker-compose run --rm app ./manage.py migrate

dpaste with virtualenv for local development
============================================

If you prefer the classic local installation using Virtualenv then you can
do so. There's no magic involved.

Example:

.. code:: bash

    $ python3 -m venv .venv
    $ source .venv/bin/activate
    $ pip install -e .[dev]
    $ ./manage.py migrate
    $ ./manage.py runserver


CSS and Javascript development
==============================

Static files are stored in the ``client/`` directory and must get compiled
and compressed before being used on the website.

.. code:: bash

    $ npm install

There are some helper scripts you can invoke with ``make``

make js
    Compile only JS files.
make css
    Compile only CSS files.
make css-watch
    Same as ``build-css`` but it automatically watches for changes in the
    CSS files and re-compiles it.

After compilation the CSS and JS files are stored in ``dpaste/static/``
where they are picked up by Django (and Django's collectstatic command).

.. note::
    These files are not commited to the project repository, however they are
    part of the pypi wheel package, since users couldn't compile those once
    they are within Python's site-packages.

