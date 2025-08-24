from django.contrib import admin
from .models import Quote


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ('text_short', 'source', 'weight', 'likes', 'dislikes', 'views', 'created_at')
    list_filter = ('source',)
    search_fields = ('text', 'source')
    ordering = ('-likes', '-views')

    def text_short(self, obj):
        return (obj.text[:60] + '...') if len(obj.text) > 60 else obj.text
    text_short.short_description = 'Цитата'
