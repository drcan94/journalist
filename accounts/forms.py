from datetime import timedelta
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.forms import ValidationError
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from accounts.models import CustomUser, UserProfile


class UserCacheMixin:
    user_cache = None


class SignIn(UserCacheMixin, forms.Form):
    password = forms.CharField(label=_('Password'), strip=False, widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if settings.USE_REMEMBER_ME:
            self.fields['remember_me'] = forms.BooleanField(label=_('Remember me'), required=False)

    def clean_password(self):
        password = self.cleaned_data['password']

        if not self.user_cache:
            return password

        if not self.user_cache.check_password(password):
            raise ValidationError(_('Invalid Password'))

        return password


class SignInViaUsernameForm(SignIn):
    username = forms.CharField(label=_('Username'))

    @property
    def field_order(self):
        if settings.USE_REMEMBER_ME:
            return ['username', 'password', 'remember_me']
        return ['username', 'password']

    def clean_username(self):
        username = self.cleaned_data['username']

        user = CustomUser.objects.filter(username=username).first()
        if not user:
            raise ValidationError(_('You Have Entered an Invalid Username'))

        if not user.is_active:
            raise ValidationError(_('This Account Is Inactive'))

        self.user_cache = user

        return username


class SignInViaEmailForm(SignIn):
    email = forms.EmailField(label=_('E-mail'))

    @property
    def field_order(self):
        if settings.USE_REMEMBER_ME:
            return ['email', 'password', 'remember_me']
        return ['email', 'password']

    def clean_email(self):
        email = self.cleaned_data['email']

        user = CustomUser.objects.filter(email__iexact=email).first()
        if not user:
            raise ValidationError(_('You Have Entered an Invalid Username'))

        if not user.is_active:
            raise ValidationError(_('This Account Is Inactive'))

        self.user_cache = user

        return email


class SignInViaEmailOrUsernameForm(SignIn):
    email_or_username = forms.CharField(label=_('E-Mail or Username'))

    @property
    def field_order(self):
        if settings.USE_REMEMBER_ME:
            return ['email_or_username', 'password', 'remember_me']
        return ['email_or_username', 'password']

    def clean_email_or_username(self):
        email_or_username = self.cleaned_data['email_or_username']

        user = CustomUser.objects.filter(Q(username=email_or_username) | Q(email__iexact=email_or_username)).first()
        if not user:
            raise ValidationError(_('You Have Entered an Invalid E-Mail Address or Username'))

        if not user.is_active:
            raise ValidationError(_('This Account Is Inactive'))

        self.user_cache = user

        return email_or_username


def isEnglish(field):
    try:
        field.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True


class SignUpForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = settings.SIGN_UP_FIELDS

    email = forms.EmailField(label=_('E-mail'), help_text=_('Necessary! Enter an Existing E-Mail Address'))

    def clean_email(self):
        email = self.cleaned_data['email']

        user = CustomUser.objects.filter(email__iexact=email).exists()
        if user:
            raise ValidationError(_('This E-Mail Address is Registered in the System'))

        return email

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if CustomUser.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError(_('This username is registered in the System'))
        elif not isEnglish(username):
            raise forms.ValidationError(_('Invalid Username, Do not use special characters!'))
        return username


class ResendActivationCodeForm(UserCacheMixin, forms.Form):
    email_or_username = forms.CharField(label=_('E-Mail or Username'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for i in self.fields:
            self.fields[i].widget.attrs = {"class": "single-input"}
        self.helper = FormHelper()

        self.helper.add_input(Submit("submit", _("Send"), css_class="nw-btn primary-btn mt-3 dv-size"))

    def clean_email_or_username(self):
        email_or_username = self.cleaned_data['email_or_username']

        user = CustomUser.objects.filter(Q(username=email_or_username) | Q(email__iexact=email_or_username)).first()
        if not user:
            raise ValidationError(_('You Have Entered an Invalid E-Mail Address or Username'))

        if user.is_active:
            raise ValidationError(_('This Account Is Already Active'))

        activation = user.activation_set.first()
        if not activation:
            raise ValidationError(_('Failed to Verify Activation Code'))

        now_with_shift = timezone.now() - timedelta(hours=24)
        if activation.created_at > now_with_shift:
            raise ValidationError(_('Activation Code Already Sent, But You Can Try Again In 24 Hours'))

        self.user_cache = user

        return email_or_username


class ResendActivationCodeViaEmailForm(UserCacheMixin, forms.Form):
    email = forms.EmailField(label=_('E-mail'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for i in self.fields:
            self.fields[i].widget.attrs = {"class": "single-input"}
        self.helper = FormHelper()

        self.helper.add_input(Submit("submit", _("Send"), css_class="nw-btn primary-btn mt-3 dv-size"))

    def clean_email(self):
        email = self.cleaned_data['email']

        user = CustomUser.objects.filter(email__iexact=email).first()
        if not user:
            raise ValidationError(_('You Have Entered an Invalid E-Mail Address'))

        if user.is_active:
            raise ValidationError(_('This Account Is Already Active'))

        activation = user.activation_set.first()
        if not activation:
            raise ValidationError(_('Failed to Verify Activation Code'))

        now_with_shift = timezone.now() - timedelta(hours=24)
        if activation.created_at > now_with_shift:
            raise ValidationError(_('Activation Code Already Sent, But You Can Try Again In 24 Hours'))

        self.user_cache = user

        return email


class RestorePasswordForm(UserCacheMixin, forms.Form):
    email = forms.EmailField(label=_('E-mail'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for i in self.fields:
            self.fields[i].widget.attrs = {"class": "single-input"}
        self.helper = FormHelper()

        self.helper.add_input(Submit("submit", _("Send"), css_class="nw-btn primary-btn mt-3 dv-size"))

    def clean_email(self):
        email = self.cleaned_data['email']

        user = CustomUser.objects.filter(email__iexact=email).first()
        if not user:
            raise ValidationError(_('You Have Entered an Invalid E-Mail Address'))

        if not user.is_active:
            raise ValidationError(_('This Account Is Inactive'))

        self.user_cache = user

        return email


class RestorePasswordViaEmailOrUsernameForm(UserCacheMixin, forms.Form):
    email_or_username = forms.CharField(label=_('E-Mail or Username'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for i in self.fields:
            self.fields[i].widget.attrs = {"class": "single-input"}
        self.helper = FormHelper()

        self.helper.add_input(Submit("submit", _("Send"), css_class="nw-btn primary-btn mt-3 dv-size"))

    def clean_email_or_username(self):
        email_or_username = self.cleaned_data['email_or_username']

        user = CustomUser.objects.filter(Q(username=email_or_username) | Q(email__iexact=email_or_username)).first()
        if not user:
            raise ValidationError(_('You Have Entered an Invalid E-Mail Address or Username'))

        if not user.is_active:
            raise ValidationError(_('This Account Is Inactive'))

        self.user_cache = user

        return email_or_username


class ChangeProfileForm(forms.Form):
    first_name = forms.CharField(label=_('First Name'), max_length=30, required=False)
    last_name = forms.CharField(label=_('Last Name'), max_length=150, required=False)
    username = forms.CharField(label=_('Username'), max_length=150, required=False)
    gender = forms.ChoiceField(required=False, choices=UserProfile.GENDER, label=_('Gender'))
    dogum_tarihi = forms.DateField(input_formats=("%d.%m.%Y",), widget=forms.DateInput(format="%d.%m.%Y"),
                                   required=True, label=_('Date of birth'))
    profile_photo = forms.ImageField(required=False, label=_('Profile Photo'))
    about = forms.CharField(widget=forms.Textarea, required=False, label=_('About Me'))

    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "username", "gender", "dogum_tarihi", "profile_photo", "about"]

    def __init__(self, *args, **kwargs):
        super(ChangeProfileForm, self).__init__(*args, **kwargs)

        for i in self.fields:
            if i != "about":
                self.fields[i].widget.attrs = {"class": "single-input"}
        self.fields["about"].widget.attrs["rows"] = 10
        self.fields["about"].widget.attrs["cols"] = 30
        self.fields["dogum_tarihi"].widget.attrs["placeholder"] = "GG.AA.YYYY"

        self.helper = FormHelper()

        self.helper.add_input(Submit("submit", _("Update"), css_class="nw-btn primary-btn mt-3 dv-size"))

    def clean_username(self):
        username = self.cleaned_data.get('username', None)
        if not username:
            raise forms.ValidationError(_('Please Enter a Username'))

        if CustomUser.objects.filter(Q(username__iexact=username) & ~Q(username=self.initial["username"])).exists():
            raise forms.ValidationError(_('This username is registered in the System'))
        else:
            return username


class ChangeEmailForm(forms.Form):
    email = forms.EmailField(label=_('E-mail'))

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

        for i in self.fields:
            self.fields[i].widget.attrs = {"class": "single-input"}
        self.helper = FormHelper()

        self.helper.add_input(Submit("submit", _("Send"), css_class="nw-btn primary-btn mt-3 dv-size"))

    def clean_email(self):
        email = self.cleaned_data['email']

        if email == self.user.email:
            raise ValidationError(_('This E-Mail Is Already Yours'))

        user = CustomUser.objects.filter(Q(email__iexact=email) & ~Q(id=self.user.id)).exists()
        if user:
            raise ValidationError(_('You Cannot Use This E-Mail Address'))

        return email


class RemindUsernameForm(UserCacheMixin, forms.Form):
    email = forms.EmailField(label=_('E-mail'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for i in self.fields:
            self.fields[i].widget.attrs = {"class": "single-input"}
        self.helper = FormHelper()

        self.helper.add_input(Submit("submit", _("Send"), css_class="nw-btn primary-btn mt-3 dv-size"))

    def clean_email(self):
        email = self.cleaned_data['email']

        user = CustomUser.objects.filter(email__iexact=email).first()
        if not user:
            raise ValidationError(_('You Have Entered an Invalid E-Mail Address'))

        if not user.is_active:
            raise ValidationError(_('This Account Is Inactive'))

        self.user_cache = user

        return email
