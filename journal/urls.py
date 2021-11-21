from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


static_root = static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
media_root = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('journalApp.urls')),
    path('us/', include('home.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
    path('user/', include("accounts.urls")),
] + static_root + media_root
