from django.contrib import admin

from .models import Job, Transcript


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("id", "source_type", "status", "wants_transcript", "created_at", "finished_at")
    list_filter = ("source_type", "status", "wants_transcript", "created_at")
    search_fields = ("id", "source_url", "original_filename")
    readonly_fields = ("id", "created_at", "started_at", "finished_at")


@admin.register(Transcript)
class TranscriptAdmin(admin.ModelAdmin):
    list_display = ("job", "language", "duration_seconds", "created_at")
    search_fields = ("job__id", "text")
