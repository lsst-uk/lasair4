from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile
from crispy_forms.helper import FormHelper
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3
from django.conf import settings


class UserRegisterForm(UserCreationForm):
    captcha = ReCaptchaField(widget=ReCaptchaV3())
    email = forms.EmailField()
    if getattr(settings, "DEBUG", False) and getattr(settings, "LASAIR_URL", False) == "127.0.0.1":
        captcha.clean = lambda x: True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'captcha']


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']


class ProfileUpdateForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ['image']
