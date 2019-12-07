======
dpaste
======

.. image:: https://img.shields.io/pypi/v/dpaste.svg
   :target: https://pypi.org/project/dpaste/

.. image:: https://travis-ci.org/bartTC/dpaste.svg?branch=master
   :target: https://travis-ci.org/bartTC/dpaste

.. image:: https://api.codacy.com/project/badge/Coverage/185cfbe9b4b447e59a40f816c4a5ebf4
   :target: https://www.codacy.com/app/bartTC/dpaste

.. image:: https://api.codacy.com/project/badge/Grade/185cfbe9b4b447e59a40f816c4a5ebf4
   :target: https://www.codacy.com/app/bartTC/dpaste

----

📖 Full documentation on https://dpaste.readthedocs.io/

dpaste is a pastebin_ application written in Python using the Django
framework. You can find a live installation on `dpaste.de`_.

.. image:: https://raw.githubusercontent.com/bartTC/dpaste/master/docs/_static/dpaste_de_screenshot.png
   :alt: A screenshot of https://dpaste.de/
   :width: 60%

The project is intended to run standalone as any regular Django Project,
but it's also possible to install it into an existing project as a typical
Django application.

The code is open source and available on Github: https://github.com/bartTC/dpaste.
If you found bugs, have problems or ideas with the project or the website installation,
please create an *Issue* there.

⚠️ dpaste requires at a minimum Python 3.6 and Django 2.2.

Run dpaste using Docker:
========================

Docker images are in `Docker Hub`_.

You can try the latest of dpaste using Docker. This will store the snippet
database in a SQLite file in a Docker volume:

.. code:: bash

    $ docker run --rm -p 8000:8000 barttc/dpaste:latest

If you want to run it in production-like environments, it's encouraged to
use an external database. See the example below for all available options,
specifically ``DATABASE_URL``:

.. code:: bash

    $ docker run --rm --name db1 --detach postgres:latest
    $ docker run --rm -p 12345:12345 \
          --link db1 \
          -e DATABASE_URL=postgres://postgres@db1:5432/postgres \
          -e DEBUG=True \
          -e SECRET_KEY=very-secret-key \
          -e PORT=12345 \
          barttc/dpaste:latest

.. _dpaste.de: https://dpaste.de/
.. _pastebin: https://en.wikipedia.org/wiki/Pastebin
.. _Docker Hub: https://hub.docker.com/r/barttc/dpaste
