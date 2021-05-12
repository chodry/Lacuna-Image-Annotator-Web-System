from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, Upload


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('username', 'email', 'country', 'is_leader', 'is_annotator')


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'country', 'is_leader', 'is_annotator')


class LeaderModelForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = (
            'email',
            'username',
            'country'
        )


class AnnotatorModelForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = (
            'email',
            'username',
        )