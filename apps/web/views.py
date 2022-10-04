from django.views.generic import TemplateView


class HomePageView(TemplateView):
    template_name = "web/home.html"


class AboutPageView(TemplateView):
    template_name = "web/about.html"


class ContactPageView(TemplateView):
    template_name = "web/contact.html"
