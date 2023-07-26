from django.contrib import messages
from django.core.mail import mail_admins
from django.shortcuts import render
from django.views.generic import TemplateView

from .forms import ContactForm


def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            subject = form.cleaned_data["subject"]
            email_subject = f"New contact {email}: {subject}"
            email_message = form.cleaned_data["message"]
            mail_admins(email_subject, email_message)
            messages.add_message(request, messages.SUCCESS, "Message sent.")
            return render(request, "web/success.html")
    else:
        form = ContactForm()

    context = {"form": form}
    return render(request, "web/contact.html", context)


class HomePageView(TemplateView):
    template_name = "web/home.html"


class AboutPageView(TemplateView):
    template_name = "web/about.html"


class TermsPageView(TemplateView):
    template_name = "web/terms.html"


class PrivacyPageView(TemplateView):
    template_name = "web/privacy.html"
