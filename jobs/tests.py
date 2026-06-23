from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .forms import JobCreateForm


class JobViewsTests(TestCase):
    def test_index_loads(self):
        response = self.client.get(reverse("jobs:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Transforme video em audio e texto")

    def test_healthcheck(self):
        response = self.client.get(reverse("healthcheck"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

class JobCreateFormTests(TestCase):
    def test_requires_one_source(self):
        form = JobCreateForm(data={"audio_format": "mp3", "wants_transcript": "on"})
        self.assertFalse(form.is_valid())
        self.assertIn("Informe um link ou envie um arquivo", str(form.errors))

    def test_rejects_two_sources(self):
        upload = SimpleUploadedFile("video.mp4", b"fake")
        form = JobCreateForm(
            data={
                "source_url": "https://example.com/video",
                "audio_format": "mp3",
                "wants_transcript": "on",
            },
            files={"source_file": upload},
        )
        self.assertFalse(form.is_valid())
        self.assertIn("Informe um link ou envie um arquivo", str(form.errors))
