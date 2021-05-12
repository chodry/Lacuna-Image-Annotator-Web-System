from django.urls import path
from .views import (
    HomePageView, CountryCreateView, LandingPageView,
    UploadCreateView, UploadListView,
    LeaderCreateView, LeaderListView,
    AnnotatorListView, AnnotatorCreateView, AnnotatorHomeView
)

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('landing_page', LandingPageView.as_view(), name='landing_page'),
    path('country/', CountryCreateView.as_view(), name='country'),
    path('upload/', UploadCreateView.as_view(), name='upload'),
    path('upload_list/', UploadListView.as_view(), name='upload_list'),
    path('leader/', LeaderListView.as_view(), name='leaders_list'),
    path('create/', LeaderCreateView.as_view(), name='leaders_create'),
    path('annotator', AnnotatorListView.as_view(), name='annotators_list'),
    path('annotator/create/', AnnotatorCreateView.as_view(), name='annotator_create'),
    path('home/', AnnotatorHomeView.as_view(), name='annotators_home'),
]