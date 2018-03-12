==================================
Installation for local development
==================================

Local development is done with `pipenv`_ to maintain packages. 

Installation::

    $ cd dpaste/
    $ pipenv install --three --dev

Copy the settings file and edit it, to meet your needs::

    $ cp dpaste/settings/local.py.example dpaste/settings/local.py
    $ nano dpaste/settings/local.py

Run the testsuite::

    $ pipenv run ./runtests.py

To run the project on your local machine::

    $ pipenv run ./manage.py migrate
    $ pipenv run ./manage.py runserver

.. _pipenv: https://docs.pipenv.org/
