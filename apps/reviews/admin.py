from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('app', 'rating', 'author', 'source', 'created_at')
    list_filter = ('rating', 'source', 'created_at')
    search_fields = ('text', 'author', 'app__name')
    readonly_fields = ('created_at',)

