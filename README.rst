======
dpaste
======

.. image:: https://travis-ci.org/bartTC/dpaste.png?branch=master
    :target: https://travis-ci.org/bartTC/dpaste
.. image:: https://coveralls.io/repos/bartTC/dpaste/badge.png?branch=master
    :target: https://coveralls.io/r/bartTC/dpaste?branch=master

dpaste is a Django based pastebin. It's intended to run separately but its also
possible to be installed into an existing Django project like a regular app.

You can find a live example on http://dpaste.de/

-----------------------------
Testing and local development
-----------------------------

dpaste is continuously tested on _Travis. You can also run the test
suite locally with _tox::

    $ cd dpaste/
    $ pip install tox
    $ tox

A more manual approach is installing it all by hand in a virtual environment.
This is also the preferred way to setup an environment for local development::

    $ cd dpaste/
    $ pip install -e .
    $ pip install -r requirements.txt
    $ python runtests.py

_Travis: https://travis-ci.org/bartTC/dpaste
_tox: http://tox.readthedocs.org/en/latest/

-----------------------------------------
Integrate dpaste into an existing project
-----------------------------------------

Dpaste needs at least Django 1.4+ and is tested on Python 2.7 as well as
Python 3.3.

Install the latest dpaste release in your environment. This will install all
necessary dependencies of dpaste as well::

    pip install dpaste

Add `dpaste` and (preferred) `south` to your `INSTALLED_APPS`::

    INSTALLED_APPS = (
        'django.contrib.sessions',
        'django.contrib.staticfiles',
        # ...

        'mptt',
        'dpaste',
        # 'south', (supported)
    )

Add ``dpaste`` and if you want the ``dpaste_api`` to your urlpatterns::

    urlpatterns = patterns('',
        # ...

        url(r'pastebin/', include('dpaste.urls.dpaste')),
        url(r'pastebin/api/', include('dpaste.urls.dpaste_api')),
    )

Finally just ``syncdb`` or if you use South, migrate::

    manage.py migrate dpaste

Do not forget to setup a cron job to purge expired snippets. You need to
run the management command ``cleanup_snippets``. A cron job I use looks like::

    30 * * * * /srv/dpaste.de/bin/python /srv/dpaste.de/bin/manage.py cleanup_snippets > /dev/null

Note also that dpaste does *not* come with Django admin integration. You need
to setup an register the models in an ``admin.py`` yourself.
