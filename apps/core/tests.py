from django.contrib.sites.models import Site
from django.test import Client, TestCase
from django.urls import reverse


class ContextProcessorTests(TestCase):
    def test_global_site_context_processor(self):
        """
        Test whether global site context is available and equals current site
        """
        c = Client()
        response = c.get(reverse("web:home"))
        current_site = Site.objects.get_current()
        current_settings = current_site.settings
        try:
            site_context = response.context["site"]
        except KeyError:
            site_context = None
        try:
            site_settings = site_context.settings
        except AttributeError:
            site_settings = None
        self.assertIsNotNone(site_context)
        self.assertIsNotNone(site_settings)
        self.assertEqual(site_context, current_site)
        self.assertEqual(site_settings, current_settings)
