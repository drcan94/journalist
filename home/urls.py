from django.urls import path
from .views import *

urlpatterns = [
    path('about/',about,name="about"),
    path('contact/',contact,name="contact"),
    path('success/',success,name="success"),
]