# Generated manually for the initial project scaffold.

import uuid
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Job",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                (
                    "source_type",
                    models.CharField(
                        choices=[("url", "Link"), ("upload", "Arquivo")],
                        max_length=20,
                    ),
                ),
                ("source_url", models.URLField(blank=True)),
                ("source_file", models.FileField(blank=True, null=True, upload_to="uploads/%Y/%m/%d/")),
                ("original_filename", models.CharField(blank=True, max_length=255)),
                (
                    "audio_format",
                    models.CharField(
                        choices=[("mp3", "MP3"), ("wav", "WAV")],
                        default="mp3",
                        max_length=10,
                    ),
                ),
                ("wants_transcript", models.BooleanField(default=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("queued", "Na fila"),
                            ("downloading", "Baixando video"),
                            ("extracting", "Extraindo audio"),
                            ("transcribing", "Transcrevendo"),
                            ("done", "Concluido"),
                            ("failed", "Falhou"),
                        ],
                        default="queued",
                        max_length=30,
                    ),
                ),
                ("status_detail", models.CharField(blank=True, max_length=255)),
                ("error_message", models.TextField(blank=True)),
                ("video_file_path", models.CharField(blank=True, max_length=500)),
                ("audio_file_path", models.CharField(blank=True, max_length=500)),
                ("transcript_file_path", models.CharField(blank=True, max_length=500)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("started_at", models.DateTimeField(blank=True, null=True)),
                ("finished_at", models.DateTimeField(blank=True, null=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="Transcript",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("text", models.TextField()),
                ("language", models.CharField(blank=True, max_length=50)),
                ("duration_seconds", models.PositiveIntegerField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "job",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="transcript",
                        to="jobs.job",
                    ),
                ),
            ],
        ),
    ]
