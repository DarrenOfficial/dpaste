# Changelog

## 4.0

### Abuse filter

- Snippets which link to other pastebins, `.onion` hidden services, file
  sharing providers or a blocked domain are rejected, in the form and the API.
- Existing snippets are checked again on every view and deleted if they are
  detected. A snippet is deleted as well if a visitor arrives with an HTTP
  Referer of a pastebin, hidden service, file sharing provider or blocked
  domain.
- New `blocklist` management command to maintain a domain blocklist in the
  database (`add`, `import`, `remove`, `list`).
- Keywords: a link is detected if its hostname contains a keyword of the new
  `ABUSE_KEYWORDS` option or of the file set with `ABUSE_KEYWORDS_FILE`
  (`DPASTE_ABUSE_KEYWORDS_FILE`). The file is reloaded when it changes.
- New `purge_abuse` management command, which is also run by
  `cleanup_snippets`.
- New `ABUSE_CONTACT` option, displayed on the About page, next to each snippet
  and in the rejection message.

### Features

- Snippets have an optional title, in the form and the API (`title`). The
  `<title>` of a snippet page is its title or the first line of its content
  (#129).
- The number of views is displayed next to each snippet (#155).
- Link previews of messengers and social networks no longer count as a view
  and no longer destroy One-Time snippets (#245).

### Fixes

- Compatible with all Pygments versions from 2.12 on, the upper version limit
  is gone (#208).
- The snippet link is built from the new `BASE_URL` option
  (`DPASTE_BASE_URL`), the Sites framework or the host of the request, in the
  user interface and the API. The API no longer returns links to
  `dpaste-base-url.example.org`. New `USE_X_FORWARDED_HOST` environment
  variable (#266).
- The API enforces `MAX_CONTENT_LENGTH`.
- The database password is no longer written to the log on startup.

### Upgrade notes

- Requires Python 3.10+ and Django 5.2+.
- Requires django-csp 4.0+. If you override the `CSP_*` settings, migrate them
  to the `CONTENT_SECURITY_POLICY` setting.
- Run `manage.py migrate`.
- The honeypot form field was renamed from `title` to `website`. Custom
  form templates need to render `form.website` hidden and may render
  `form.title` as a regular field.
- `dpasteAppConfig.get_base_url` is a regular method now. Overrides declared
  as `@staticmethod` keep working.
- The unused `ratelimiter` dependency was removed, `uglify-es` was replaced
  with `terser`, and packaging moved from `setup.cfg` to `pyproject.toml`.
