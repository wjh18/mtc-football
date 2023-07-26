"""
Tests for static web pages.

Note:
    `databases = "__all__"` is a workaround for SimpleTestCase
    due to a bug in pytest-django outlined in issue#472. Default fixtures
    set up a test database for every test case, even when not needed.
"""

from django.test import SimpleTestCase
from django.urls import resolve, reverse

from .. import views


class ContactPageTest(SimpleTestCase):
    """Tests for static contact page."""

    databases = "__all__"

    def setUp(self):
        url = reverse("web:contact")
        self.response = self.client.get(url)

    def test_contact_page_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_contact_page_template(self):
        self.assertTemplateUsed(self.response, "web/contact.html")

    def test_contact_page_contains_correct_html(self):
        self.assertContains(self.response, "Contact")

    def test_contact_page_does_not_contain_incorrect_html(self):
        self.assertNotContains(self.response, "Hi there! I should not be on the page.")

    def test_contact_page_url_resolves_contactpageview(self):
        view = resolve("/contact/")
        self.assertEqual(view.func.__name__, views.contact_view.__name__)


class HomePageTest(SimpleTestCase):
    """Tests for static home page."""

    databases = "__all__"

    def setUp(self):
        url = reverse("web:home")
        self.response = self.client.get(url)

    def test_home_page_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_home_page_template(self):
        self.assertTemplateUsed(self.response, "web/home.html")

    def test_home_page_contains_correct_html(self):
        self.assertContains(self.response, "Welcome to Move the Chains football!")

    def test_home_page_does_not_contain_incorrect_html(self):
        self.assertNotContains(self.response, "Hi there! I should not be on the page.")

    def test_home_page_url_resolves_homepageview(self):
        view = resolve("/")
        self.assertEqual(view.func.__name__, views.HomePageView.as_view().__name__)


class AboutPageTest(SimpleTestCase):
    """Tests for static about page."""

    databases = "__all__"

    def setUp(self):
        url = reverse("web:about")
        self.response = self.client.get(url)

    def test_about_page_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_about_page_template(self):
        self.assertTemplateUsed(self.response, "web/about.html")

    def test_about_page_contains_correct_html(self):
        self.assertContains(self.response, "About")

    def test_about_page_does_not_contain_incorrect_html(self):
        self.assertNotContains(self.response, "Hi there! I should not be on the page.")

    def test_about_page_url_resolves_aboutpageview(self):
        view = resolve("/about/")
        self.assertEqual(view.func.__name__, views.AboutPageView.as_view().__name__)


class PrivacyPageTest(SimpleTestCase):
    """Tests for static privacy policy page."""

    databases = "__all__"

    def setUp(self):
        url = reverse("web:privacy")
        self.response = self.client.get(url)

    def test_privacy_page_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_privacy_page_template(self):
        self.assertTemplateUsed(self.response, "web/privacy.html")

    def test_privacy_page_contains_correct_html(self):
        self.assertContains(self.response, "Privacy Policy")

    def test_privacy_page_does_not_contain_incorrect_html(self):
        self.assertNotContains(self.response, "Hi there! I should not be on the page.")

    def test_privacy_page_url_resolves_privacypageview(self):
        view = resolve("/privacy/")
        self.assertEqual(view.func.__name__, views.PrivacyPageView.as_view().__name__)


class TermsPageTest(SimpleTestCase):
    """Tests for static terms of use page."""

    databases = "__all__"

    def setUp(self):
        url = reverse("web:terms")
        self.response = self.client.get(url)

    def test_terms_page_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_terms_page_template(self):
        self.assertTemplateUsed(self.response, "web/terms.html")

    def test_terms_page_contains_correct_html(self):
        self.assertContains(self.response, "Terms of Use")

    def test_terms_page_does_not_contain_incorrect_html(self):
        self.assertNotContains(self.response, "Hi there! I should not be on the page.")

    def test_terms_page_url_resolves_termspageview(self):
        view = resolve("/terms/")
        self.assertEqual(view.func.__name__, views.TermsPageView.as_view().__name__)
