from django.db import models
from django.contrib.auth.models import AbstractUser
from django.shortcuts import reverse
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _


class CustomUser(AbstractUser):
    pass


class Activation(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    code = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True)


class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, null=True, blank=False, verbose_name=_('User'), on_delete=models.CASCADE)
    about = models.TextField(max_length=2000, blank=True, null=True, verbose_name=_('About Me'))
    GENDER = ((None, _('Gender')), ('man', _('Man')), ('woman', _('Woman')))
    gender = models.CharField(choices=GENDER, blank=True, null=True, max_length=10, verbose_name=_('Gender'))
    profile_photo = models.ImageField(null=True, blank=True, verbose_name=_('Profile Photo'))
    birth_year = models.DateField(null=True, blank=True, verbose_name=_('Date of birth'))

    class Meta:
        verbose_name_plural = _('User Profiles')

    def get_screen_name(self):
        user = self.user
        if user.get_full_name():
            return user.get_full_name()
        return user.username

    def get_user_profile_url(self):
        url = reverse('accounts:user-profile', kwargs={'username': self.user.username})
        return url

    def user_full_name(self):
        if self.user.get_full_name():
            return self.user.get_full_name()
        return None

    def get_profile_photo(self):
        if self.profile_photo:
            return self.profile_photo.url
        return "/content/media/uploads/avatars/default.svg"

    def get_notification_count(self):
        from journalApp.models import Notification
        count = 0
        types = [1, 2, 3, 4, 5, 6]
        for i in Notification.objects.all():
            if i.notification_type in types:
                if (i.notification_type == 5 or i.notification_type == 6) and i.from_user == self.user and i.is_seen is False:
                    count += 1
                if (i.notification_type != 5 and i.notification_type != 6) and (i.to_user == self.user) and (i.is_seen is False):
                    count += 1
        if count > 0:
            return count

        return False

    def __str__(self):
        return "%s" % (self.get_screen_name())


def create_profile(sender, created, instance, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


post_save.connect(create_profile, sender=CustomUser)
