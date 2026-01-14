from django import forms
from django.contrib.auth.models import User
from .models import Project, Prompt, ProjectFile

class ProjectFileForm(forms.ModelForm):
    class Meta:
        model = ProjectFile
        fields = ['file', 'name']

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean_password_confirm(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords do not match")
        return password_confirm

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description']

class PromptForm(forms.ModelForm):
    class Meta:
        model = Prompt
        fields = ['content']
