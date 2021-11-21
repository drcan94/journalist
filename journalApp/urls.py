from django.urls import path
from .views import *
from django.views.decorators.csrf import csrf_exempt


journal_request = [
    path('onoff/<slug:slug>/', open_close_requesting, name="open_close"),
    path("request/<slug:slug>/", request_author_ship_view,name="authorship-request"),
    path("assessments/", JournalEditorAssessmentView.as_view(), name="editor-assessments"),
    path("reject/<int:id>/", JournalEditorAssessmentRejectView.as_view(), name="request-reject"),
    path("accept/<int:id>/", JournalEditorAssessmentAcceptView.as_view(), name="request-accept"),
    path("blocked/<int:id>/", JournalEditorAssessmentBlockView.as_view(), name="request-blocked"),
]


urlpatterns = [
    path('journals/', JournalView, name="journalindex"),
    path('journals_all/', JournalAll, name="journalall"),
    path('issue_create/', CreateIssueView.as_view(), name="issue_create"),
    path('journal_create/', CreateJournalView.as_view(), name="journal_create"),

    path('notification/<int:notification_id>/article/<slug:slug>/',ArticleNotification.as_view(), name="article_notification"),
    path('notification/<int:notification_id>/journal/<slug:slug>/',JournalNotification.as_view(), name="journal_notification"),
    path('notification/<int:notification_id>/request/',RequestNotification.as_view(), name="request_notification"),

    path('ajax/load-issues/', load_issues, name="load_issues"),

    path("fileUPload/",csrf_exempt(upload_file_view)),
    path("imageUPload/",csrf_exempt(upload_image_view)),
    path("fetchUrl/",csrf_exempt(fetch_url)),

    path('article_create/', CreateArticleView.as_view(), name="article_create"),
    path('journal_detail/<slug:slug>/', JournalDetailView, name="journal_detail"),
    path('', articles_journal_followed, name="index"),
    path('articledetail/<slug:slug>/', Article_Detail.as_view(), name="article_detail"),
    path('journaldetail/<slug:slug>/delete/', JournalDeleteView.as_view(), name="journal_delete"),
    path('articledetail/<slug:slug>/delete/', ArticleDeleteView.as_view(), name="article_delete"),
    path('journaldetail/<slug:slug>/update/', JournalUpdateView, name="journal_update"),
    path('articledetail/<slug:slug>/update/', ArticleUpdateView, name="article_update"),

    #ads.txt
    path('ads.txt/', ads, name="ads"),

    # category detail
    path('category/<slug:slug>/', Journal_CategoryDetail.as_view(), name="journal_category_detail"),

    # commentdelete
    path('comment/<int:pk>/delete/', Article_CommentDeleteView.as_view(), name="article_comment-delete"),

    # dergi_takip
    path('journal_follow/<slug:slug>/', add_or_remove_journal_follow, name="journal_follow"),
    path('journal_follow_users/<slug:slug>/', journal_follow_user, name="journal_follow_user"),

    # article_like
    path('favorite-page/<slug:slug>/', add_or_remove_favorite_article, name="favorite-article-page"),
    path('favorite-page-users/<slug:slug>/', article_list_favorite_article_user, name="favorite-article-user"),

]

urlpatterns += journal_request
