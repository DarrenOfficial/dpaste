from django.contrib import admin
from dpaste.models import Snippet

class SnippetAdmin(admin.ModelAdmin):
    list_display = ('published', 'expires', 'lexer', 'get_absolute_url')
    date_hierarchy = 'published'
    list_filter = ('published',)
    raw_id_fields = ('parent',)

admin.site.register(Snippet, SnippetAdmin)
