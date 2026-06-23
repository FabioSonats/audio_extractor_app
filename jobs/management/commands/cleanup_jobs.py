from datetime import timedelta
from pathlib import Path
import shutil

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from jobs.models import Job


class Command(BaseCommand):
    help = "Remove arquivos e registros de jobs antigos ja finalizados."

    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(hours=settings.JOB_RETENTION_HOURS)
        old_jobs = Job.objects.filter(finished_at__lt=cutoff)
        count = 0

        for job in old_jobs:
            directory = Path(settings.MEDIA_ROOT) / "jobs" / str(job.id)
            if directory.exists():
                shutil.rmtree(directory)
            job.delete()
            count += 1

        self.stdout.write(f"{count} job(s) removido(s).")
