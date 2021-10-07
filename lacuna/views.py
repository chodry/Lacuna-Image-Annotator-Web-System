from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Country, Upload, Leader, Annotator, CustomUser
from django.urls import reverse_lazy
from .forms import LeaderModelForm, AnnotatorModelForm, AssignAnnotatorForm, AssignAnnotatorForm2
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import random
import os
from django.conf import settings
from django.http import HttpResponse, Http404
import json
from django.core.files.storage import default_storage
from django.db.models import Q


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

        # html_content = render_to_string("email_template.html")
        send_mail(
            subject="Lacuna Annotation Project",
            message="You were added as a Team Leader for " + user.crop + "on the Lacuna Annotation Project. Your "
                                                                         "username is: " + user.username + "\n Please access our web app from this link "
                                                                                                           "http://104.155.175.230/ "
                                                                                                           "then click Forgot Password. \n Then provide your email " + user.email + " to reset your password "
                                                                                                                                                                                    "then log in.",
            from_email=settings.DEFAULT_FROM_EMAIL,
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
            message="You were added as an Annotator for " + user.crop + "on the Lacuna Annotation Project. Your "
                                                                        "username is: " + user.username + "\n Please access our web app from this link "
                                                                                                          "http://104.155.175.230/ "
                                                                                                          "then click Forgot Password. \n Then provide your email " + user.email + " to reset your password "
                                                                                                                                                                                   "then log in.",
            from_email=settings.DEFAULT_FROM_EMAIL,
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

        # annotator = Annotator.objects.get(user=self.request.user.id)
        annotator = assigned.annotate_all

        if annotator:
            query = Upload.objects.filter(country=upload).filter(annotator_2=assigned)
            query2 = query.filter(is_annotated2=True).exclude(annotated2_right='Good Annotations')
            query2_1 = query.filter(is_annotated2=True).filter(annotated2_right='Good Annotations')
        else:
            query = Upload.objects.filter(country=upload).filter(assigned=assigned)
            query2 = query.filter(is_annotated=True).exclude(annotated_right='Good Annotations')
            query2_1 = query.filter(is_annotated=True).filter(annotated_right='Good Annotations')

        context = super(AnnotatorHomeView, self).get_context_data(**kwargs)

        context.update({
            "crop": crop,
            "casAnn": query2_1.filter(crop=crop).count(),
            "casHalf": query2.filter(crop=crop).count(),
            "annotator": annotator,
            "second": query,
            "cas2": query.filter(crop=crop).count(),
            "partials": query2,
            "fulls": query2_1,

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

        # first = queryset.filter(crop=crop).filter(assigned__isnull=False).filter(is_annotated=False)\
        #     .filter(is_annotated2=True)
        # second = queryset.filter(crop=crop).filter(annotator_2__isnull=False).filter(is_annotated2=False) \
        #     .filter(is_annotated=True)

        full_annotations = queryset.filter(crop=crop).filter(annotated_right="Good Annotations") \
            .filter(annotated2_right="Good Annotations")
        # print(full_annotations)

        partial1 = queryset.filter(crop=crop).filter(is_annotated=True).exclude(annotated_right="Good Annotations")
        partial3 = queryset.filter(crop=crop).filter(is_annotated=False).filter(is_annotated2=True)
        partial2 = queryset.filter(crop=crop).filter(is_annotated2=True).exclude(annotated2_right="Good Annotations")
        partial4 = queryset.filter(crop=crop).filter(is_annotated2=False).filter(is_annotated=True)
        partials = partial1 | partial2 | partial3 | partial4
        # print(partial1)
        # print(partial2)
        # print(partial3)
        # print(partial4)
        # print(partials)

        context = super(UploadListView, self).get_context_data(**kwargs)

        context.update({
            "crop": crop,
            "fulls": full_annotations,
            "cas": queryset.filter(crop=crop).count(),
            "casAnn": queryset.filter(crop=crop).filter(is_annotated=True).count(),
            "casAnn2": queryset.filter(crop=crop).filter(is_annotated2=True).count(),
            "partials": partials,

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
        queryset = Upload.objects.filter(country=upload).filter(crop=crop)
        return queryset


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
        leader = Leader.objects.get(user=self.request.user)
        general_Annotator = Annotator.objects.filter(leader=leader).get(annotate_all=True)
        upload.assigned = annotator
        upload.leader = self.request.user.username
        upload.annotator_2 = general_Annotator
        upload.save()
        return super(AssignAnnotatorView, self).form_valid(form)


class AssignAnnotatorView2(LoginRequiredMixin, FormView):
    template_name = "upload_assign2.html"
    form_class = AssignAnnotatorForm2
    success_url = reverse_lazy('upload_list')

    def get_form_kwargs(self, **kwargs):
        kwargs = super(AssignAnnotatorView2, self).get_form_kwargs(**kwargs)
        kwargs.update({
            "request": self.request,
        })
        return kwargs

    def form_valid(self, form):
        annotator = form.cleaned_data["annotator_2"]
        upload = Upload.objects.get(id=self.kwargs["pk"])
        assigned = upload.assigned
        if assigned == annotator:
            print("Same Annotator")
        else:
            upload.annotator_2 = annotator
            cus = CustomUser.objects.get(username=annotator)
            cus = cus.id
            Annotator.objects.filter(user=cus).update(annotate_all=True)
            upload.save()
        return super(AssignAnnotatorView2, self).form_valid(form)


class AnnotatorPageView(LoginRequiredMixin, ListView):
    model = Upload
    context_object_name = 'uploads'
    template_name = 'via.html'

    def get_context_data(self, **kwargs):
        upload = self.request.user.country
        assigned = self.request.user.annotator
        queryset = Upload.objects.filter(country=upload).filter(assigned=assigned)
        queryset2 = queryset.filter(is_annotated=True)
        queryset3 = Upload.objects.filter(country=upload).filter(annotator_2=assigned)
        queryset4 = queryset3.filter(is_annotated2=True)

        # going = queryset4.first()
        # nex = json.dumps(str(going))
        # f = open('media_cdn/media/matty_8Jul2021_9h22m.json', 'r')
        # man = f.read()

        chodrine = generateList(queryset)
        mutebi = generateList(queryset2)
        musisi = generateList(queryset3)
        john = generateList(queryset4)

        if assigned.annotate_all:
            query = queryset4.filter(annotator2Update=False).filter(annotated2_right='Bad Annotations')
            query2 = queryset3.filter(is_annotated2=False)
        else:
            query = queryset2.filter(annotatorUpdate=False).filter(annotated_right='Bad Annotations')
            query2 = queryset.filter(is_annotated=False)

        context = super(AnnotatorPageView, self).get_context_data(**kwargs)

        context.update({
            "cass": chodrine,
            "maz": mutebi,
            "anno": musisi,
            "john": john,
            "querying": query,
            "query2": query2,
            # "going": going,
        })

        return context

    def post(self, request):
        if request.method == 'POST':
            if request.POST.get('action') == 'upload1':
                blob = request.FILES.get('mydata')
                fileName = request.POST.get('fileName')
                folder = request.POST.get('file')
                annotation = request.POST.get('annotated')
                path = default_storage.save('media/' + fileName + ".json", blob)
                # url = Upload.objects.get(url=folder)
                if annotation == "first":
                    Upload.objects.filter(url=folder).update(is_annotated=True, annotatorUpload=path)
                elif annotation == "second":
                    Upload.objects.filter(url=folder).update(is_annotated2=True, annotatorUpload_2=path)
                elif annotation.startswith('review'):
                    pk = annotation.replace("review", "")
                    assigned = self.request.user.annotator
                    upload = Upload.objects.filter(id=pk)

                    if assigned.annotate_all:
                        upload.update(annotatorUpload_2=path, annotator2Update=True)
                    else:
                        upload.update(annotatorUpload=path, annotatorUpdate=True)
                else:
                    pk = annotation.replace("annotated", "")
                    assigned = self.request.user.annotator
                    upload = Upload.objects.filter(id=pk)

                    if assigned.annotate_all:
                        upload.update(annotatorUpload_2=path, is_annotated2=True)
                    else:
                        upload.update(annotatorUpload=path, is_annotated=True)

                json_data = "uploaded"

            elif request.POST.get('action') == 'upload2':
                pk = request.POST.get('pk')
                assigned = self.request.user.annotator
                query = Upload.objects.get(id=pk)

                if assigned.annotate_all:
                    json_file = query.annotatorUpload_2.name
                    f = open('media_cdn/' + json_file, 'r')
                    json_data = json.load(f)
                else:
                    json_file = query.annotatorUpload.name
                    f = open('media_cdn/' + json_file, 'r')
                    json_data = json.load(f)

            else:
                pk = request.POST.get('pk')
                query = Upload.objects.get(id=pk)
                text_file = query.adminUpload.name
                f = open('media_cdn/' + text_file, 'r')
                data = f.read()
                print(data)
                json_data = data

            my_context = {
                "upload": json_data
            }

            return HttpResponse(json.dumps(my_context, indent=4, sort_keys=True, default=str),
                                content_type='application/json')


def generateList(queryset):
    firstnames = queryset.values_list('url', flat=True)

    firstnames = list(firstnames)
    chodrine = ""
    for ele in firstnames:
        chodrine += ele

    return chodrine


def upload_file(request):
    if request.method == 'POST':
        print(request.FILES)
        blob = request.FILES.get('mydata')
        fileName = request.POST.get('fileName')
        folder = request.POST.get('file')
        annotation = request.POST.get('annotated')
        # print(chod)
        # File type is : InMemoryUploadedFile, can be saved in many ways, here I use Django's inbuilt default_storage
        # print(type(blob))
        # print(folder)
        # Define how you want to save and your save path for the files
        path = default_storage.save('media/' + fileName + ".json", blob)
        # url = Upload.objects.get(url=folder)
        if annotation == "first":
            Upload.objects.filter(url=folder).update(is_annotated=True, annotatorUpload=path)
        elif annotation == "second":
            Upload.objects.filter(url=folder).update(is_annotated2=True, annotatorUpload_2=path)
        else:
            pk = annotation.replace("review", "")
            upload = Upload.objects.filter(id=pk)

        # print(path)
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


def downloadV3(request, path):
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(file_path):
        with open(file_path, 'rb')as fh:
            response = HttpResponse(fh.read(), content_type="application/annotatorUpload_2")
            response['Content-Disposition'] = 'inline;filename=' + os.path.basename(file_path)
            return response
    raise Http404


def update1(request, pk):
    upload = Upload.objects.filter(id=pk)
    upload.update(annotated_right='Good Annotations', annotatorUpdate=True)
    return redirect("/")


def update01(request, pk):
    upload = Upload.objects.filter(id=pk)
    upload.update(annotated2_right='Good Annotations', annotator2Update=True)
    return redirect("/")


def update2(request, pk):
    upload = Upload.objects.filter(id=pk)
    upload.update(annotated_right='Bad Annotations', annotatorUpdate=False)
    return redirect("/")


def update02(request, pk):
    upload = Upload.objects.filter(id=pk)
    upload.update(annotated2_right='Bad Annotations', annotator2Update=False)
    return redirect("/")
