from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import JobCreateForm
from .models import Job
from .processing import start_job, transcription_backend_available


@login_required
def index(request):
    if request.method == "POST":
        form = JobCreateForm(request.POST, request.FILES)
        if form.is_valid():
            job = form.save()
            if settings.JOB_AUTO_START:
                start_job(job.id)
            messages.success(request, "Processamento criado. Ja coloquei ele para rodar.")
            return redirect("jobs:detail", job_id=job.id)
    else:
        form = JobCreateForm(
            initial={
                "wants_transcript": transcription_backend_available(),
                "audio_format": Job.AudioFormat.MP3,
            }
        )

    jobs = Job.objects.all()[:8]
    return render(
        request,
        "jobs/index.html",
        {
            "form": form,
            "jobs": jobs,
            "transcription_available": transcription_backend_available(),
        },
    )


@login_required
def detail(request, job_id):
    job = get_object_or_404(Job, pk=job_id)
    return render(request, "jobs/detail.html", {"job": job})


@login_required
def status(request, job_id):
    job = get_object_or_404(Job, pk=job_id)
    return JsonResponse(
        {
            "status": job.status,
            "status_label": job.get_status_display(),
            "status_detail": job.status_detail,
            "error_message": job.error_message,
            "is_finished": job.is_finished,
            "detail_url": reverse("jobs:detail", kwargs={"job_id": job.id}),
        }
    )


@login_required
def download(request, job_id, artifact):
    job = get_object_or_404(Job, pk=job_id)
    paths = {
        "audio": job.audio_file_path,
        "transcript": job.transcript_file_path,
    }
    file_path = paths.get(artifact)
    if not file_path:
        raise Http404("Arquivo nao encontrado.")

    path = Path(file_path)
    try:
        path.resolve().relative_to(Path(settings.MEDIA_ROOT).resolve())
    except ValueError as exc:
        raise Http404("Arquivo fora da area permitida.") from exc

    if not path.exists():
        raise Http404("Arquivo nao encontrado.")

    return FileResponse(path.open("rb"), as_attachment=True, filename=path.name)
