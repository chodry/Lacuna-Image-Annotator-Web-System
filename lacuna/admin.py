from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm


# Register your models here.
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['username', 'email', 'country', 'is_admin', 'is_leader', 'is_annotator', ]
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('country', 'is_admin', 'is_leader', 'is_annotator',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('country', 'is_admin', 'is_leader', 'is_annotator',)}),
    )


admin.site.register(CustomUser)
admin.site.register(Country)
admin.site.register(Leader)
admin.site.register(Annotator)
admin.site.register(Upload)
admin.site.register(SavedUpload)