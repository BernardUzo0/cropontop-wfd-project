from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, Project, Task, Field


class RegisterForm(UserCreationForm):
    full_name = forms.CharField(max_length=100)
    email = forms.EmailField()
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES)

    class Meta:
        model = User
        fields = ['username', 'full_name', 'email', 'role', 'password1', 'password2']


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['project_name', 'description', 'start_date', 'end_date', 'status', 'farm', 'field']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date', 'priority', 'status', 'project', 'assigned_to']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }


class FieldForm(forms.ModelForm):
    class Meta:
        model = Field
        fields = ['field_name', 'farm', 'crop_type', 'area_size']