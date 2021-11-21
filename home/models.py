from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.


class Contact(models.Model):
    name = models.CharField(verbose_name=_('Name'),max_length=100)
    email = models.EmailField(verbose_name=_('E-Mail'))
    content = models.TextField(verbose_name=_('Message'))