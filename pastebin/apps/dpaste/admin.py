from django.contrib import admin
from pastebin.apps.dpaste.models import Snippet

class SnippetAdmin(admin.ModelAdmin):
    list_display = ('published', 'expires', 'lexer', 'get_absolute_url')
    date_hierarchy = 'published'
    list_filter = ('published',)

admin.site.register(Snippet, SnippetAdmin)
