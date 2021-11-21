from django import views
from django.contrib.auth.decorators import login_required
from .forms import *
from .models import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect, HttpResponseForbidden
from django.template.loader import render_to_string
from django.contrib import messages
from django.views.generic import DetailView, DeleteView, CreateView
from django.views.decorators.csrf import requires_csrf_token
from django.core.files.storage import FileSystemStorage
from django.utils.decorators import method_decorator
from django.shortcuts import render, reverse, redirect
from django.urls import reverse_lazy
from django.views.generic.edit import FormMixin
from hitcount.views import HitCountDetailView
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from uuid import uuid4
import os


def articles_journal_followed(request):
    x = 1
    requestable_journals = []

    if request.user.is_authenticated:
        list_journal_id = Journal.get_added_follower_user_id(self=request.user)
        article_follow = Article_Journal.objects.all().filter(journal_name_of_article__id__in=list_journal_id)
        if article_follow.count() == 0:
            x = 0

        requestable_journals = Journal.objects.exclude(journal_editor=request.user).exclude(
            requestauthorship__user=request.user, requestauthorship__status="accepted").exclude(
            requestauthorship__user=request.user, requestauthorship__status="requested").values_list("journal_name",
                                                                                                     flat=True)
    else:
        article_follow = Article_Journal.objects.all()
    form = ArticleSearchForm(data=request.GET or None)
    page = request.GET.get("page", 1)
    if form.is_valid():
        search = form.cleaned_data.get("search", None)
        if search:
            article_follow = article_follow.filter(
                Q(article_title__icontains=search) | Q(article_content__icontains=search) | Q(
                    journal_name_of_article__journal_name__icontains=search)).distinct()

            # the problem is all content line searching.. but i prefer just searched in content.data
            # i can't do this :(

    allcounter = article_follow.count()
    paginator = Paginator(article_follow, 6)
    try:
        article_follow = paginator.page(page)
    except EmptyPage:
        msg = _("<strong>The '%(h)s'</strong> page is not available.<br>We are redirecting you to the last page.") % {
            'h': request.GET.get("page")}
        messages.success(request, msg, extra_tags="danger")
        article_follow = paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        article_follow = paginator.page(1)

    context = {"article_follow": article_follow, "requestable": requestable_journals, "allcounter": allcounter, "x": x}
    return render(request, 'journalApp/article_follow_list.html', context=context)


def JournalView(request):
    x = 1
    requestable_journals = []
    if request.user.is_authenticated:
        list = []
        for i in Journal.get_added_follower_user_id(self=request.user):
            list.append(i)
        journalList = Journal.objects.all().filter(id__in=list)

        if journalList.count() == 0:
            x = 0

        requestable_journals = Journal.objects.exclude(journal_editor=request.user).exclude(
            requestauthorship__user=request.user, requestauthorship__status="accepted").exclude(
            requestauthorship__user=request.user, requestauthorship__status="requested").values_list("journal_name",
                                                                                                     flat=True)
    else:
        journalList = Journal.objects.all()
    allCategories = Journal_Category.objects.all()
    form = ArticleSearchForm(data=request.GET or None)
    page = request.GET.get("page", 1)
    if form.is_valid():
        search = form.cleaned_data.get("search", None)
        if search:
            journalList = journalList.filter(
                Q(journal_name__icontains=search) | Q(category__title__icontains=search)).distinct()
    allcounter = journalList.count()
    paginator = Paginator(journalList, 6)
    try:
        journalList = paginator.page(page)
    except EmptyPage:
        msg = _("<strong>The '%(h)s'</strong> page is not available.<br>We are redirecting you to the last page.") % {
            'h': request.GET.get("page")}
        messages.success(request, msg, extra_tags="danger")
        journalList = paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        journalList = paginator.page(1)

    context = {"journalList": journalList, "requestable": requestable_journals, "allCategories": allCategories,
               "allcounter": allcounter, "x": x}
    return render(request, 'journalApp/dergi_list.html', context=context)


def JournalAll(request):
    journalList = Journal.objects.all()
    allCategories = Journal_Category.objects.all()
    form = ArticleSearchForm(data=request.GET or None)
    page = request.GET.get("page", 1)
    if form.is_valid():
        search = form.cleaned_data.get("search", None)
        if search:
            journalList = journalList.filter(
                Q(journal_name__icontains=search) | Q(category__title__icontains=search)).distinct()
    allcounter = journalList.count()
    paginator = Paginator(journalList, 6)
    requestable_journals = []
    if request.user.is_authenticated:
        requestable_journals = Journal.objects.exclude(journal_editor=request.user).exclude(
            requestauthorship__user=request.user, requestauthorship__status="accepted").exclude(
            requestauthorship__user=request.user, requestauthorship__status="requested").values_list("journal_name",
                                                                                                     flat=True)

    try:
        journalList = paginator.page(page)
    except EmptyPage:
        msg = _("<strong>The '%(h)s'</strong> page is not available.<br>We are redirecting you to the last page.") % {
            'h': request.GET.get("page")}
        messages.success(request, msg, extra_tags="danger")
        journalList = paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        journalList = paginator.page(1)

    context = {"journalList": journalList, "allCategories": allCategories, "allcounter": allcounter,
               "requestable": requestable_journals}
    return render(request, 'journalApp/dergi_all.html', context=context)


def JournalDetailView(request, slug):
    journal = Journal.objects.filter(slug=slug).first()
    articleList = Article_Journal.objects.filter(journal_name_of_article_id=journal.id)
    issues = Journal_Issue.objects.filter(journal_id=journal.id)

    page = request.GET.get("page", 1)
    paginator = Paginator(issues, 5)

    form = IssueSearchForm(data=request.GET or None)

    mod = 0
    number = 0
    issue_index = 0
    if form.is_valid():
        issue = form.cleaned_data.get("issue")
        if issue:

            for index, i in enumerate(issues, start=1):
                if issue == i.name:
                    issue_index = index

            number = issue_index % 5

            mod = issue_index % 5

            if issue_index == 0:
                mod = 0
            elif mod == 0:
                mod = 5

            if number != 0:
                number = (issue_index // 5) + 1
                if number <= 0:
                    number = 1
            else:
                number = (issue_index // 5)
                if number <= 0:
                    number = 1

            page = request.GET.get("page", number)

            try:
                issues = paginator.page(page)
                if issue_index == 0:
                    msg = _(
                        "<strong>The '%(h)s'</strong> issue is not available.<br>We are redirecting you to the first page.") % {
                              'h': issue}
                    messages.success(request, msg, extra_tags="danger")

            except EmptyPage:
                msg = _(
                    "<strong>The '%(h)s'</strong> issue is not available.<br>We are redirecting you to the last page.") % {
                          'h': number}
                messages.success(request, msg, extra_tags="danger")
                issues = paginator.page(paginator.num_pages)

            except PageNotAnInteger:
                msg = _(
                    "<strong>The '%(h)s'</strong> issue is not available.<br>We are redirecting you to the first page.") % {
                          'h': number}
                messages.success(request, msg, extra_tags="danger")
                issues = paginator.page(1)

    try:
        issues = paginator.page(page)
    except EmptyPage:
        msg = _("<strong>The '%(h)s'</strong> page is not available.<br>We are redirecting you to the last page.") % {
            'h': request.GET.get("page")}
        messages.success(request, msg, extra_tags="danger")
        issues = paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        msg = _("<strong>The '%(h)s'</strong> page is not available.<br>We are redirecting you to the first page.") % {
            'h': request.GET.get("page")}
        messages.success(request, msg, extra_tags="danger")
        issues = paginator.page(1)

    allcounter = articleList.count()

    x = 1
    if allcounter == 0:
        x = 0

    requestable_journals = []
    if request.user.is_authenticated:
        requestable_journals = Journal.objects.exclude(journal_editor=request.user).exclude(
            requestauthorship__user=request.user, requestauthorship__status="accepted").exclude(
            requestauthorship__user=request.user, requestauthorship__status="requested").values_list("journal_name",
                                                                                                     flat=True)

    context = {"requestable": requestable_journals, "articleList": articleList, "allcounter": allcounter,
               "journal": journal, "x": x, "issues": issues, "mod": mod}
    return render(request, 'journalApp/dergi_detail.html', context=context)


class Article_Detail(HitCountDetailView, FormMixin):
    template_name = "journalApp/article_detail.html"
    model = Article_Journal
    context_object_name = "article"
    form_class = CreateCommentForm
    count_hit = True

    def get_success_url(self):
        return reverse("article_detail", kwargs={"slug": self.object.slug})

    def get_context_data(self, **kwargs):
        context = super(Article_Detail, self).get_context_data(**kwargs)
        context["form"] = self.get_form()
        return context

    def form_valid(self, form):
        form.instance.article_comment_user = self.request.user
        form.instance.article = self.object
        form.save()
        if self.object.author_of_article != self.request.user:
            notification = Notification.objects.create(notification_type=2, from_user=self.request.user,
                                                       first_comment=form.instance,
                                                       to_user=self.object.author_of_article, article=self.object)
        messages.success(request=self.request, message=_("Your Comment Has Been Added Successfully"))
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        self.object = self.get_object()
        form = self.get_form()

        if form.is_valid():

            return self.form_valid(form)
        else:
            return self.form_invalid(form)


@login_required
def open_close_requesting(request, slug):
    data = {"status": "closed"}
    journal = Journal.objects.filter(slug=slug).first()
    if request.user == journal.journal_editor:
        if journal.requesting_status == "open":

            data.update({"status": "closed"})
            Journal.objects.filter(slug=slug).update(requesting_status="closed")


        else:
            data.update({"status": "open"})

            Journal.objects.filter(slug=slug).update(requesting_status="open")
    return JsonResponse(data=data)


@login_required(login_url=reverse_lazy("accounts:log_in"))
def request_author_ship_view(request, slug):
    mentioned_journal = Journal.objects.all().filter(slug=slug).first()

    accepted_item = RequestAuthorShip.objects.all().filter(user=request.user, status="accepted",
                                                           journal=mentioned_journal).count()
    blocked_item = RequestAuthorShip.objects.all().filter(user=request.user, status="blocked",
                                                          journal=mentioned_journal).count()

    rejected_item = RequestAuthorShip.objects.all().filter(user=request.user, status="rejected",
                                                           journal=mentioned_journal).count()

    banned_item = RequestAuthorShip.objects.all().filter(user=request.user, status="banned",
                                                         journal=mentioned_journal).count()

    if Journal.objects.filter(requesting_status="open", journal_name=mentioned_journal).exists():

        # This code line is fit too :)
        # if str(mentioned_journal) in Journal.objects.all().filter(journal_editor=request.user).values_list("journal_name",
        #                                                                                                    flat=True):
        if RequestAuthorShip.objects.filter(member_status="founder", user=request.user,
                                            journal=mentioned_journal).exists():
            msg = _("You can always write in your own journal :)")

            messages.success(request=request, message=msg, extra_tags="success")

            return HttpResponseRedirect("/")

        else:
            if rejected_item >= 3:
                RequestAuthorShip.objects.all().filter(user=request.user, status="rejected",
                                                       journal=mentioned_journal).delete()
                RequestAuthorShip.objects.create(user=request.user, status="banned",
                                                 journal=mentioned_journal)
                msg = _(
                    "Your application was rejected 3 times.<br>You no longer have the right to apply to the journal named '%(i)s'.") % {
                          'i': mentioned_journal}
                messages.success(request=request, message=msg, extra_tags="danger")
                return HttpResponseRedirect("/")
            elif banned_item >= 1 or blocked_item >= 1:
                msg = _(
                    "You have been blocked from submitting an authorship request by the owner of the journal '%(j)s'") % {
                          'j': mentioned_journal}
                messages.success(request=request, message=msg, extra_tags="danger")
                return HttpResponseRedirect("/")
            else:
                if accepted_item >= 1:
                    msg = _("You are already the author of <strong>'%(k)s'</strong> journal") % {'k': mentioned_journal}
                    messages.success(request=request, message=msg, extra_tags="success")
                    return HttpResponseRedirect("/")
                else:
                    already_requested = RequestAuthorShip.objects.all().filter(user=request.user, status="requested",
                                                                               journal=mentioned_journal).count()
                    if already_requested == 0:
                        if not request.user in Journal.objects.filter(
                                slug=slug).first().get_added_follower_user_as_object():
                            FollowerJournal.objects.create(journal=mentioned_journal, user=request.user)
                        RequestAuthorShip.objects.create(user=request.user, status="requested",
                                                         journal=mentioned_journal)
                        msg = _("Your application has been made to <strong>'%(l)s'</strong> journal") % {
                            'l': mentioned_journal}
                        messages.success(request=request, message=msg, extra_tags="success")
                        noti = Notification.objects.filter(notification_type=6, from_user=request.user,
                                                           to_user=mentioned_journal.journal_editor,
                                                           journal=mentioned_journal)
                        if noti.exists():
                            noti.delete()
                        notification = Notification.objects.create(notification_type=3, from_user=request.user,
                                                                   to_user=mentioned_journal.journal_editor,
                                                                   journal=mentioned_journal)

                        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                    else:
                        msg = _("You Have Already Applied to <strong>'%(m)s'</strong> journal") % {
                            'm': mentioned_journal}
                        messages.success(request=request, message=msg, extra_tags="success")
                        return HttpResponseRedirect("/")
    else:
        msg = _("Authorship Requests are closed for this journal")
        messages.success(request=request, message=msg, extra_tags="danger")
        return HttpResponseRedirect("/")


@method_decorator(login_required(login_url=reverse_lazy("accounts:log_in")), name="dispatch")
class JournalEditorAssessmentView(views.View):
    def get(self, request):

        try:
            assessments = RequestAuthorShip.objects.filter(journal__journal_editor=self.request.user,
                                                           status="requested")
            return render(request, "journalApp/journal_editor_assessments.html", context={"assessments": assessments})

        except RequestAuthorShip.DoesNotExist:
            pass

    def post(self, request):
        pass


@method_decorator(login_required(login_url=reverse_lazy("accounts:log_in")), name="dispatch")
class JournalEditorAssessmentAcceptView(views.View):
    def get(self, request, id):
        # journalApp = get_object_or_404(RequestAuthorShip, id=id)
        req_obj = RequestAuthorShip.objects.all().filter(id=id)
        req_obj.update(status="accepted", member_status="author")
        journal = req_obj.first().journal
        from_user = req_obj.first().user
        notification = Notification.objects.all().filter(notification_type=3, to_user=request.user, from_user=from_user,
                                                         journal=journal)
        notification.update(notification_type=5, is_seen=False)
        return HttpResponseRedirect(reverse("editor-assessments"))


@method_decorator(login_required(login_url=reverse_lazy("accounts:log_in")), name="dispatch")
class JournalEditorAssessmentRejectView(views.View):

    def get(self, request, id):
        # journalApp = get_object_or_404(RequestAuthorShip, id=id)
        req_obj = RequestAuthorShip.objects.all().filter(id=id)
        req_obj.update(status="rejected", member_status="any")
        journal = req_obj.first().journal
        from_user = req_obj.first().user
        notification = Notification.objects.all().filter(notification_type=3, to_user=request.user, from_user=from_user,
                                                         journal=journal)
        notification.update(notification_type=6, is_seen=False)
        return HttpResponseRedirect(reverse("editor-assessments"))


@method_decorator(login_required(login_url=reverse_lazy("accounts:log_in")), name="dispatch")
class JournalEditorAssessmentBlockView(views.View):

    def get(self, request, id):
        # journalApp = get_object_or_404(RequestAuthorShip, id=id)
        RequestAuthorShip.objects.filter(id=id).update(status="blocked", member_status="any")
        return HttpResponseRedirect(reverse("editor-assessments"))


@method_decorator(login_required(login_url=reverse_lazy("accounts:log_in")), name="dispatch")
class CreateJournalView(CreateView):
    form_class = CreateJournalForm
    template_name = "journalApp/create_dergi.html"

    def get_success_url(self):
        return reverse("journal_detail", kwargs={"slug": self.object.slug})

    def form_valid(self, form):
        form.instance.journal_editor = self.request.user
        journal = form.save()
        user = journal.journal_editor
        FollowerJournal.objects.create(journal=journal, user=user)
        RequestAuthorShip.objects.create(user=user, journal=journal, status="created", member_status="founder")
        msg = _("Your journal named <strong>'%(x)s'</strong> has been created") % {'x': journal.journal_name}
        messages.success(request=self.request, message=msg, extra_tags="success")
        return super(CreateJournalView, self).form_valid(form)


@method_decorator(login_required(login_url=reverse_lazy("accounts:log_in")), name="dispatch")
class CreateIssueView(views.View):
    def get(self, request):
        form = CreateIssueForm()

        qs = Journal.objects.filter(Q(journal_editor=request.user))

        if qs:
            form.fields["journal"].queryset = qs
        else:
            messages.success(request,
                             _("You Don't Have A Journal You Are The Author Of<br>You Can Create A New Journal If You Want"))
            return HttpResponseRedirect("/journal_create/")
        return render(request, 'journalApp/create_issue.html', context={"form": form})

    def post(self, request):
        form = CreateIssueForm(data=request.POST or None, files=request.FILES or None)

        if form.is_valid():
            issue = form.save()
            msg = _("Your Issue Named <strong>'%(title)s'</strong> Has Been Created") % {"title": issue.name}
            messages.success(request=self.request, message=msg, extra_tags="success")
            return HttpResponseRedirect(reverse("journal_detail", kwargs={"slug": issue.journal.slug}))
        return render(request, 'journalApp/create_issue.html', context={"form": form})


def load_issues(request):
    journal_id = request.GET.get("journal_id")

    issues = Journal_Issue.objects.filter(journal_id=journal_id).all()

    return JsonResponse(list(issues.values('id', 'name', 'year')), safe=False)


@method_decorator(login_required(login_url=reverse_lazy("accounts:log_in")), name="dispatch")
class CreateArticleView(views.View):
    def get(self, request):
        form = CreateArticleForm()

        qs = Journal.objects.filter(Q(journal_editor=request.user) | Q(requestauthorship__user=request.user,
                                                                       requestauthorship__status="accepted")).distinct()

        if qs:
            form.fields["journal_name_of_article"].queryset = qs
        else:
            messages.success(request,
                             _("You Don't Have A Journal You Are The Author Of<br>You Can Create A New Journal If You Want"))
            return HttpResponseRedirect("/journal_create/")

        return render(request, 'journalApp/create_article.html', context={"form": form})

    def post(self, request):

        form = CreateArticleForm(data=request.POST or None, files=request.FILES or None)

        if form.is_valid():
            form.instance.author_of_article = self.request.user
            article = form.save()
            msg = _("Your Article Titled <strong>'%(title)s'</strong> Has Been Created") % {
                "title": article.article_title}
            messages.success(request=self.request, message=msg, extra_tags="success")
            return redirect("article_detail", slug=article.slug)
        return HttpResponseRedirect(reverse("index"))


@requires_csrf_token
def upload_image_view(request):
    f = request.FILES["image"]
    print(request.FILES)

    fs = FileSystemStorage()
    filename, ext = os.path.splitext(str(f))
    filename = slugify(unidecode(filename))
    filename = str(filename) + str(uuid4())
    file = fs.save(filename + ext, f)
    fileurl = fs.url(file)
    return JsonResponse({
        "success": 1,
        "file": {
            "url": fileurl
        }
    })


@requires_csrf_token
def upload_file_view(request):
    f = request.FILES["file"]
    fs = FileSystemStorage()
    filename, ext = os.path.splitext(str(f))
    filename = slugify(unidecode(filename))
    filename = str(filename) + str(uuid4())
    file = fs.save(filename + ext, f)
    fileurl = fs.url(file)
    return JsonResponse({
        "success": 1,
        "file": {
            "url": fileurl,
            "size": fs.size(filename + ext),
            "name": str(f),
            "extension": ext
        }
    })


import urllib.request
from bs4 import BeautifulSoup


@requires_csrf_token
def fetch_url(request):
    url = request.GET.get("url")
    if url[:8] != "https://":
        if url[:7] == "http://":
            url = url
        else:
            url = "https://" + url

    page = urllib.request.urlopen(str(url)).read()
    soup = BeautifulSoup(page, "html.parser")
    description = soup.find('meta', attrs={'name': 'og:description'}) or soup.find('meta', attrs={
        'property': 'description'}) or soup.find('meta', attrs={'name': 'description'})

    title = ""
    description = ""
    for tags in soup.find_all("meta"):
        if tags.get("name") == "description" or tags.get("name") == "og:description" or tags.get(
                "property") == "og:description" or tags.get("property") == "description":
            description = tags.get("content")
        if tags.get("name") == "title" or tags.get("name") == "og:title" or tags.get(
                "property") == "og:title" or tags.get("property") == "title":
            title = tags.get("content")

    return JsonResponse({
        "success": 1,
        "meta": {
            "title": title,
            "url": url,
            "description": description
        }
    })


@login_required
def add_or_remove_journal_follow(request, slug):
    data = {"count": 0, "status": "deleted"}
    journal = Journal.objects.filter(slug=slug).first()
    journal_follow = FollowerJournal.objects.filter(journal=journal, user=request.user)

    if journal_follow.exists():
        journal_follow.delete()
        notification = Notification.objects.filter(notification_type=4, from_user=request.user,
                                                   to_user=journal.journal_editor, journal=journal)
        if notification.exists():
            notification.delete()
    else:
        FollowerJournal.objects.create(journal=journal, user=request.user)
        Notification.objects.create(notification_type=4, from_user=request.user,
                                    to_user=journal.journal_editor, journal=journal)
        data.update({"status": "added"})

    count = journal.get_journal_follow_count()
    data.update({"count": count})
    return JsonResponse(data=data)


@login_required
def journal_follow_user(request, slug):
    journal = Journal.objects.filter(slug=slug).first()
    user_list = journal.get_added_follower_user_as_object()
    html = render_to_string("journalApp/include/follower_dergi_user_list.html",
                            context={"user_list": user_list}, request=request)
    return JsonResponse(data={"html": html})


@login_required(login_url=reverse_lazy("accounts:log_in"))
def ArticleUpdateView(request, slug):
    article = Article_Journal.objects.filter(slug=slug).first()
    if request.user != article.author_of_article:
        return HttpResponseForbidden()
    form = UpdateArticleForm(instance=article, data=request.POST or None, files=request.FILES or None)
    qs = Journal.objects.filter(Q(journal_editor=request.user) | Q(requestauthorship__user=request.user,
                                                                   requestauthorship__status="accepted")).distinct()

    if qs:
        form.fields["journal_name_of_article"].queryset = qs
    else:
        messages.success(request,
                         _("You Don't Have A Journal You Are The Author Of<br>You Can Create A New Journal If You Want"))
        return HttpResponseRedirect("/journal_create/")
    if form.is_valid():
        article = form.save()
        msg = _("Your article titled <strong>'%(titleup)s'</strong> has been updated") % {
            'titleup': article.article_title}
        messages.success(request, msg, extra_tags="success")
        url = reverse("article_detail", kwargs={"slug": article.slug})
        return HttpResponseRedirect(url)
    return render(request, "journalApp/update_article.html", context={"form": form})


@login_required(login_url=reverse_lazy("accounts:log_in"))
def JournalUpdateView(request, slug):
    journal = Journal.objects.filter(slug=slug).first()
    if request.user != journal.journal_editor:
        return HttpResponseForbidden()
    form = UpdateJournalForm(instance=journal, data=request.POST or None, files=request.FILES or None)
    if form.is_valid():
        journal = form.save()
        msg = _("Your journalApp named <strong>'%(nameup)s'</strong> has been updated") % {
            'nameup': journal.journal_isim}
        messages.success(request, msg, extra_tags="success")
        url = reverse("journal_detail", kwargs={"slug": journal.slug})
        return HttpResponseRedirect(url)
    return render(request, "journalApp/update_dergi.html", context={"form": form})


@method_decorator(login_required(login_url=reverse_lazy("accounts:log_in")), name="dispatch")
class JournalDeleteView(DeleteView):
    model = Journal
    success_url = "/"
    template_name = "journalApp/dergidel.html"

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.journal_editor == request.user:
            self.object.delete()
            return HttpResponseRedirect(self.success_url)
        else:
            return HttpResponseRedirect("/")

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.journal_editor != request.user:
            msg = _("Dear <strong>'%(usererror)s'</strong><br>This Journal Is Not Yours, You Can't Delete It!") % {
                'usererror': request.user.username}
            messages.success(request, msg, extra_tags="success")
            return HttpResponseRedirect("/")
        return super(JournalDeleteView, self).get(request, *args, **kwargs)


@method_decorator(login_required(login_url=reverse_lazy("accounts:log_in")), name="dispatch")
class ArticleDeleteView(DeleteView):
    model = Article_Journal
    template_name = "journalApp/articledel.html"

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.author_of_article == request.user:
            self.object.delete()
            notification = Notification.objects.filter(notification_type=2, article=self.object)
            notification.delete()
            msg = _(
                "Dear <strong>'%(dear)s'</strong><br><strong>'%(article_title)s'</strong> named article is deleted!") % {
                      'dear': request.user.get_full_name(), 'article_title': self.object.article_title}
            messages.success(request, msg, extra_tags="danger")
            return HttpResponseRedirect(
                reverse("journal_detail", kwargs={"slug": self.object.journal_name_of_article.slug}))
        else:
            return HttpResponseRedirect("/")

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.author_of_article != request.user:
            msg = _("Dear <strong>'%(dear)s'</strong><br>This Article Is Not Your Own, You Can't Delete It!") % {
                'dear': request.user.username}
            messages.success(request, msg, extra_tags="success")
            return HttpResponseRedirect("/")
        return super(ArticleDeleteView, self).get(request, *args, **kwargs)


class Journal_CategoryDetail(DetailView):
    model = Journal_Category
    template_name = "journalApp/categories/detail.html"
    context_object_name = "category"


@method_decorator(login_required(login_url=reverse_lazy("accounts:log_in")), name="dispatch")
class Article_CommentDeleteView(DeleteView):
    model = Comment

    def get_success_url(self):
        return reverse("article_detail", kwargs={"slug": self.object.article.slug})

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.article_comment_user == request.user:
            self.object.delete()
            notification = Notification.objects.filter(notification_type=2, article=self.object.article,
                                                       first_comment=self.object.id)
            notification.delete()
        return HttpResponseRedirect(self.get_success_url())


@login_required
def add_or_remove_favorite_article(request, slug):
    data = {"count": 0, "status": "deleted"}
    article = Article_Journal.objects.filter(slug=slug).first()
    favorite_article = FavoriteArticleJournal.objects.filter(article=article, user=request.user)

    if favorite_article.exists():
        favorite_article.delete()
        notification = Notification.objects.filter(notification_type=1, from_user=request.user,
                                                   to_user=article.author_of_article, article=article)
        if notification.exists():
            notification.delete()
    else:
        FavoriteArticleJournal.objects.create(article=article, user=request.user)
        notification = Notification.objects.create(notification_type=1, from_user=request.user,
                                                   to_user=article.author_of_article, article=article)

        data.update({"status": "added"})

        if notification.to_user == notification.from_user:
            notification.delete()

    count = article.get_favorite_article_count()
    data.update({"count": count})
    return JsonResponse(data=data)


@login_required
def article_list_favorite_article_user(request, slug):
    article = Article_Journal.objects.filter(slug=slug).first()
    user_list = article.get_added_favorite_article_user_as_object()
    html = render_to_string("journalApp/favorite/favorite_user_list.html", context={"user_list": user_list},
                            request=request)
    return JsonResponse(data={"html": html})


@method_decorator(login_required(login_url=reverse_lazy("accounts:log_in")), name="dispatch")
class ArticleNotification(views.View):
    def get(self, request, notification_id, slug):
        notification = Notification.objects.get(id=notification_id)
        article = Article_Journal.objects.get(slug=slug)

        notification.is_seen = True
        notification.save()

        return redirect("article_detail", slug=slug)


@method_decorator(login_required(login_url=reverse_lazy("accounts:log_in")), name="dispatch")
class JournalNotification(views.View):
    def get(self, request, notification_id, slug):
        notification = Notification.objects.get(id=notification_id)
        journal = Journal.objects.get(slug=slug)

        notification.is_seen = True
        notification.save()

        return redirect("journal_detail", slug=slug)


@method_decorator(login_required(login_url=reverse_lazy("accounts:log_in")), name="dispatch")
class RequestNotification(views.View):
    def get(self, request, notification_id):
        notification = Notification.objects.get(id=notification_id)

        notification.is_seen = True
        notification.save()
        if notification.notification_type != 3:
            return redirect("journal_detail", slug=notification.journal.slug)
        else:
            return redirect("editor-assessments")


def ads(request):
    return render(request, "journalApp/ads.txt", {})
