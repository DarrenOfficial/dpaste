from pastebin.apps.dpaste.models import Snippet, Spamword
from django.contrib import admin

class SnippetAdmin(admin.ModelAdmin):
    list_display = (
        '__unicode__',
        'author',
        'lexer',
        'published',
        'expires',
    )

admin.site.register(Snippet, SnippetAdmin)
admin.site.register(Spamword)