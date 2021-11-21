from .models import *
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from django.forms import ValidationError


class CreateCommentForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(
            CreateCommentForm, self).__init__(
            *args, **kwargs)

        self.helper = FormHelper()

        self.helper.form_method = "post"

        self.helper.layout = Layout(
            Field(
                "article_comment_content", 
                rows="4"))

        css = "btn bg-efl brdr-efl mt-10 dv-size"

        self.helper.add_input(
            Submit(
                "submit",
                _('Send Comment'), 
                css_class = css))

    class Meta:
        model = Comment
        fields = ["article_comment_content"]


class CreateJournalForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CreateJournalForm, self).__init__(
            *args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "createId"
        self.helper.field_class = ""
        self.helper.layout = Layout(
            Field(
                "journal_name", 
                css_class="single-input", 
                placeholder=_("Enter Journal Name")),
            
            Field(
                "category", 
                css_class="single-input"),

            Field(
                "journal_image", 
                css_class="single-input"))

        self.helper.add_input(
            Submit(
                "submit", 
                _("Add Journal"), 
                css_class="nw-btn primary-btn mt-3"))

    class Meta:
        model = Journal
        fields = [
            "journal_name", 
            "journal_image", 
            "category"]


class ArticleSearchForm(forms.Form):
    search = forms.CharField(
        required = False, 
        max_length = 500, 
        widget = forms.TextInput(
            attrs = {
                "class": "form-control"
                }
            )
        )


class IssueSearchForm(forms.Form):
    issue = forms.CharField(
        required=False, 
        max_length=500, 
        widget=forms.TextInput(
            attrs={
                "class": "form-control"
                }
            )
        )


class CreateIssueForm(forms.ModelForm):
    class Meta:
        model = Journal_Issue
        fields = ["journal", "name", "year"]

    def __init__(self, *args, **kwargs):
        super(CreateIssueForm, self).__init__(
            *args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "createId"
        self.helper.field_class = ""
        self.helper.form_method = 'post'

        self.helper.layout = Layout(
            Field(
                "journal", 
                css_class="single-input", 
                placeholder=_("Enter Title")),

            Field(
                "name", 
                css_class="single-input"),

            Field(
                "year", 
                css_class="single-input", 
                placeholder=_(
                    "You Can Enter Your Content")),
        )

        self.helper.add_input(
            Submit(
                "submit", 
                _("Add Issue"), 
                css_class="btn btn-primary btn-lg"))

    def clean_name(self):
        name = self.cleaned_data['name']
        journal = self.cleaned_data['journal']
        issue = Journal_Issue.objects.filter(
            name__iexact=name,
            journal=journal).exists()
        if issue:
            raise ValidationError(
                _('This Issue Name is Already Registered'))

        return name


issue = "issue_name_of_article"

j_filter = Journal_Issue.objects.filter

j_name = "journal_name_of_article"

class CreateArticleForm(forms.ModelForm):
    class Meta:
        model = Article_Journal
        exclude = ["author_of_article"]
    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        

        journal = Journal_Issue.objects

        

        self.fields[issue].queryset = journal.none()

        if j_name in self.data:
            try:
                journal_id = int(
                    self.data.get(j_name))
                
                self.fields[issue].queryset = j_filter(
                    journal_id=journal_id).order_by('name')
            except (ValueError, TypeError):
                pass

        self.helper = FormHelper()
        self.helper.form_id = "articleForm"
        self.helper.attrs = {
            "data-issues-url": "/ajax/load-issues/"}
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field(
                "article_title", 
                css_class="single-input"),

            Field(
                j_name, 
                css_class="single-input"),

            Field(
                issue, 
                css_class="single-input"),

            Field(
                "article_content", 
                css_class="single-input"),

            Field(
                "article_image"),
        )

        css = "nw-btn primary-btn mt-3 btn-lg"

        self.helper.add_input(
            Submit(
                "submit",
                _("Add Article"),
                css_class=css))


class UpdateArticleForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UpdateArticleForm, self).__init__(
            *args, **kwargs)

        self.fields[issue].queryset = j_filter(
                journal = self.initial[
                    "journal_name_of_article"])

        self.helper = FormHelper()
        self.helper.form_id = "articleForm"
        self.helper.attrs = {
            "data-issues-url": "/ajax/load-issues/"}
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field(
                "article_title", 
                css_class="single-input"),

            Field(
                "journal_name_of_article", 
                css_class="single-input"),

            Field(
                issue, 
                css_class="single-input"),

            Field(
                "article_content", 
                css_class="single-input"),

            Field("article_image"),
        )

        css = "nw-btn primary-btn mt-3 btn-lg"

        self.helper.add_input(
            Submit(
                "submit", 
                _("Update"), 
                css_class = css))


    class Meta:
        model = Article_Journal
        exclude = ["author_of_article"]
 


class UpdateJournalForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UpdateJournalForm, self).__init__(
            *args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "createId"
        self.helper.field_class = ""
        self.helper.layout = Layout(
            Field(
                "journal_name", 
                css_class="single-input"),
            Field(
                "category", 
                css_class="single-input"),
            Field(
                "journal_image", 
                css_class="single-input"),

        )
        self.helper.add_input(
            Submit(
                "submit", 
                _("Update"), 
                css_class="nw-btn primary-btn mt-3"))

    class Meta:
        model = Journal
        fields = [
            "journal_name", 
            "journal_image", 
            "category"]
