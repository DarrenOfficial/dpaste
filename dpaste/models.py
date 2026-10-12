from logging import getLogger
from random import SystemRandom

from django.apps import apps
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from dpaste import abuse, highlight

config = apps.get_app_config("dpaste")
logger = getLogger(__file__)
R = SystemRandom()


def generate_secret_id(length):
    if length > config.SLUG_LENGTH:
        logger.warning(
            "Slug creation triggered a duplicate, "
            "consider increasing the SLUG_LENGTH."
        )

    secret_id = "".join(
        [R.choice(config.SLUG_CHOICES) for i in range(length or config.SLUG_LENGTH)]
    )

    # Check if this slug already exists, if not, return this new slug
    try:
        Snippet.objects.get(secret_id=secret_id)
    except Snippet.DoesNotExist:
        return secret_id

    # Otherwise create a new slug which is +1 character longer
    # than the previous one.
    return generate_secret_id(length=length + 1)


class Snippet(models.Model):
    EXPIRE_TIME = 1
    EXPIRE_KEEP = 2
    EXPIRE_ONETIME = 3
    EXPIRE_CHOICES = (
        (EXPIRE_TIME, _("Expire by timestamp")),
        (EXPIRE_KEEP, _("Keep Forever")),
        (EXPIRE_ONETIME, _("One-Time snippet")),
    )

    secret_id = models.CharField(
        _("Secret ID"), max_length=255, blank=True, null=True, unique=True
    )
    title = models.CharField(_("Title"), max_length=255, blank=True, default="")
    content = models.TextField(_("Content"))
    lexer = models.CharField(_("Lexer"), max_length=30, default=highlight.LEXER_DEFAULT)
    published = models.DateTimeField(_("Published"), auto_now_add=True)
    expire_type = models.PositiveSmallIntegerField(
        _("Expire Type"), choices=EXPIRE_CHOICES, default=EXPIRE_CHOICES[0][0]
    )
    expires = models.DateTimeField(_("Expires"), blank=True, null=True)
    view_count = models.PositiveIntegerField(_("View count"), default=0)
    rtl = models.BooleanField(_("Right-to-left"), default=False)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        verbose_name=_("Parent Snippet"),
        related_name="children",
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ("-published",)
        db_table = "dpaste_snippet"

    def __str__(self):
        return self.secret_id

    def save(self, *args, **kwargs):
        if not self.secret_id:
            self.secret_id = generate_secret_id(length=config.SLUG_LENGTH)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("snippet_details", kwargs={"snippet_id": self.secret_id})

    def highlight(self):
        HighlighterClass = highlight.get_highlighter_class(self.lexer)
        return HighlighterClass().render(
            code_string=self.content,
            lexer_name=self.lexer,
            direction="rtl" if self.rtl else "ltr",
        )

    @property
    def lexer_name(self):
        """Display name for this lexer."""
        return highlight.Highlighter.get_lexer_display_name(self.lexer)

    @property
    def page_title(self):
        """
        The title of this snippet, or the first line of its content if it
        has none. One-Time snippets never leak their content that way.
        """
        if self.title:
            return self.title
        if not config.TITLE_FROM_CONTENT or self.expire_type == self.EXPIRE_ONETIME:
            return ""
        for line in self.content.splitlines():
            line = line.strip()
            if line:
                return line[: config.TITLE_MAX_LENGTH]
        return ""

    @property
    def remaining_views(self):
        if self.expire_type == self.EXPIRE_ONETIME:
            remaining = config.ONETIME_LIMIT - self.view_count
            return remaining > 0 and remaining or 0


class BlockedDomain(models.Model):
    """
    A domain on the blocklist. Snippets which link to it, or to one of its
    subdomains, are rejected and deleted by the abuse filter.
    """

    domain = models.CharField(_("Domain"), max_length=255, unique=True)
    note = models.CharField(_("Note"), max_length=255, blank=True, default="")
    created = models.DateTimeField(_("Created"), auto_now_add=True)
    hits = models.PositiveIntegerField(_("Hits"), default=0)
    last_hit = models.DateTimeField(_("Last hit"), blank=True, null=True)

    class Meta:
        ordering = ("domain",)
        db_table = "dpaste_blockeddomain"

    def __str__(self):
        return self.domain

    def save(self, *args, **kwargs):
        self.domain = abuse.normalize_domain(self.domain)
        super().save(*args, **kwargs)


post_save.connect(abuse.clear_cache, sender=BlockedDomain)
post_delete.connect(abuse.clear_cache, sender=BlockedDomain)
