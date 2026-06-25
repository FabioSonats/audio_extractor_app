from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .forms import JobCreateForm


class JobViewsTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="tester",
            password="strong-test-password",
        )

    def test_index_requires_login(self):
        response = self.client.get(reverse("jobs:index"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response["Location"])

    def test_index_loads(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("jobs:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Transforme video em audio")

    def test_healthcheck(self):
        response = self.client.get(reverse("healthcheck"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

class JobCreateFormTests(TestCase):
    def test_requires_one_source(self):
        form = JobCreateForm(data={"audio_format": "mp3"})
        self.assertFalse(form.is_valid())
        self.assertIn("Informe um link ou envie um arquivo", str(form.errors))

    def test_rejects_two_sources(self):
        upload = SimpleUploadedFile("video.mp4", b"fake")
        form = JobCreateForm(
            data={
                "source_url": "https://example.com/video",
                "audio_format": "mp3",
            },
            files={"source_file": upload},
        )
        self.assertFalse(form.is_valid())
        self.assertIn("Informe um link ou envie um arquivo", str(form.errors))
