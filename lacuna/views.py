from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Country, Upload, Leader, Annotator
from django.urls import reverse_lazy
from .forms import LeaderModelForm, AnnotatorModelForm, AssignAnnotatorForm
from django.core.mail import send_mail
import random
import os
from django.conf import settings
from django.http import HttpResponse, Http404
import json
from django.core.files.storage import default_storage


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
            from_email="mcrops101@gmail.com",
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
        user.crop = self.request.user.crop
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
            from_email="mcrops101@gmail.com",
            recipient_list=[user.email]
        )
        return super(AnnotatorCreateView, self).form_valid(form)


class AnnotatorHomeView(LoginRequiredMixin, ListView):
    model = Annotator
    template_name = 'annotators_home.html'
    context_object_name = 'uploads'

    def get_context_data(self, **kwargs):
        upload = self.request.user.country
        assigned = self.request.user.annotator
        crop = self.request.user.crop
        queryset = Upload.objects.filter(country=upload).filter(assigned=assigned)

        context = super(AnnotatorHomeView, self).get_context_data(**kwargs)

        context.update({
            "crop": crop,
            "cas": queryset.filter(crop=crop).count(),
            "casAnn": queryset.filter(crop=crop).filter(is_annotated=True).count(),

        })

        return context

    def get_queryset(self):
        upload = self.request.user.country
        assigned = self.request.user.annotator
        crop = self.request.user.crop
        queryset = Upload.objects.filter(country=upload).filter(crop=crop).filter(assigned=assigned)
        return queryset


def download(request, path):
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(file_path):
        with open(file_path, 'rb')as fh:
            response = HttpResponse(fh.read(), content_type="application/adminUpload")
            response['Content-Disposition'] = 'inline;filename=' + os.path.basename(file_path)
            return response
    raise Http404


class UploadCreateView(LoginRequiredMixin, CreateView):
    model = Upload
    template_name = 'upload.html'
    fields = ('crop', 'country', 'url', 'adminUpload',)
    success_url = reverse_lazy('upload_list')

    def form_valid(self, form):
        return super().form_valid(form)


class UploadListView(LoginRequiredMixin, ListView):
    model = Upload
    template_name = 'upload_list.html'
    context_object_name = 'uploads'

    def get_context_data(self, **kwargs):
        upload = self.request.user.country
        crop = self.request.user.crop
        # print(crop)
        queryset = Upload.objects.filter(country=upload)
        queryset2 = Upload.objects.filter(country=Country.objects.get(country='Uganda'))
        queryset3 = Upload.objects.filter(country=Country.objects.get(country='Tanzania'))
        queryset4 = Upload.objects.filter(country=Country.objects.get(country='Namibia'))
        queryset5 = Upload.objects.filter(country=Country.objects.get(country='Ghana'))

        context = super(UploadListView, self).get_context_data(**kwargs)

        context.update({
            "crop": crop,
            "cas": queryset.filter(crop=crop).count(),
            "casAnn": queryset.filter(crop=crop).filter(is_annotated=True).count(),

            "cassavaUg": queryset2.filter(crop="Cassava").count(),
            "cassavaUg_A": queryset2.filter(crop="Cassava").filter(is_annotated=True).count(),
            "cassavaTz": queryset3.filter(crop="Cassava").count(),
            "cassavaTz_A": queryset3.filter(crop="Cassava").filter(is_annotated=True).count(),
            "maizeUg": queryset2.filter(crop="Maize").count(),
            "maizeUg_A": queryset2.filter(crop="Maize").filter(is_annotated=True).count(),
            "maizeTz": queryset3.filter(crop="Maize").count(),
            "maizeTz_A": queryset3.filter(crop="Maize").filter(is_annotated=True).count(),
            "maizeNa": queryset4.filter(crop="Maize").count(),
            "maizeNa_A": queryset4.filter(crop="Maize").filter(is_annotated=True).count(),
            "maizeGh": queryset5.filter(crop="Maize").count(),
            "maizeGh_A": queryset5.filter(crop="Maize").filter(is_annotated=True).count(),
            "beans": queryset2.filter(crop="Beans").count(),
            "beans_A": queryset2.filter(crop="Beans").filter(is_annotated=True).count(),
            "bananaTz": queryset3.filter(crop="Banana").count(),
            "banana_A": queryset3.filter(crop="Banana").filter(is_annotated=True).count(),
            "pearl": queryset4.filter(crop="Pearl_millet").count(),
            "pearl_A": queryset4.filter(crop="Pearl_millet").filter(is_annotated=True).count(),
            "cocoa": queryset5.filter(crop="Cocoa").count(),
            "cocoa_A": queryset5.filter(crop="Cocoa").filter(is_annotated=True).count(),
        })

        return context

    def get_queryset(self):
        upload = self.request.user.country
        crop = self.request.user.crop
        return Upload.objects.filter(country=upload).filter(crop=crop)


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


class AnnotatorPageView(LoginRequiredMixin, ListView):
    model = Upload
    context_object_name = 'uploads'
    template_name = 'via.html'

    def get_context_data(self, **kwargs):
        upload = self.request.user.country
        assigned = self.request.user.annotator
        queryset = Upload.objects.filter(country=upload).filter(assigned=assigned)
        queryset2 = queryset.filter(is_annotated=True)

        firstnames = queryset.values_list('url', flat=True)

        firstnames = list(firstnames)
        chodrine = ""
        for ele in firstnames:
            chodrine += ele
        chodrine
        print(chodrine)

        lastnames = queryset2.values_list('url', flat=True)
        lastnames = list(lastnames)
        mutebi = ""
        for ele in lastnames:
            mutebi += ele
        mutebi
        print(mutebi)

        context = super(AnnotatorPageView, self).get_context_data(**kwargs)

        context.update({
            "cass": chodrine,
            "maz": mutebi,
        })

        return context


def upload_file(request):
    if request.method == 'POST':
        print(request.FILES)
        blob = request.FILES.get('mydata')
        fileName = request.POST.get('fileName')
        folder = request.POST.get('file')
        # print(chod)
        # File type is : InMemoryUploadedFile, can be saved in many ways, here I use Django's inbuilt default_storage
        print(type(blob))
        print(folder)
        # Define how you want to save and your save path for the files
        path = default_storage.save('media/' + fileName + ".json", blob)
        # url = Upload.objects.get(url=folder)
        Upload.objects.filter(url=folder).update(is_annotated=True)
        Upload.objects.filter(url=folder).update(annotatorUpload=path)
        print(path)
    return HttpResponse("File received")


class DownloadList(LoginRequiredMixin, ListView):
    model = Upload
    template_name = 'download.html'
    context_object_name = 'uploads'

    def get_queryset(self):
        return Upload.objects.all()


def downloadV2(request, path):
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(file_path):
        with open(file_path, 'rb')as fh:
            response = HttpResponse(fh.read(), content_type="application/annotatorUpload")
            response['Content-Disposition'] = 'inline;filename=' + os.path.basename(file_path)
            return response
    raise Http404