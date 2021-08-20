from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url
from django.views.static import serve
from .views import (
    HomePageView, CountryCreateView, LandingPageView,
    UploadCreateView, UploadListView, AssignAnnotatorView, AssignAnnotatorView2,
    LeaderCreateView, LeaderListView,
    AnnotatorListView, AnnotatorCreateView, AnnotatorHomeView,
    AnnotatorPageView, upload_file, DownloadList,
)

urlpatterns = [
    path('home', HomePageView.as_view(), name='home'),
    path('landing_page', LandingPageView.as_view(), name='landing_page'),
    path('country/', CountryCreateView.as_view(), name='country'),
    path('upload/', UploadCreateView.as_view(), name='upload'),
    path('', UploadListView.as_view(), name='upload_list'),
    path('<int:pk>/upload_assign/', AssignAnnotatorView.as_view(), name='upload_assign'),
    path('<int:pk>/upload_assign2/', AssignAnnotatorView2.as_view(), name='upload_assign2'),
    path('leader/', LeaderListView.as_view(), name='leaders_list'),
    path('create/', LeaderCreateView.as_view(), name='leaders_create'),
    path('annotator', AnnotatorListView.as_view(), name='annotators_list'),
    path('annotator/create/', AnnotatorCreateView.as_view(), name='annotator_create'),
    path('annotation/', AnnotatorPageView.as_view(), name='annotator'),
    url(r'^download/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    path('annotation_home/', AnnotatorHomeView.as_view(), name='annotators_home'),
    path('fileUpload/', upload_file, name='upload_file'),
    path('downl/', DownloadList.as_view(), name='downloads'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
