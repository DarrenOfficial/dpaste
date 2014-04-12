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

4. Run the commands::

    $ python manage.py syncdb
    $ python manage.py migrate

5. Start up the webserver::

    $ python manage.py runserver
