.. _settings:

========
Settings
========

When dpaste is installed as a standalone service or integrated into an existing
project there are various settings you can override to adjust dpaste's
behavior.


To do so, you need to override dpaste's AppConfig. This is a feature
`introduced in Django 1.9`_ and allows you to set settings more
programmatically.

See :ref:`current_appconfig` for a full list of settings and functions you
can override.

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

.. _current_appconfig:

Current AppConfig with default values
=====================================

This is the file content of ``dpaste/apps.py``:

.. literalinclude:: ../dpaste/apps.py
    :language: python
