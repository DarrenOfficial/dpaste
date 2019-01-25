.. _project_installation:

====================
Project Installation
====================

.. important:: This documentation describes the installation of dpaste
    into an existing Django project. If you want to run the application
    standalone, see :ref:`standalone_installation`.

.. note:: Misaka, the Markdown renderer used in dpaste may need "dev" packages
    for compilation on Debian based Linux distributions. Install it with
    ``sudo apt install python3.5-dev``.

Install the latest dpaste release in your environment. This will install all
necessary dependencies of dpaste as well:

.. code-block:: bash

    $ pip install dpaste

Add ``dpaste.apps.dpasteAppConfig`` to your ``INSTALLED_APPS`` list:

.. code-block:: python

    INSTALLED_APPS = (
        'django.contrib.sessions',
        # ...
        'dpaste.apps.dpasteAppConfig',
    )

Add ``dpaste`` and the (optiona) ``dpaste_api`` url patterns:

.. code-block:: python

    urlpatterns = patterns('',
        # ...

        url(r'my-pastebin/', include('dpaste.urls.dpaste')),
        url(r'my-pastebin/api/', include('dpaste.urls.dpaste_api')),
    )

Finally, migrate the database schema:

.. code-block:: bash

    $ manage.py migrate dpaste


