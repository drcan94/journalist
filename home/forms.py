from .models import Contact
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit,Layout,Field,HTML
from django import forms
from django.utils.translation import gettext_lazy as _



class ContactForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        super(ContactForm, self).__init__(*args,**kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "createId"
        self.helper.field_class = ""
        self.helper.layout = Layout(
            Field("name",css_class="single-input",placeholder=_('Enter Your Full Name')),
            Field("email",css_class="single-input",placeholder=_('E-Mail')),
            Field("content", css_class="single-input",placeholder=_('Your Message')),
        )
        self.helper.add_input(Submit("submit",_('Send'),css_class="nw-btn primary-btn mt-3"))
    class Meta:
        model = Contact
        fields = ["name","email","content"]
