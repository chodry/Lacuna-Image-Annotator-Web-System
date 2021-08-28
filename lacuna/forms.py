from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, Upload, Annotator


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
            'country',
            'crop',
        )


class AnnotatorModelForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = (
            'email',
            'username',
        )


class AssignAnnotatorForm(forms.Form):
    assigned = forms.ModelChoiceField(queryset=Annotator.objects.none())

    def __init__(self, *args, **kwargs):
        request = kwargs.pop("request")
        annotators = Annotator.objects.filter(leader=request.user.leader).filter(annotate_all=False)
        super(AssignAnnotatorForm, self).__init__(*args, **kwargs)
        self.fields["assigned"].queryset = annotators


class AssignAnnotatorForm2(forms.Form):
    annotator_2 = forms.ModelChoiceField(queryset=Annotator.objects.none())

    def __init__(self, *args, **kwargs):
        request = kwargs.pop("request")
        annotators = Annotator.objects.filter(leader=request.user.leader)
        super(AssignAnnotatorForm2, self).__init__(*args, **kwargs)
        self.fields["annotator_2"].queryset = annotators
