from django.db import models
from django.contrib.auth.models import Group
from uuid import uuid4
import os, datetime
from django.template.defaultfilters import slugify
from django_editorjs import EditorJsField
from hitcount.models import HitCount
from unidecode import unidecode
from django.contrib.contenttypes.fields import GenericRelation
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from accounts.models import CustomUser

AUTHORSHIP_STATUS = (
    ('requested', _('Request')),
    ('accepted', _('Accept')),
    ('rejected', _('Reject')),
    ('banned', _('Request Exceeded')),
    ('blocked', _('Blocked')),
    ('created', _('Created'))
)

REQUESTING_STATUS = (
    ('open', _('Open')),
    ('closed', _('Close')),
)

JOURNAL_MEMBER_STATUS = (
    ('founder', _('Founder')),
    ('admin', _('Admin')),
    ('author', _('Author')),
    ('any', _('Any')),
)


def upload_to(instance, filename):
    extension = filename.split(".")[-1]
    new_name = "%s.%s" % (str(uuid4()), extension)
    unique_id = instance.unique_id
    return os.path.join("uploads", unique_id, new_name)


class Journal_Category(models.Model):
    title = models.CharField(
        max_length=150,
        verbose_name=_("Journal Category"))

    slug = models.SlugField(
        unique=True,
        editable=False)

    def __str__(self):
        return self.title


    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Journal_Category, self).save(*args, **kwargs)


class Journal(models.Model):
    class Meta:
        verbose_name = _("Journal")
        verbose_name_plural = _("Journals")
        ordering = ["-created"]

    journal_editor = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="journal_editor",
        default=1)

    journal_image = models.ImageField(
        upload_to=upload_to,
        null=True,
        blank=True,
        default="uploads/onecki.jpg",
        verbose_name=_("Cover photo"))

    unique_id = models.CharField(
        max_length=100,
        editable=False,
        null=True)

    journal_name = models.CharField(
        max_length=250,
        verbose_name=_("Journal Name"),
        blank=False,
        null=True)

    slug = models.SlugField(
        null=True,
        unique=True,
        editable=False)

    requesting_status = models.CharField(
        max_length=50,
        choices=REQUESTING_STATUS,
        default="closed")

    created = models.DateTimeField(
        auto_now_add=True)

    updated = models.DateTimeField(
        auto_now=True)

    category = models.ForeignKey(
        Journal_Category,
        on_delete=models.CASCADE,
        related_name="category_of_journal",
        verbose_name=_("Journal Category"))

    def __str__(self):
        return self.journal_name

    def get_journal_follow_count(self):
        return self.journalfollow.count()

    def get_added_follower_user_id(self):
        return self.journalfollow.values_list(
            'journal__id',
            flat=True)

    def get_added_follower_user(self):
        return self.journalfollow.values_list(
            'user__username',
            flat=True)

    def get_added_follower_user_as_object(self):
        data_list = []
        for i in self.journalfollow.all():
            data_list.append(i.user)
        return data_list

    def get_requesting_status(self):
        return self.requesting_status

    def get_unique_slug(self):
        counter = 0
        slug = slugify(unidecode(self.journal_name))
        new_slug = slug
        while Journal.objects.filter(slug=new_slug).exists():
            counter += 1
            new_slug = "%s-%s" % (slug, counter)
        slug = new_slug
        return slug

    def save(self, *args, **kwargs):
        if self.id is None:
            new_unique_id = str(uuid4())
            self.unique_id = new_unique_id
            self.slug = self.get_unique_slug()

        else:
            journal = Journal.objects.get(slug=self.slug)
            if journal.journal_name != self.journal_name:
                self.slug = self.get_unique_slug()

        super(Journal, self).save(*args, **kwargs)


class RequestAuthorShip(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE)
    journal = models.ForeignKey(
        Journal,
        on_delete=models.CASCADE)
    status = models.CharField(
        max_length=50,
        choices=AUTHORSHIP_STATUS,
        default="requested")
    member_status = models.CharField(
        max_length=50,
        choices=JOURNAL_MEMBER_STATUS,
        default="author")

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.journal.journal_name


YEAR_CHOICES = []
for r in range(1950, (datetime.datetime.now().year + 1)):
    YEAR_CHOICES.append((r, r))


class Journal_Issue(models.Model):
    journal = models.ForeignKey(
        Journal,
        null=False,
        blank=False,
        verbose_name=_('Journal'),
        on_delete=models.CASCADE)

    name = models.CharField(
        max_length=150,
        verbose_name=_("Issue Name"))

    year = models.IntegerField(
        _('Year'),
        choices=YEAR_CHOICES,
        default=datetime.datetime.now().year)

    created = models.DateTimeField(
        auto_now_add=True)

    slug = models.SlugField(
        unique=True,
        editable=False)

    def __str__(self):
        return str(self.year) + " / " + self.name

    def get_unique_slug(self):
        sayi = 0
        slug = slugify(unidecode(self.name))
        new_slug = slug
        j_issue = Journal_Issue.objects.filter(slug=new_slug)
        while j_issue.exists():
            sayi += 1
            new_slug = "%s-%s" % (slug, sayi)

        slug = new_slug
        return slug

    def save(self, *args, **kwargs):
        if self.id is None:
            new_unique_id = str(uuid4())
            self.unique_id = new_unique_id
            self.slug = self.get_unique_slug()
        else:
            issue = Journal_Issue.objects.get(slug=self.slug)
            if issue.name != self.name:
                self.slug = self.get_unique_slug()
        print(self.slug)
        super(Journal_Issue, self).save(*args, **kwargs)


class Article_Journal(models.Model):
    class Meta:
        verbose_name = _("Article")
        verbose_name_plural = _("Articles")
        ordering = ["-created"]

    author_of_article = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="author_of_article")

    journal_name_of_article = models.ForeignKey(
        Journal,
        on_delete=models.CASCADE,
        verbose_name=_("Select the Journal"),
        related_name="journal_name_of_article")

    issue_name_of_article = models.ForeignKey(
        Journal_Issue,
        on_delete=models.CASCADE,
        verbose_name=_("Select the Issue"),
        related_name="issue_name_of_article")

    article_image = models.ImageField(
        upload_to=upload_to,
        null=True,
        blank=True,
        default="uploads/onecki.jpg",
        verbose_name=_("Image"))

    unique_id = models.CharField(
        max_length=100,
        editable=False,
        null=True)

    article_title = models.CharField(
        max_length=250,
        verbose_name=_("Title"),
        blank=False,
        null=True)

    hit_count_generic = GenericRelation(
        HitCount,
        object_id_field='object_pk',
        related_query_name='hit_count_generic_relation')

    article_content = EditorJsField(
        null=True,
        blank=False,
        verbose_name=_("Content"),
        editorjs_config={
            "tools": {
                "Image": {
                    "config": {
                        "endpoints": {
                            "byFile": "/imageUPload/",
                            "byUrl": "/imageUPload/",
                        },
                        "additionalRequestsHeaders": [
                            {"Content-Type": "multipart/form-data"}
                        ]
                    }
                },
                "Attaches": {
                    "config": {
                        "endpoint": "/fileUPload/"
                    }
                },
                "Link": {
                    "config": {
                        "endpoint": "/fetchUrl/"
                    },
                }
            }
        })

    slug = models.SlugField(
        null=True,
        unique=True,
        editable=False)

    created = models.DateTimeField(
        auto_now_add=True)

    updated = models.DateTimeField(
        auto_now=True)

    def __str__(self):
        return "%s" % (self.article_title)

    def get_comments_article(self):
        return self.comments_article.all().count()

    def get_article_comments(self):
        return self.comments_article.all()

    def get_added_favorite_article_user(self):
        fav_list = self.favorite_article_journal
        return fav_list.values_list('user__username', flat=True)

    def get_added_favorite_article_user_as_object(self):
        data_list = []
        for i in self.favorite_article_journal.all():
            data_list.append(i.user)
        return data_list

    def get_favorite_article_count(self):
        return self.favorite_article_journal.count()

    def get_unique_slug(self):
        sayi = 0
        slug = slugify(unidecode(self.article_title))
        new_slug = slug
        while Article_Journal.objects.filter(slug=new_slug).exists():
            sayi += 1
            new_slug = "%s-%s" % (slug, sayi)

        slug = new_slug
        return slug

    def save(self, *args, **kwargs):
        if self.id is None:
            new_unique_id = str(uuid4())
            self.unique_id = new_unique_id
            self.slug = self.get_unique_slug()
        else:
            article = Article_Journal.objects.get(slug=self.slug)
            if article.article_title != self.article_title:
                self.slug = self.get_unique_slug()
        super(Article_Journal, self).save(*args, **kwargs)


class Comment(models.Model):
    article = models.ForeignKey(
        Article_Journal,
        null=True,
        on_delete=models.CASCADE,
        default=1,
        related_name="comments_article",
        verbose_name=_("Article"))

    article_comment_user = models.ForeignKey(
        CustomUser,
        null=True,
        default=1,
        related_name="comments_article",
        on_delete=models.CASCADE)

    article_comment_content = models.TextField(
        null=True,
        blank=False,
        verbose_name=_("Comment"),
        max_length=1000)

    created = models.DateTimeField(
        auto_now_add=True)

    class Meta:
        verbose_name_plural = _('comments')

    def __str__(self):
        return "%s" % self.article.article_title

    def get_screen_name(self):
        c_user = self.article_comment_user
        if c_user:
            return "%s" % c_user.username
        return c_user.email


class FollowerJournal(models.Model):
    user = models.ForeignKey(
        CustomUser,
        null=True,
        default=1,
        related_name="journalfollow",
        on_delete=models.CASCADE,
        verbose_name=_("Follower"))

    journal = models.ForeignKey(
        Journal,
        null=True,
        on_delete=models.CASCADE,
        related_name="journalfollow")

    class Meta:
        verbose_name_plural = _('Journal Subscription')

    def __str__(self):
        x = self.user.username
        y = self.journal.journal_name
        return str(x) + " / " + str(y)


class FavoriteArticleJournal(models.Model):
    user = models.ForeignKey(
        CustomUser,
        null=True,
        default=1,
        related_name="favorite_article_journal",
        on_delete=models.CASCADE)

    article = models.ForeignKey(
        Article_Journal,
        null=True,
        on_delete=models.CASCADE,
        related_name="favorite_article_journal")

    class Meta:
        verbose_name_plural = _("Likes")

    def __str__(self):
        return "%s / %s" % (self.user, self.article.article_title)


class Notification(models.Model):
    # 1=like
    # 2=comment
    # 3=requestauthorship
    # 4=subscribed
    # 5=accepted
    # 6=rejected

    notification_type = models.IntegerField()
    from_user = models.ForeignKey(
        CustomUser,
        related_name="notification_from",
        on_delete=models.CASCADE,
        null=True)

    to_user = models.ForeignKey(
        CustomUser,
        related_name="notification_to",
        on_delete=models.CASCADE,
        null=True)

    article = models.ForeignKey(
        Article_Journal,
        related_name="+",
        on_delete=models.CASCADE,
        null=True,
        blank=True)

    journal = models.ForeignKey(
        Journal,
        related_name="+",
        on_delete=models.CASCADE,
        null=True,
        blank=True)

    first_comment = models.ForeignKey(
        Comment,
        related_name="+",
        on_delete=models.CASCADE,
        null=True,
        blank=True)

    second_comment = models.ForeignKey(
        Comment,
        related_name="+",
        on_delete=models.CASCADE,
        null=True,
        blank=True)

    date = models.DateTimeField(
        default=timezone.now)

    is_seen = models.BooleanField(
        default=False)
