from django.contrib import admin

from .models import Job


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("id", "source_type", "status", "created_at", "finished_at")
    list_filter = ("source_type", "status", "created_at")
    search_fields = ("id", "source_url", "original_filename")
    readonly_fields = ("id", "created_at", "started_at", "finished_at")
