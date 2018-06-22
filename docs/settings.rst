==========================
Settings and Configuration
==========================

When dpaste is installed as a standalone service or integrated into an existing
project there are various settings you can override to adjust dpaste's
behavior.


To do so, you need to override dpaste's AppConfig. This is a feature
`introduced in Django 1.9`_ and allows you to set settings more programmatically.

Please see the source of ``dpaste.apps.dpasteAppConfig`` for a full list
of settings and functions you can override.


Example for your custom AppConfig:
==================================


.. code-block:: python

    # settings.py
    from dpaste.apps import dpasteAppConfig

    class MyBetterDpasteAppConfig(dpasteAppConfig):
        SLUG_LENGTH = 8
        LEXER_DEFAULT = 'js'

    # ...

    INSTALLED_APPS = [
        'myproject.settings.MyBetterDpasteAppConfig',
    ]

.. _introduced in Django 1.9: https://docs.djangoproject.com/en/1.9/ref/applications/
