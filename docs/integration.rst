=========================================
Integrate dpaste into an existing project
=========================================

Install the latest dpaste release in your environment. This will install all
necessary dependencies of dpaste as well::

    pip install dpaste

Add ``dpaste.apps.dpasteAppConfig`` to your ``INSTALLED_APPS``::

    INSTALLED_APPS = (
        'django.contrib.sessions',
        'django.contrib.staticfiles',
        # ...
        'dpaste.apps.dpasteAppConfig',
    )

Add ``dpaste`` — and if you want — the ``dpaste_api`` to your urlpatterns::

    urlpatterns = patterns('',
        # ...

        url(r'pastebin/', include('dpaste.urls.dpaste')),
        url(r'pastebin/api/', include('dpaste.urls.dpaste_api')),
    )

Finally just migrate the database schema::

    manage.py migrate dpaste


Purge expired snippets
======================

Do not forget to setup a cron job to purge expired snippets. You need to
run the management command ``cleanup_snippets``. A cron job I use looks like::

    30 * * * * /srv/dpaste.de/bin/python /srv/dpaste.de/bin/manage.py cleanup_snippets > /dev/null

Note also that dpaste does *not* come with Django admin integration. You need
to setup an register the models in an ``admin.py`` yourself.

.. note::

    For further customization see :doc:`settings`.
