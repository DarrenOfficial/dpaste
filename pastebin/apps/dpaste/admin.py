from django.contrib import admin
from pastebin.apps.dpaste.models import Snippet, Spamword

class SnippetAdmin(admin.ModelAdmin):
    list_display = ('published', 'expires', 'author', 'title')
    date_hierarchy = 'published'
    list_filter = ('published',)

admin.site.register(Snippet, SnippetAdmin)
admin.site.register(Spamword)
