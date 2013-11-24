=================================================
How to integrate dpaste into an existing project:
=================================================

You already have a full Django based project running. If not, and you still
want to proceed just create a simple barebone project:

    $ mkvirtualenv dpaste-example
    $ pip install django south
    $ django-admin.py startproject myproject

Install the latest dpaste release in your envoirenment. This will install all
necessary dependencies of dpaste as well, **except Django and South**. Since
you here integrate dpaste into your project its likely those are already
installed::

    pip install https://github.com/bartTC/dpaste

Add `dpaste` and (preferred) `south` to your `INSTALLED_APPS`::

    INSTALLED_APPS = (
        'django.contrib.sessions',
        'django.contrib.staticfiles',
        # ...

        'dpaste',
        'south',
    )

Add `dpaste` and if you want the `dpaste_api` to your urlpatterns:

    urlpatterns = patterns('',
        # ...

        url(r'pastebin/', include('dpaste.urls.dpaste')),
        url(r'pastebin/api/', include('dpaste.urls.dpaste_api')),
    )

Finally just migrate:

    manage.py migrate dpaste
