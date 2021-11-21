from django.contrib import admin
from .models import Journal, Journal_Issue, RequestAuthorShip, Article_Journal, Journal_Category, Comment, FollowerJournal, Notification
from import_export.admin import ImportExportModelAdmin


@admin.register(Journal)
class PostAdmin(ImportExportModelAdmin):
    list_display = ["journal_name", "category", "journal_editor","requesting_status" ,"created"]

    class Meta:
        model = Journal

@admin.register(Journal_Issue)
class PostAdmin(ImportExportModelAdmin):
    list_display = ["journal", "year", "name", "created","slug"]

    class Meta:
        model = Journal_Issue


@admin.register(RequestAuthorShip)
class PostAdmin(ImportExportModelAdmin):
    list_display = ["user", "journal", "status","member_status"]

    class Meta:
        model = RequestAuthorShip


@admin.register(Article_Journal)
class PostAdmin(ImportExportModelAdmin):
    list_display = ["issue_name_of_article","article_title", "article_content", "author_of_article", "journal_name_of_article", "created"]

    class Meta:
        model = Article_Journal


@admin.register(Journal_Category)
class PostAdmin(ImportExportModelAdmin):
    list_display = ["title"]

    class Meta:
        model = Journal_Category


@admin.register(Comment)
class PostAdmin(ImportExportModelAdmin):
    list_display = ["article"]

    class Meta:
        model = Comment


@admin.register(FollowerJournal)
class PostAdmin(ImportExportModelAdmin):
    list_display = ["user", "journal"]

    class Meta:
        model = FollowerJournal



@admin.register(Notification)
class PostAdmin(ImportExportModelAdmin):
    list_display = ["notification_type", "from_user","to_user","article","first_comment","second_comment","journal","date","is_seen"]

    class Meta:
        model = Notification
