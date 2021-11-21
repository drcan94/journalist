from django.core.mail import EmailMessage
from django.views.generic import TemplateView
from django.shortcuts import render
from .forms import *
from django.shortcuts import redirect


class ChangeLanguageView(TemplateView):
    template_name = 'change_language.html'


def contact(request):
    template_name = 'home/contact.html'
    if request.method == "POST":
        form = ContactForm(request.POST or None)
        if form.is_valid():
            email = EmailMessage(
                "İletişim Formu Postaları",
                "İsim : " + form.cleaned_data.get("name")+"\n\nMesaj : " + form.cleaned_data.get("content"),
                "site_name",
                ["owner_email"],
                reply_to=[form.cleaned_data.get("email")],
                headers={"Messaage-ID": "foo"}
            )
            email.send(fail_silently=False)
        return redirect("success")
    else:
        form = ContactForm()
        return render(request, template_name, {'form': form})


def success(request):
    return render(request,"home/success.html",{})


def about(request):
    return render(request, "home/about.html", {})


