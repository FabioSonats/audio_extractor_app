import uuid

from django.db import models
from django.utils import timezone


class Job(models.Model):
    class SourceType(models.TextChoices):
        URL = "url", "Link"
        UPLOAD = "upload", "Arquivo"

    class Status(models.TextChoices):
        QUEUED = "queued", "Na fila"
        DOWNLOADING = "downloading", "Baixando video"
        EXTRACTING = "extracting", "Extraindo audio"
        DONE = "done", "Concluido"
        FAILED = "failed", "Falhou"

    class AudioFormat(models.TextChoices):
        MP3 = "mp3", "MP3"
        WAV = "wav", "WAV"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source_type = models.CharField(max_length=20, choices=SourceType.choices)
    source_url = models.URLField(blank=True)
    source_file = models.FileField(upload_to="uploads/%Y/%m/%d/", blank=True, null=True)
    original_filename = models.CharField(max_length=255, blank=True)
    audio_format = models.CharField(max_length=10, choices=AudioFormat.choices, default=AudioFormat.MP3)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.QUEUED)
    status_detail = models.CharField(max_length=255, blank=True)
    error_message = models.TextField(blank=True)
    video_file_path = models.CharField(max_length=500, blank=True)
    audio_file_path = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(blank=True, null=True)
    finished_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        label = self.source_url or self.original_filename or str(self.id)
        return f"{label} ({self.get_status_display()})"

    @property
    def is_finished(self):
        return self.status in {self.Status.DONE, self.Status.FAILED}

    def mark_status(self, status, detail=""):
        if not self.started_at:
            self.started_at = timezone.now()
        self.status = status
        self.status_detail = detail
        self.save(update_fields=["status", "status_detail", "started_at"])

    def mark_failed(self, message):
        self.status = self.Status.FAILED
        self.error_message = message[:4000]
        self.finished_at = timezone.now()
        self.save(update_fields=["status", "error_message", "finished_at"])

    def mark_done(self):
        self.status = self.Status.DONE
        self.finished_at = timezone.now()
        self.save(update_fields=["status", "finished_at"])
