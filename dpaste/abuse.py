"""
Abuse filter.

Public pastebins attract link dumps: a snippet that is nothing but a pointer
to illegal material hosted elsewhere. Those snippets share a handful of
characteristics that legitimate code snippets rarely have, and this module
detects them:

- links to other pastebins,
- links to ``.onion`` hidden services,
- links to file sharing providers,
- links to any domain on the operator's own blocklist,
- links to any hostname which contains one of the operator's keywords,
- visits arriving with an HTTP Referer from any of the above.

A detected snippet is never stored; one which is already in the database is
deleted the moment it is detected. Nothing of it is kept, and nobody is told
what was detected: the only trace is a line in the log.
"""

import os
import re
import time
import unicodedata
from collections import ChainMap, namedtuple
from logging import getLogger
from urllib.parse import urlsplit

from django.apps import apps
from django.db.models import F
from django.utils import timezone

logger = getLogger(__name__)
config = apps.get_app_config("dpaste")

REASON_ONION = "onion"
REASON_PASTEBIN = "pastebin"
REASON_FILEHOST = "filehost"
REASON_BLOCKLIST = "blocklist"
REASON_KEYWORD = "keyword"

# What was found (`reason` is one of the REASON_* keys, `domain` the entry
# of the list that matched) and where (`source` is "content" or "referer").
Match = namedtuple("Match", ("reason", "domain", "source"))

# Tor v3 hidden service address. This intentionally has no word boundaries,
# so addresses behind a tor2web gateway (<address>.onion.ws) match as well.
ONION_RE = re.compile(r"[a-z2-7]{56}\.onion", re.IGNORECASE)

# Anything that looks like a hostname, with or without a scheme in front of
# it. The lookbehind makes sure we start at the beginning of a name, which
# also keeps this linear on long runs of characters such as base64 blobs.
HOST_RE = re.compile(
    r"(?<![a-z0-9_.\-])"
    r"((?:[a-z0-9](?:[a-z0-9\-]{0,61}[a-z0-9])?\.)+[a-z][a-z0-9\-]{1,62})"
    r"(?![a-z0-9_\-])",
    re.IGNORECASE,
)

# example[.]com, example(dot)com, example{.}com
DEFANGED_DOT_RE = re.compile(r"\s*[\[({]\s*(?:\.|dot)\s*[\])}]\s*", re.IGNORECASE)

# Zero-width and other invisible characters used to break up a hostname.
INVISIBLE_CHARS = dict.fromkeys(
    (0x00AD, 0x200B, 0x200C, 0x200D, 0x2060, 0xFEFF), None
)


# A comment in a blocklist file starts with // or # and runs to the end of
# the line. It has to be at the start of the line or follow a space, so the
# slashes of a URL are not mistaken for one.
LIST_COMMENT_RE = re.compile(r"(?:^|\s)(?://|#).*$")

# Keywords shorter than this match too many harmless hostnames.
KEYWORD_MIN_LENGTH = 4


def parse_list(text):
    """
    Read the entries of a blocklist file. That is one entry per line, in
    the most simple case. Quotes, trailing commas, comments and the lines
    which open or close a list are ignored, so a list which was written as
    source code can be used as it is::

        // Why these are blocked
        BLOCKED = [
            'filehost.example',
            'badsite.', // they move TLDs a lot
        ]
    """
    entries = []
    for line in text.splitlines():
        line = LIST_COMMENT_RE.sub("", line).strip().rstrip(",;").strip()
        if not line or line[-1] in "[({" or line in ("]", ")", "}"):
            continue
        entry = line.strip("'\"").strip().lower()
        if entry:
            entries.append(entry)
    return entries


def normalize_domain(value):
    """
    Reduce a domain, hostname or URL to the bare lowercase hostname which
    is stored in the blocklist. Returns an empty string if there is none.
    """
    value = (value or "").strip().lower()
    if not value:
        return ""
    if "//" not in value:
        value = f"//{value}"
    try:
        host = urlsplit(value).hostname or ""
    except ValueError:
        return ""
    host = host.strip(".")
    if host.startswith("*."):
        host = host[2:]
    if host.startswith("www."):
        host = host[4:]
    try:
        host = host.encode("idna").decode("ascii")
    except UnicodeError:
        pass
    return host


def normalize_text(text):
    """
    Undo the common tricks to hide a hostname from a filter.
    """
    if not text.isascii():
        text = unicodedata.normalize("NFKC", text).translate(INVISIBLE_CHARS)
    return DEFANGED_DOT_RE.sub(".", text)


def extract_hosts(text):
    """
    Set of all hostnames found in a text.
    """
    return {host.lower() for host in HOST_RE.findall(text)}


# -----------------------------------------------------------------------------
# Blocklist
# -----------------------------------------------------------------------------

_db_blocklist = {"domains": {}, "loaded": None}


def clear_cache(**kwargs):
    """
    Forget the cached blocklist of the database and the keywords file.
    Connected to the save and delete signals of the BlockedDomain model.
    """
    _db_blocklist["loaded"] = None
    _file_keywords.update(keywords=(), path=None, mtime=None, checked=None)


def get_db_blocklist():
    """
    The domains the operator has blocked. They are cached in the process for
    a short moment, so viewing a snippet does not cost an extra query.
    """
    loaded = _db_blocklist["loaded"]
    if loaded is None or time.monotonic() - loaded > config.ABUSE_BLOCKLIST_CACHE:
        from dpaste.models import BlockedDomain

        _db_blocklist["domains"] = dict.fromkeys(
            BlockedDomain.objects.values_list("domain", flat=True), REASON_BLOCKLIST
        )
        _db_blocklist["loaded"] = time.monotonic()
    return _db_blocklist["domains"]


_file_keywords = {"keywords": (), "path": None, "mtime": None, "checked": None}


def get_file_keywords():
    """
    The keywords of the ``ABUSE_KEYWORDS_FILE``. The file is read again
    when it has changed, so it can be edited while the server is running.
    """
    path = config.ABUSE_KEYWORDS_FILE
    if not path:
        return ()

    cache = _file_keywords
    checked = cache["checked"]
    if (
        cache["path"] == path
        and checked is not None
        and time.monotonic() - checked <= config.ABUSE_BLOCKLIST_CACHE
    ):
        return cache["keywords"]

    if cache["path"] != path:
        cache.update(keywords=(), mtime=None)
    cache.update(path=path, checked=time.monotonic())
    try:
        mtime = os.stat(path).st_mtime
        if mtime != cache["mtime"]:
            with open(path, encoding="utf-8") as f:
                cache.update(keywords=tuple(parse_list(f.read())), mtime=mtime)
    except OSError as e:
        # Keep what was loaded before, a filter which silently stops to
        # work is worse than one which is a few entries behind.
        logger.error("Abuse filter can't read the keywords file %s: %s", path, e)
    return cache["keywords"]


def get_keywords():
    """
    All keywords, the ones of the settings and the ones of the keywords file.
    A hostname which contains a keyword is blocked.
    """
    keywords = [str(k).strip().lower() for k in config.ABUSE_KEYWORDS]
    keywords.extend(get_file_keywords())
    return tuple(dict.fromkeys(k for k in keywords if len(k) >= KEYWORD_MIN_LENGTH))


def get_blocklist():
    """
    Mapping of every blocked domain to the reason it is blocked for. The
    blocklist of the database can be large, so it is chained, not copied.
    """
    builtin = {}
    if config.ABUSE_BLOCK_FILEHOSTS:
        builtin.update(dict.fromkeys(config.ABUSE_FILEHOST_DOMAINS, REASON_FILEHOST))
    if config.ABUSE_BLOCK_PASTEBINS:
        builtin.update(dict.fromkeys(config.ABUSE_PASTEBIN_DOMAINS, REASON_PASTEBIN))
    return ChainMap(get_db_blocklist(), builtin)


def get_allowed_domains(request=None):
    """
    Domains which are never blocked: the ones the operator has allowed and
    this very installation, so snippets can link to each other.
    """
    allowed = {normalize_domain(d) for d in config.ALLOWED_LINK_DOMAINS}
    allowed.add(normalize_domain(config.get_base_url(request=request)))
    if request is not None:
        allowed.add(normalize_domain(request.get_host()))
    allowed.discard("")
    return allowed


def domain_suffixes(host):
    """
    'a.b.example.com' -> 'a.b.example.com', 'b.example.com', 'example.com', 'com'
    """
    labels = host.split(".")
    return [".".join(labels[i:]) for i in range(len(labels))]


def match_host(host, blocklist, allowed, keywords=()):
    """
    Check a single hostname. Returns a `(reason, entry)` tuple with the
    blocklist entry the hostname or one of its parent domains is listed
    under, or the keyword it contains. Returns None if it's fine.
    """
    suffixes = domain_suffixes(host)
    if any(suffix in allowed for suffix in suffixes):
        return None
    for suffix in suffixes:
        if suffix in blocklist:
            return blocklist[suffix], suffix
    for keyword in keywords:
        if keyword in host:
            return REASON_KEYWORD, keyword
    return None


# -----------------------------------------------------------------------------
# Scanning
# -----------------------------------------------------------------------------


def scan_text(text, request=None, source="content"):
    """
    Check a text for links which are not allowed. Returns a `Match` for
    the first one found, otherwise None.
    """
    if not config.ABUSE_FILTER_ENABLED or not text:
        return None

    text = normalize_text(text)

    if config.ABUSE_BLOCK_ONION:
        onion = ONION_RE.search(text)
        if onion:
            return Match(REASON_ONION, onion.group(0).lower(), source)

    blocklist = get_blocklist()
    keywords = get_keywords()
    if not blocklist and not keywords:
        return None

    allowed = get_allowed_domains(request)
    for host in sorted(extract_hosts(text)):
        found = match_host(host, blocklist, allowed, keywords)
        if found:
            return Match(found[0], found[1], source)
    return None


def scan_referer(request):
    """
    Check where a visitor is coming from. Snippets which are linked on other
    pastebins, hidden services or blocked domains are part of a link chain.
    """
    if not config.ABUSE_FILTER_ENABLED or not config.ABUSE_CHECK_REFERER:
        return None
    referer = request.headers.get("Referer", "")
    host = normalize_domain(referer)
    if not host:
        return None
    return scan_text(host, request=request, source="referer")


def scan_snippet(snippet, request=None):
    """
    Check the title and content of a snippet.
    """
    return scan_text(f"{snippet.title}\n{snippet.content}", request=request)


def record_hit(match):
    """
    Log a detection and count it on the blocklist entry. The log line is the
    only trace which is kept, it never contains snippet content.
    """
    logger.warning(
        "Abuse filter hit: %s (%s) in %s", match.reason, match.domain, match.source
    )
    if match.reason == REASON_BLOCKLIST:
        from dpaste.models import BlockedDomain

        BlockedDomain.objects.filter(domain=match.domain).update(
            hits=F("hits") + 1, last_hit=timezone.now()
        )


def purge_snippets(dry_run=False):
    """
    Check every snippet in the database and delete the ones which are
    detected. Returns a list of `(secret_id, Match)` tuples.
    """
    from dpaste.models import Snippet

    detected = []
    queryset = Snippet.objects.only("secret_id", "title", "content").order_by("pk")
    for snippet in queryset.iterator(chunk_size=200):
        match = scan_snippet(snippet)
        if match:
            detected.append((snippet.secret_id, match))

    if not dry_run:
        for secret_id, match in detected:
            record_hit(match)
            Snippet.objects.filter(secret_id=secret_id).delete()

    return detected
