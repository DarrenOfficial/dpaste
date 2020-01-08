Changelog
=========

3.5 (2020-01-08)
----------------

- Mobile view improvements.
- Upgraded django-csp dependency to v3.6 that ships with Django 3.0 support.

3.4 (2019-12-08)
----------------

- Dropped support for Python 3.4.
- Dropped support for Python 3.5.
- Dropped support for Django 1.11. ⚠️
- Dropped support for Django 2.0. ⚠️
- Dropped support for Django 2.1. ⚠️
- Added support for Python 3.8.
- Added support for Django 3.0.
- Snippets which are expired are now deleted as soon as they are requested
  by a client. It's not necessary to purge them minutely with the
  ``cleanup_snipppet`` managemenent command. It's still encouraged to have the
  management command setup, just run it daily, so snippets which expired but
  never got fetched by a client are deleted properly.
- All pages have sane Expire or Max-Age header.
- Onetime snippets which were never viewed a second time are now deleted if
  they reach the default expire date.
- New AppConfig setting ``APPLICATION_NAME`` that can be used to replace the
  term "dpaste" throughout the UI.
- New AppConfig setting ``EXTRA_HEAD_HTML`` and similars that can be used to
  add custom HTML to each template, to easily override the stock UI of dpaste.
- New "Slim" view that displays the highlighted snippet without header,
  options etc, and can be iframed.
- Forced line-break for superlongwordsthatwouldexceedthecanvas.
- Local development is no longer centered around ``pipenv``, instead it's using
  docker-compose or the classic virtualenv based setups.
- Error pages are now correctly translated.
- Testsuite and Tox uses pytest instead of a homebrewed testrunner.

3.3.1 (2019-08-04):
-------------------

- Exclude the local settings file from the pypi release.

3.3 (2019-07-12)
----------------

- The compiled static files (CSS, JS) are now shipped with the Pypi package since
  its not possible to compile them after installation with pip.

3.2 (2019-06-24)
----------------

- "Edit Snippet" panel is now hidden by default to remove visual noise.
- Linux/Unix browsers now use Ctrl+Enter as a shortcut to submit the form.
- Added a dedicated "Copy Snippet" button to copy the content to the clipboard.
- Added "View Raw" option to optionally render the 'raw' snippet content with a
  template rather served as plain text. This was added to hinder abuse.
- Added "Json" to the list of lexers.
- Added 'JSX/React" to the list of lexers.

3.1 (2019-05-16)
----------------

- Django 2.1 support and tests.
- Django 2.2 support and tests.
- General code cleanup by running the entire codebase through black_.
- Right-to-left support for text snippets.
- dart-sass is now used for SASS compilation.
- Updated lexer list.
- "View Raw" feature can be disabled in app config to hinder abuse.

.. _black: https://github.com/ambv/black

3.0 (2018-06-22)
----------------

Huge release. Full cleanup and update of the entire codebase. Details:

- Requires Python 3.4 and up.
- Dropped support for Django 1.8 to 1.10 due to it's general end of support.
  The project will likely work well but it's no longer specifically tested.
- All views are now class based and use the latest generic based views sugar.
- Django 1.11 based templates, forms, views, models, etc.
- Added pipenv support for local development.
- Added AppConfig support to set and maintain settings.
- Added "Rendered Text" lexer with support for rST and Markdown.
- Added Content Security Policy features, with django-csp (this is mainly
  required for the "rendered" text feature).
- Removed jQuery dependency, all Javascript is native.
- Removed Bootstrap dependency.
- Removed 'Maximum History' limit setting.
- Removed translations.
- Removed "Suspicious" middleware which was never been used, documented,
  and also not functional for a while.
- Fixed issues around leading whitespace in lines.
- Fixed CMD+Enter form submission shortcut in Firefox.

2.14 (no public release)
------------------------

- Django 1.11 compatibility. But not Django 2.0 yet.
- Removed "Suspicious" middleware which was never been used, documented,
  and also not functional for a while.

2.13 (2017-01-20)
-----------------

- (Backwards incompatible) Removal of django-mptt and therefor the removal of a
  tree based snippet list, due to performance reasons with large snippet counts.
  Snippets still have a 'parent' relation if it's an answer of another snippet,
  however this is no longer a Nested Set. The UI is simplified too and the user
  can now only compare an answer to it's parent snippet. I believe this is the
  major use case anyway.
- (Backwards incompatible) Removal of the "Gist" button feature.
- Fixed broken 404 view handler in Django 1.9+.
- Python 3.6 and Django 1.10 compatibility and tests.

2.12 (2016-09-06)
-----------------

- Fixed "Content Type" problem with Django 1.10.
- Development requirements now use a different version scheme to be
  compatible with older `pip` versions.

2.11 (2016-09-04)
-----------------

- Django 1.10 Support
- R Lexer is enabled by default
- Minor fixes and improvements.

2.10 (2016-03-23)
-----------------

- Dropped Django 1.4 and 1.7 support!
- Full Django 1.8 support
- Full Django 1.9 support
- C++ Lexer is enabled by default
- (Backwards incompatible) All API calls must pass the data within a POST
  request. It can't mix POST and GET arguments anymore. This was weird behavior
  anyway and is likely no issue for any paste plugin out there.

2.9 (2015-08-12)
----------------

- Full Django 1.7 support
- Full Django 1.8 support
- New Django migrations, with fallback to South migrations if South is
  installed. If you want to switch from South to native Django migrations,
  and have an existing databsae, fake the initial migrations:
  `manage.py migrate --fake-initial`
- Added full i18n support and several languages
- More settings can be overrridden, like the jQuery URL, site name and wether
  you want to enable Gthub Gist.
- Ships a middleware that blocks anonymous proxies and TOR nodes. Not enabled
  by default.

2.8 (2014-08-02)
----------------

- The API create view has a new argument 'filename' which is used to determine
  the lexer out of a given filename.
- Fixed a XSS bug where HTML tags were not properly escaped with the simple
  ``code`` lexer.

2.7 (2014-06-08)
----------------

- "never" as an expiration choice is enable by default! This creates snippets
  in the database which are never purged.
- The API create call now supports to set the exiration time.
- Some simple Bootstrap 3 support.
- Gist fixes on Python 3.

2.6 (2014-04-12)
----------------

- Fix for the rare case of duplicate slug (secret id) generation.
- A new 'code' lexer renders source code with no highlighting.
- Whitespace fixes with tab indention and word wrap mode.
- Installation docs.


2.5 (2014-01-21)
----------------

- IRC lexer is now in the default lexer list.
- One-Time snippet support. Snippets get automatically deleted after the
  another user looks at it.
- Toggle wordwrap for code snippets.
- General UI and readability improvements.

2.4 (2014-01-11)
----------------

- API accepts the format or lexer via GET too. You can call an API url like
  ``example.com/api/?format=json`` and have the body in POST only.
- Added an option to keep snippets forever.
- ABAP lexer is now in the default lexer list.

2.3 (2014-01-07)
----------------

- API Documentation.
- Full test coverage.
- Removed Twitter button from homepage.
- Slug generation is less predictable.

2.2 (2013-12-18)
----------------

- Added documentation_
- Added support for CSRF middleware.
- Windows users can submit the form using Ctrl+Enter.
- The raw view now sends the X-Content-Type-Options=nosniff header.
- Various constants can now be overridden by settings.
- Support for `python setup.py test` to run the tox suite.

.. _documentation: http://dpaste.readthedocs.org/en/latest/

2.1 (2013-12-14)
----------------

- Changes and fixes along the package management.

2.0 (2013-11-29)
----------------

- A huge cleanup and nearly total rewrite.
- dpaste now includes a Django project which is used on www.dpaste.de
  as well as hooks to get it integrated into existing projcts.
