from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Resume


class RegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'username',
            'email',
            'password1',
            'password2'
        ]


class ResumeUploadForm(forms.ModelForm):

    class Meta:
        model = Resume
        fields = ['resume']

    def clean_resume(self):
        file = self.cleaned_data['resume']

        if not file.name.endswith(('.pdf', '.docx')):
            raise forms.ValidationError(
                "Only PDF and DOCX files are allowed."
            )

        return file