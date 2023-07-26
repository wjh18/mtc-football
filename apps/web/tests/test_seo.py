"""
Tests for SEO related features.
"""

from http import HTTPStatus

from django.contrib.sites.models import Site
from django.test import TestCase


class RobotsTest(TestCase):
    """Tests for robots.txt."""

    def test_get(self):
        response = self.client.get("/robots.txt")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response["content-type"], "text/plain")
        lines = response.content.decode().splitlines()
        self.assertEqual(lines[0], "User-Agent: *")

    def test_post(self):
        response = self.client.post("/robots.txt")

        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)


class SitemapsTest(TestCase):
    """Tests for static sitemap URLs."""

    def setUp(self):
        self.response = self.client.get("/sitemap.xml")
        self.site = Site.objects.get_current()

    def test_sitemap_status_and_content_type(self):
        self.assertEqual(self.response.status_code, HTTPStatus.OK)
        self.assertEqual(self.response["content-type"], "application/xml")

    def test_home_page_in_sitemap(self):
        self.assertContains(self.response, f"https://{self.site.domain}/")

    def test_about_page_in_sitemap(self):
        self.assertContains(self.response, f"https://{self.site.domain}/about/")

    def test_contact_page_in_sitemap(self):
        self.assertContains(self.response, f"https://{self.site.domain}/contact/")

    def test_privacy_page_in_sitemap(self):
        self.assertContains(self.response, f"https://{self.site.domain}/privacy/")

    def test_terms_page_in_sitemap(self):
        self.assertContains(self.response, f"https://{self.site.domain}/terms/")
