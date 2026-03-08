from django.contrib import admin
from .models import AnalysisRun


@admin.register(AnalysisRun)
class AnalysisRunAdmin(admin.ModelAdmin):
    list_display = ('app', 'status', 'llm_label', 'llm_confidence', 'model_name', 'created_at')
    list_filter = ('status', 'llm_label', 'model_name', 'created_at')
    search_fields = ('app__name', 'app__package_name', 'llm_rationale')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('App Information', {
            'fields': ('app', 'created_by')
        }),
        ('Analysis Results', {
            'fields': ('status', 'llm_label', 'llm_confidence', 'llm_rationale')
        }),
        ('Model Information', {
            'fields': ('model_name', 'prompt_version')
        }),
        ('Raw Data', {
            'fields': ('llm_json', 'raw_response', 'error_message'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )

