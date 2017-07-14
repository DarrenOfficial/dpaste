============
Installation
============

Ready to contribute? Here's how to set up `dpaste` for local development.

1. Fork the `dpaste` repo on GitHub.
2. Clone your fork locally::

    $ git clone https://github.com/<your_username>/dpaste.git

3. Install your local copy into a virtualenv. Assuming you have virtualenvwrapper installed, this is how you set up your fork for local development::

    $ mkvirtualenv dpaste
    $ cd dpaste/
    $ pip install -r requirements.txt

4. Copy the settings file and edit it, to meet your needs::

    $ cp dpaste/settings/local.py.example dpaste/settings/local.py
    $ nano dpaste/settings/local.py

5. Initialze the database by running the command::

    $ python manage.py migrate

6. Start up the webserver::

    $ python manage.py runserver
