dpaste
======

[![Build Status](https://travis-ci.org/bartTC/dpaste.png?branch=master)](https://travis-ci.org/bartTC/dpaste)
[![Coverage Status](https://coveralls.io/repos/bartTC/dpaste/badge.png?branch=master)](https://coveralls.io/r/bartTC/dpaste?branch=master)

dpaste is a Django based pastebin. It's intended to run separatly or installed
into an existing Django project.

You can find a live example on http://dpaste.de/

Testing
-------

dpaste is continuously tested on [Travis][travis]. You can also run the test
suite locally with [tox][tox]:

    $ pip install tox
    $ tox

A more manual approach is installing it all by hand in a virtual environment.
This is also the preferred way local development:

    $ pip install -e .
    $ pip install -r requirements.txt
    $ python runtests.py

[travis]: https://travis-ci.org/bartTC/dpaste
[tox]: http://tox.readthedocs.org/en/latest/
