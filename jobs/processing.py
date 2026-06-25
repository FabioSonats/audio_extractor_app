from pathlib import Path
import shutil
import subprocess
import sys
import threading

from django.conf import settings
from django.db import close_old_connections

from .models import Job


class ProcessingError(Exception):
    pass


def job_dir(job):
    path = Path(settings.MEDIA_ROOT) / "jobs" / str(job.id)
    path.mkdir(parents=True, exist_ok=True)
    return path


def ensure_command(command):
    if shutil.which(command) is None:
        raise ProcessingError(
            f"'{command}' nao foi encontrado no PATH. Instale o {command} no servidor."
        )


def ffmpeg_command():
    configured = getattr(settings, "FFMPEG_BINARY", "")
    if configured:
        path = Path(configured)
        if not path.is_absolute():
            path = settings.BASE_DIR / path
        if path.exists():
            return str(path)

    local_binary = settings.BASE_DIR / ".tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
    if local_binary.exists():
        return str(local_binary)

    ensure_command("ffmpeg")
    return "ffmpeg"


def run_command(args, cwd=None):
    completed = subprocess.run(
        args,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        output = (completed.stderr or completed.stdout).strip()
        raise ProcessingError(output[-2000:] or f"Comando falhou: {' '.join(args)}")
    return completed


def download_video(job, directory):
    job.mark_status(Job.Status.DOWNLOADING, "Baixando o audio do link informado")
    output_template = str(directory / "source.%(ext)s")
    run_command(
        [
            sys.executable,
            "-m",
            "yt_dlp",
            "--no-playlist",
            "--max-filesize",
            f"{settings.MAX_UPLOAD_MB}M",
            "-o",
            output_template,
            job.source_url,
        ]
    )
    files = sorted(directory.glob("source.*"))
    if not files:
        raise ProcessingError("Nao consegui encontrar o arquivo baixado pelo yt-dlp.")
    return files[0]


def get_upload_path(job, directory):
    if not job.source_file:
        raise ProcessingError("Arquivo enviado nao encontrado.")

    suffix = Path(job.source_file.name).suffix or ".mp4"
    target = directory / f"source{suffix}"
    source = Path(job.source_file.path)
    if source.resolve() != target.resolve():
        shutil.copyfile(source, target)
    return target


def extract_audio(job, video_path, directory):
    ffmpeg = ffmpeg_command()
    job.mark_status(Job.Status.EXTRACTING, "Convertendo video para audio")
    audio_path = directory / f"audio.{job.audio_format}"

    if job.audio_format == Job.AudioFormat.WAV:
        args = [
            ffmpeg,
            "-y",
            "-i",
            str(video_path),
            "-vn",
            "-acodec",
            "pcm_s16le",
            "-ar",
            "16000",
            "-ac",
            "1",
            str(audio_path),
        ]
    else:
        args = [
            ffmpeg,
            "-y",
            "-i",
            str(video_path),
            "-vn",
            "-codec:a",
            "libmp3lame",
            "-q:a",
            "2",
            str(audio_path),
        ]

    run_command(args)
    return audio_path


def process_job(job_id):
    job = None
    try:
        close_old_connections()
        job = Job.objects.get(pk=job_id)
        directory = job_dir(job)

        if job.source_type == Job.SourceType.URL:
            video_path = download_video(job, directory)
        else:
            video_path = get_upload_path(job, directory)

        job.video_file_path = str(video_path)
        job.save(update_fields=["video_file_path"])

        audio_path = extract_audio(job, video_path, directory)
        job.audio_file_path = str(audio_path)
        job.save(update_fields=["audio_file_path"])

        job.mark_done()
    except Exception as exc:
        if job:
            job.mark_failed(str(exc))
        else:
            raise
    finally:
        close_old_connections()


def start_job(job_id):
    thread = threading.Thread(target=process_job, args=(job_id,), daemon=True)
    thread.start()
    return thread
