.. _testing:

=======
Testing
=======

Testing with Tox
================

dpaste is continuously tested online with Travis_. You can also run the test
suite locally with tox_. Tox automatically tests the project against multiple
Python and Django versions.

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
