from time import sleep

from django.core.management.base import BaseCommand

from jobs.models import Job
from jobs.processing import process_job


class Command(BaseCommand):
    help = "Processa jobs pendentes. Use --watch para manter o worker rodando."

    def add_arguments(self, parser):
        parser.add_argument("--watch", action="store_true", help="Continua procurando jobs novos.")
        parser.add_argument("--sleep", type=int, default=5, help="Segundos entre buscas no modo watch.")

    def handle(self, *args, **options):
        while True:
            job = Job.objects.filter(status=Job.Status.QUEUED).order_by("created_at").first()
            if job:
                self.stdout.write(f"Processando {job.id}")
                process_job(job.id)
                continue

            if not options["watch"]:
                self.stdout.write("Nenhum job pendente.")
                return

            sleep(options["sleep"])
