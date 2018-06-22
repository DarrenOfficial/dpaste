.. _local_development:

=================
Local Development
=================


Installation for local development
==================================

Local development is done with `pipenv`_ to maintain packages.

Installation::

    $ cd dpaste/

    $ npm install
    $ pipenv install --dev

Copy the settings file and edit it, to meet your needs::

    $ cp dpaste/settings/local.py.example dpaste/settings/local.py
    $ nano dpaste/settings/local.py

Run the testsuite::

    $ pipenv run ./runtests.py

To run the project on your local machine::

    $ pipenv run ./manage.py migrate
    $ pipenv run ./manage.py runserver


Testing
=======

dpaste is continuously tested on Travis_. You can also run the test
suite locally with tox_::

    $ cd dpaste/
    $ pip install tox
    $ tox

A more manual approach is installing it all by hand in a virtual environment.
This is also the preferred way to setup an environment for local development::

    $ cd dpaste/
    $ pipenv install --dev
    $ pipenv run ./runtests.py

.. _Travis: https://travis-ci.org/bartTC/dpaste
.. _tox: http://tox.readthedocs.org/en/latest/
.. _pipenv: https://docs.pipenv.org/
