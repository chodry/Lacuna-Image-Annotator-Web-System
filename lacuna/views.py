from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Country, Upload, Leader, Annotator
from django.urls import reverse_lazy
from .forms import LeaderModelForm, AnnotatorModelForm
from django.core.mail import send_mail
import random


# Create your views here.
class LandingPageView(TemplateView):
    template_name = 'landing.html'


class HomePageView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'


class CountryCreateView(LoginRequiredMixin, CreateView):
    model = Country
    template_name = 'country_create.html'
    fields = ('country',)
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        return super().form_valid(form)


class LeaderListView(LoginRequiredMixin, ListView):
    model = Leader
    template_name = 'leaders_list.html'
    context_object_name = 'leaders'


class LeaderCreateView(LoginRequiredMixin, CreateView):
    template_name = 'leader_create.html'
    form_class = LeaderModelForm
    success_url = reverse_lazy('leaders_list')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_admin = False
        user.is_leader = True
        user.is_annotator = False
        user.set_password(f"{random.randint(0, 1000000)}")
        user.save()
        Leader.objects.create(
            user=user,
            country=form.cleaned_data.get('country')
        )
        send_mail(
            subject="Lacuna Annotation Project",
            message="You were added as an Team Leader on the Lacuna Annotation Project. Please log in, Your username "
                    "is: " + user.username,
            from_email="admin@test.com",
            recipient_list=[user.email]
        )
        return super(LeaderCreateView, self).form_valid(form)


class AnnotatorListView(LoginRequiredMixin, ListView):
    model = Annotator
    template_name = 'annotators_list.html'
    context_object_name = 'annotators'

    def get_queryset(self):
        leader = self.request.user.leader
        return Annotator.objects.filter(leader=leader)


class AnnotatorCreateView(LoginRequiredMixin, CreateView):
    template_name = 'annotator_create.html'
    form_class = AnnotatorModelForm
    success_url = reverse_lazy('annotators_list')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_admin = False
        user.is_leader = False
        user.is_annotator = True
        user.country = self.request.user.country
        user.set_password(f"{random.randint(0, 1000000)}")
        user.save()
        Annotator.objects.create(
            user=user,
            leader=self.request.user.leader,
        )
        send_mail(
            subject="Lacuna Annotation Project",
            message="You were added as an Annotator on the Lacuna Annotation Project. Please log in, Your username "
                    "is: " + user.username,
            from_email="admin@test.com",
            recipient_list=[user.email]
        )
        return super(AnnotatorCreateView, self).form_valid(form)


class AnnotatorHomeView(LoginRequiredMixin, TemplateView):
    model = Annotator
    template_name = 'annotators_home.html'


class UploadCreateView(LoginRequiredMixin, CreateView):
    model = Upload
    template_name = 'upload.html'
    fields = ('crop', 'country', 'url',)
    success_url = reverse_lazy('upload_list')

    def form_valid(self, form):
        return super().form_valid(form)


class UploadListView(LoginRequiredMixin, ListView):
    model = Upload
    template_name = 'upload_list.html'
    context_object_name = 'uploads'

    def get_queryset(self):
        upload = self.request.user.country
        if upload == None:
            return Upload.objects.all()
        else:
            return Upload.objects.filter(country=upload)


class UploadAssignView(LoginRequiredMixin, UpdateView):
    template_name = "upload_assign.html"
    fields = ('assigned',)
    success_url = reverse_lazy('upload_list')

    def get_queryset(self):
        leader = self.request.user.leader
        print(leader)
        annotator = Annotator.objects.filter(leader=leader)
        print(annotator)
        queryset = Upload.objects.all()
        # queryset = Annotator.objects.filter(leader=leader)
        return queryset
