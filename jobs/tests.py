from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from .forms import JobCreateForm
from .models import Job


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

    def test_user_cannot_see_other_users_job(self):
        other = get_user_model().objects.create_user(
            username="outro", password="strong-test-password"
        )
        job = Job.objects.create(
            owner=other, source_type=Job.SourceType.URL, source_url="https://x/y"
        )
        self.client.force_login(self.user)
        response = self.client.get(reverse("jobs:detail", kwargs={"job_id": job.id}))
        self.assertEqual(response.status_code, 404)


class LandingTests(TestCase):
    def test_landing_public(self):
        response = self.client.get(reverse("landing"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Como funciona")

    def test_landing_redirects_authenticated(self):
        user = get_user_model().objects.create_user(
            username="logado", password="strong-test-password"
        )
        self.client.force_login(user)
        response = self.client.get(reverse("landing"))
        self.assertRedirects(response, reverse("jobs:index"))


@override_settings(SIGNUP_INVITE_CODE="segredo")
class SignupTests(TestCase):
    def _data(self, **overrides):
        data = {
            "username": "novo",
            "invite_code": "segredo",
            "password1": "Senha-forte-123",
            "password2": "Senha-forte-123",
        }
        data.update(overrides)
        return data

    def test_signup_creates_user_and_logs_in(self):
        response = self.client.post(reverse("signup"), self._data())
        self.assertRedirects(response, reverse("jobs:index"))
        user_model = get_user_model()
        self.assertTrue(user_model.objects.filter(username="novo").exists())
        self.assertIn("_auth_user_id", self.client.session)

    def test_signup_rejects_wrong_invite_code(self):
        response = self.client.post(reverse("signup"), self._data(invite_code="errado"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Codigo de convite invalido")
        self.assertFalse(get_user_model().objects.filter(username="novo").exists())

    @override_settings(SIGNUP_INVITE_CODE="")
    def test_signup_disabled_without_invite_code(self):
        response = self.client.get(reverse("signup"))
        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "Cadastro indisponivel", status_code=403)


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
