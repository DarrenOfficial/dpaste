Deployment
==========

Staging/Development
-------------------

`Fabric <http://pypi.python.org/pypi/Fabric>`_ is used to allow developers to
easily push changes to a previously setup development/staging environment.
To get started, run the following command from within your virtual
environment::

    pip install fabric==0.9.3
    fab --fabfile src/pastebin/fabfile.py -l

This will install Fabric and provide a list of available commands.

When run from src/pastebin, you can just run ``fab [command]`` (i.e. without
the ``-fabfile`` flag).
