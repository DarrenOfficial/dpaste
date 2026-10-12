Dpaste
---
![dpaste image](https://img.shields.io/pypi/v/dpaste.svg)
[![Python CI](https://github.com/DarrenOfficial/dpaste/actions/workflows/python.yml/badge.svg)](https://github.com/DarrenOfficial/dpaste/actions/workflows/python.yml)
[![Docker Image CI](https://github.com/DarrenOfficial/dpaste/actions/workflows/docker.yml/badge.svg)](https://hub.docker.com/r/darrenofficial/dpaste)
![Code Quality](https://api.codacy.com/project/badge/Grade/185cfbe9b4b447e59a40f816c4a5ebf4)

----

📖 Full documentation on [https://docs.dpaste.org](https://docs.dpaste.org)


dpaste is a [pastebin](https://en.wikipedia.org/wiki/Pastebin) application written in [Python](https://www.python.org/) using the [Django](https://www.djangoproject.com/) framework. You can find a live installation on [dpaste.org.](https://dpaste.org)

The project is intended to run standalone as any regular Django Project, but it's also possible to install it into an existing project as a typical Django application.


The code is open source and available on Github: [https://github.com/darrenofficial/dpaste](https://github.com/darrenofficial/dpaste). If you found bugs, have problems or ideas with the project or the website installation, please create an *Issue* there.

⚠️ dpaste requires at a minimum Python 3.10 and Django 5.2.

## Configuration

All options are attributes of the `dpasteAppConfig` class in
[dpaste/apps.py](dpaste/apps.py), which you override in a subclass in your
`settings/local.py` (see [local.py.example](dpaste/settings/local.py.example)).
A few are available as environment variables as well:

| Variable | Description |
|---|---|
| `DATABASE_URL` | Database to use, e.g. `postgres://user:password@host/dpaste`. |
| `SECRET_KEY` | Django's secret key. Set this in production. |
| `ALLOWED_HOSTS` | Comma separated list of hostnames. |
| `DPASTE_BASE_URL` | Public URL of the installation, e.g. `https://paste.example.org`. Used for the links to snippets. If it's not set, the hostname of the request is used. |
| `USE_X_FORWARDED_HOST` | Set to `True` if your reverse proxy passes the public hostname in `X-Forwarded-Host` rather than `Host`. |
| `DPASTE_ABUSE_CONTACT` | Email address or URL to report abuse to. Displayed on the About page and next to each snippet. |

## Abuse filter

Public pastebins are abused to pass around links to illegal material. dpaste
detects the characteristics those snippets share, refuses to store them and
deletes the ones which are already stored. A deleted snippet is gone, no copy
is kept. Detected are:

- links to other pastebins,
- links to `.onion` hidden services,
- links to file sharing providers,
- links to any domain on your blocklist,
- visits with an HTTP Referer from any of the above.

Snippets are checked when they are created, every time they are viewed and
when the `cleanup_snippets` management command runs, which you should have in
your crontab anyway:

    */15 * * * * /path/to/manage.py cleanup_snippets

The list of pastebins and file sharing providers is built in. Your own
blocklist is kept in the database and managed on the command line. A blocked
domain includes all of its subdomains, and blocking a domain immediately
deletes all snippets which link to it:

    ./manage.py blocklist add evil.example other.example --note "Reported 2026-10"
    ./manage.py blocklist import domains.txt
    ./manage.py blocklist list
    ./manage.py blocklist remove evil.example
    ./manage.py purge_abuse --dry-run

The filter is strict by design and will reject some harmless snippets, such as
one with a link to a file on Google Drive. Set `ABUSE_CONTACT` so people can
tell you, and see the `ABUSE_*` and `ALLOWED_LINK_DOMAINS` options in
[dpaste/apps.py](dpaste/apps.py) to loosen it or turn parts of it off.


dpaste.org: https://dpaste.org/
pastebin: https://en.wikipedia.org/wiki/Pastebin
