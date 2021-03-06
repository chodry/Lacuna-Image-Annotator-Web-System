from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.db import models


# Create your models here.
class CustomUser(AbstractUser):
    CROPS = (
        ('Banana', 'Banana'),
        ('Beans', 'Beans'),
        ('Cassava', 'Cassava'),
        ('Cocoa', 'Cocoa'),
        ('Maize', 'Maize'),
        ('Pearl_millet', 'Pearl Millet'),

    )
    crop = models.CharField(choices=CROPS, max_length=100, blank=True, null=True)
    is_admin = models.BooleanField(default=True)
    is_leader = models.BooleanField(default=False)
    is_annotator = models.BooleanField(default=False)
    country = models.ForeignKey("Country", null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.username


class Country(models.Model):
    country = models.CharField(max_length=100)

    def __str__(self):
        return self.country


class Leader(models.Model):

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    country = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username


class Annotator(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    leader = models.ForeignKey(Leader, on_delete=models.CASCADE)
    annotate_all = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class Upload(models.Model):
    CROPS = (
        ('Banana', 'Banana'),
        ('Beans', 'Beans'),
        ('Cassava', 'Cassava'),
        ('Cocoa', 'Cocoa'),
        ('Maize', 'Maize'),
        ('Pearl_millet', 'Pearl Millet'),
    )
    Annotated = (
        ('Good Annotations', 'Good Annotations'),
        ('Bad Annotations', 'Bad Annotations'),
    )
    crop = models.CharField(choices=CROPS, max_length=100)
    country = models.ForeignKey(Country, models.CASCADE)
    leader = models.CharField(max_length=1000, null=True, blank=True,)
    url = models.CharField(max_length=1000)
    assigned = models.ForeignKey(Annotator, null=True, blank=True, on_delete=models.SET_NULL)
    annotator_2 = models.ForeignKey(Annotator, null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    is_annotated = models.BooleanField(default=False)
    annotated_right = models.CharField(max_length=255, blank=True)
    is_annotated2 = models.BooleanField(default=False)
    annotatorUpdate = models.BooleanField(default=False)
    annotated2_right = models.CharField(max_length=255, blank=True)
    adminUpload = models.FileField(upload_to='media', blank=True)
    annotatorUpload_2 = models.FileField(upload_to='media', blank=True)
    annotator2Update = models.BooleanField(default=False)
    annotatorUpload = models.FileField(upload_to='media', blank=True)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    annotator1_comment = models.TextField(null=True, blank=True)
    annotator2_comment = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.url


class SavedUpload(models.Model):
    upload = models.ForeignKey(Upload, on_delete=models.CASCADE)
    annotator = models.ForeignKey(Annotator, null=True, blank=True, on_delete=models.SET_NULL)
    annotation = models.CharField(max_length=255, blank=True, null=True)
    saved = models.FileField(upload_to='media')

    def __str__(self):
        return self.upload.url
