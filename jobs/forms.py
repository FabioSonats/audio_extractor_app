from django import forms
from django.conf import settings

from .models import Job


class JobCreateForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ["source_url", "source_file", "audio_format", "wants_transcript"]
        widgets = {
            "source_url": forms.URLInput(
                attrs={
                    "placeholder": "Cole aqui o link do YouTube ou outro video",
                    "class": "input",
                }
            ),
            "source_file": forms.ClearableFileInput(attrs={"class": "file-input"}),
            "audio_format": forms.RadioSelect(),
            "wants_transcript": forms.CheckboxInput(attrs={"class": "checkbox"}),
        }
        labels = {
            "source_url": "Link do video",
            "source_file": "Arquivo de video",
            "audio_format": "Formato do audio",
            "wants_transcript": "Gerar texto transcrito",
        }

    def clean(self):
        cleaned = super().clean()
        source_url = cleaned.get("source_url")
        source_file = cleaned.get("source_file")

        if bool(source_url) == bool(source_file):
            raise forms.ValidationError("Informe um link ou envie um arquivo, mas nao os dois.")

        if source_file:
            max_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024
            if source_file.size > max_bytes:
                raise forms.ValidationError(
                    f"O arquivo passa do limite de {settings.MAX_UPLOAD_MB} MB."
                )

        return cleaned

    def save(self, commit=True):
        job = super().save(commit=False)
        if self.cleaned_data.get("source_url"):
            job.source_type = Job.SourceType.URL
        else:
            job.source_type = Job.SourceType.UPLOAD
            job.original_filename = self.cleaned_data["source_file"].name

        if commit:
            job.save()
        return job
