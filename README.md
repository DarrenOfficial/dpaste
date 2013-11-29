dpaste
======

[![Build Status](https://travis-ci.org/bartTC/dpaste.png?branch=master)](https://travis-ci.org/bartTC/dpaste)
[![Coverage Status](https://coveralls.io/repos/bartTC/dpaste/badge.png?branch=master)](https://coveralls.io/r/bartTC/dpaste?branch=master)

dpaste is a Django based pastebin. It's intended to run separatly but its also
possible to be installed into an existing Django project like a regular app.

You can find a live example on http://dpaste.de/

Testing and local development
-----------------------------

dpaste is continuously tested on [Travis][travis]. You can also run the test
suite locally with [tox][tox]:

    $ pip install tox
    $ tox

A more manual approach is installing it all by hand in a virtual environment.
This is also the preferred way to setup an environment for local development:

    $ pip install -e .
    $ pip install -r requirements.txt
    $ python runtests.py

[travis]: https://travis-ci.org/bartTC/dpaste
[tox]: http://tox.readthedocs.org/en/latest/

Integrate dpaste into an existing project
-----------------------------------------

Dpaste needs at Django 1.4+ and is tested on Python 2.7 as well as Python 3.3.

You already have a full Django based project running. If not, and you still
want to proceed just create a simple barebone project:

    $ mkvirtualenv dpaste-example
    $ pip install django south
    $ django-admin.py startproject myproject

Install the latest dpaste release in your envoirenment. This will install all
necessary dependencies of dpaste as well.

    pip install https://github.com/bartTC/dpaste

Add `dpaste` and (preferred) `south` to your `INSTALLED_APPS`:

    INSTALLED_APPS = (
        'django.contrib.sessions',
        'django.contrib.staticfiles',
        # ...

        'mptt',
        'dpaste',
        # 'south', (supported)
    )

Add `dpaste` and if you want the `dpaste_api` to your urlpatterns:

    urlpatterns = patterns('',
        # ...

        url(r'pastebin/', include('dpaste.urls.dpaste')),
        url(r'pastebin/api/', include('dpaste.urls.dpaste_api')),
    )

Finally just `syncdb` or if you use South, migrate:

    manage.py migrate dpaste

Do not forget to setup a cron job to purge expired snippets. You need to
run the management command `cleanup_snippets`. A cron job I use looks like:

    30 * * * * /srv/dpaste.de/bin/python /srv/dpaste.de/bin/manage.py cleanup_snippets > /dev/null

Note also that dpaste does *not* come with Django admin integration. You need
to setup an register the models in an `admin.py` yourself.
