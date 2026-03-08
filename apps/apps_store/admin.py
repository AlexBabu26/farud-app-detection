from django.contrib import admin
from .models import MobileApp, Watchlist, CommunityReport


@admin.register(MobileApp)
class MobileAppAdmin(admin.ModelAdmin):
    list_display = ('name', 'package_name', 'developer', 'category', 'created_by', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'package_name', 'developer')
    readonly_fields = ('created_at',)


@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'app', 'added_at')
    list_filter = ('added_at',)


@admin.register(CommunityReport)
class CommunityReportAdmin(admin.ModelAdmin):
    list_display = ('user', 'app', 'reason', 'created_at')
    list_filter = ('reason', 'created_at')
    search_fields = ('description',)

