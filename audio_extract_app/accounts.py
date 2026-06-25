from django import forms
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render


class SignupForm(UserCreationForm):
    invite_code = forms.CharField(
        label="Codigo de convite",
        strip=False,
        help_text="Codigo fornecido pela equipe para liberar o cadastro.",
    )

    field_order = ["username", "invite_code", "password1", "password2"]

    def clean_invite_code(self):
        code = self.cleaned_data.get("invite_code", "")
        expected = getattr(settings, "SIGNUP_INVITE_CODE", "")
        if not expected or code != expected:
            raise forms.ValidationError("Codigo de convite invalido.")
        return code


def signup(request):
    if request.user.is_authenticated:
        return redirect("jobs:index")

    if not getattr(settings, "SIGNUP_INVITE_CODE", ""):
        return render(request, "registration/signup_disabled.html", status=403)

    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("jobs:index")
    else:
        form = SignupForm()

    return render(request, "registration/signup.html", {"form": form})
