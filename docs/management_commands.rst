.. _management_commands:

===================
Management Commands
===================

.. _purge_expired_snippets:

Purge expired snippets
======================

Snippets are removed as soon as they exceed their expiration
date and get fetched by a client, however if they never get fetched this isn't
triggered. dpaste ships with a management command ``cleanup_snippets`` that
removes these expired snippets.

It's sufficient to run it daily.

To run it locally do:

.. code-block:: bash

    $ pipenv run ./managepy cleanup_snippets

Options
-------

--dry-run   Does not actually delete the snippets.
            This is useful for local testing.

Setup a Crontab
---------------

A crontab line might look like:

.. code-block:: bash

    1 20 * * * /srv/dpaste.de/pipenv run manage.py cleanup_snippets > /dev/null


.. note:: If you use the *database* session backend, you may also need to setup
    a crontab that removes the expired entries from the session database.

    See the related `Django Documentation`_ for details.

.. _Django Documentation: https://docs.djangoproject.com/en/2.0/ref/django-admin/#django-admin-clearsessions
