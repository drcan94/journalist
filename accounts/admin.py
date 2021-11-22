from django.contrib import admin
from .models import *

from import_export.admin import ImportExportModelAdmin


# Register your models here.


@admin.register(UserProfile)
class PostAdmin(ImportExportModelAdmin):
    list_display = ["user", "about", "gender", "birth_year"]

    class Meta:
        model = UserProfile


@admin.register(CustomUser)
class PostAdmin(ImportExportModelAdmin):
    list_display = ["username", "first_name", "last_name", "email"]

    class Meta:
        model = CustomUser
