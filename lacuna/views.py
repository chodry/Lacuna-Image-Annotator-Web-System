from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Country, Upload, Leader, Annotator
from django.urls import reverse_lazy
from .forms import LeaderModelForm, AnnotatorModelForm, AssignAnnotatorForm
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

    def get_context_data(self, **kwargs):
        upload = self.request.user.country
        queryset = Upload.objects.filter(country=upload)
        queryset2 = Upload.objects.filter(country=Country.objects.get(country='Uganda'))
        queryset3 = Upload.objects.filter(country=Country.objects.get(country='Tanzania'))
        queryset4 = Upload.objects.filter(country=Country.objects.get(country='Namibia'))
        queryset5 = Upload.objects.filter(country=Country.objects.get(country='Ghana'))

        context = super(UploadListView, self).get_context_data(**kwargs)

        context.update({
            "cassavaUg_uploads": queryset.filter(crop="cassava").count(),
            "cassavaUg": queryset2.filter(crop="cassava").count(),
            "cassavaUg_annotated": queryset.filter(crop="cassava").filter(is_annotated=True).count(),
            "cassavaUg_A": queryset2.filter(crop="cassava").filter(is_annotated=True).count(),
            "cassavaTz_uploads": queryset.filter(crop="cassava").count(),
            "cassavaTz": queryset3.filter(crop="cassava").count(),
            "cassavaTz_annotated": queryset.filter(crop="cassava").filter(is_annotated=True).count(),
            "cassavaTz_A": queryset3.filter(crop="cassava").filter(is_annotated=True).count(),
            "maizeUg_uploads": queryset.filter(crop="maize").count(),
            "maizeUg": queryset2.filter(crop="maize").count(),
            "maizeUg_annotated": queryset.filter(crop="maize").filter(is_annotated=True).count(),
            "maizeUg_A": queryset2.filter(crop="maize").filter(is_annotated=True).count(),
            "maizeTz_uploads": queryset.filter(crop="maize").count(),
            "maizeTz": queryset3.filter(crop="maize").count(),
            "maizeTz_annotated": queryset.filter(crop="maize").filter(is_annotated=True).count(),
            "maizeTz_A": queryset3.filter(crop="maize").filter(is_annotated=True).count(),
            "maizeNa_uploads": queryset.filter(crop="maize").count(),
            "maizeNa": queryset4.filter(crop="maize").count(),
            "maizeNa_annotated": queryset.filter(crop="maize").filter(is_annotated=True).count(),
            "maizeNa_A": queryset4.filter(crop="maize").filter(is_annotated=True).count(),
            "maizeGh_uploads": queryset.filter(crop="maize").count(),
            "maizeGh": queryset5.filter(crop="maize").count(),
            "maizeGh_annotated": queryset.filter(crop="maize").filter(is_annotated=True).count(),
            "maizeGh_A": queryset5.filter(crop="maize").filter(is_annotated=True).count(),
            "beans_uploads": queryset.filter(crop="beans").count(),
            "beans": queryset2.filter(crop="beans").count(),
            "beans_annotated": queryset.filter(crop="beans").filter(is_annotated=True).count(),
            "beans_A": queryset2.filter(crop="beans").filter(is_annotated=True).count(),
            "banana_uploads": queryset.filter(crop="banana").count(),
            "bananaTz": queryset3.filter(crop="banana").count(),
            "banana_annotated": queryset.filter(crop="banana").filter(is_annotated=True).count(),
            "banana_A": queryset3.filter(crop="banana").filter(is_annotated=True).count(),
            "pearl_uploads": queryset.filter(crop="pearl_millet").count(),
            "pearl": queryset4.filter(crop="pearl_millet").count(),
            "pearl_annotated": queryset.filter(crop="pearl_millet").filter(is_annotated=True).count(),
            "pearl_A": queryset4.filter(crop="pearl_millet").filter(is_annotated=True).count(),
            "cocoa_uploads": queryset.filter(crop="cocoa").count(),
            "cocoa": queryset5.filter(crop="cocoa").count(),
            "cocoa_annotated": queryset.filter(crop="cocoa").filter(is_annotated=True).count(),
            "cocoa_A": queryset5.filter(crop="cocoa").filter(is_annotated=True).count(),
        })

        return context

    def get_queryset(self):
        upload = self.request.user.country
        return Upload.objects.filter(country=upload)


class AssignAnnotatorView(LoginRequiredMixin, FormView):
    template_name = "upload_assign.html"
    form_class = AssignAnnotatorForm
    success_url = reverse_lazy('upload_list')

    def get_form_kwargs(self, **kwargs):
        kwargs = super(AssignAnnotatorView, self).get_form_kwargs(**kwargs)
        kwargs.update({
            "request": self.request,
        })
        return kwargs

    def form_valid(self, form):
        annotator = form.cleaned_data["assigned"]
        upload = Upload.objects.get(id=self.kwargs["pk"])
        upload.assigned = annotator
        upload.leader = self.request.user.username
        upload.save()
        return super(AssignAnnotatorView, self).form_valid(form)
