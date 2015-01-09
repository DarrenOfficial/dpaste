=============================
Testing and local development
=============================

dpaste is continuously tested on Travis_. You can also run the test
suite locally with tox_::

    $ cd dpaste/
    $ pip install tox
    $ tox --skip-missing-interpreters

A more manual approach is installing it all by hand in a virtual environment.
This is also the preferred way to setup an environment for local development::

    $ cd dpaste/
    $ pip install -e .
    $ pip install -r requirements.txt
    $ python runtests.py

.. _Travis: https://travis-ci.org/bartTC/dpaste
.. _tox: http://tox.readthedocs.org/en/latest/
