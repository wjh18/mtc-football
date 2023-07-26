"""
Tests for web forms.
"""

from django.test import TestCase
from django.urls import reverse

from ..forms import ContactForm


class ContactFormViewTest(TestCase):
    """Tests for contact form view."""

    def setUp(self):
        self.url = reverse("web:contact")
        self.g_response = self.client.get(self.url)
        self.p_response_valid = self.client.post(
            self.url,
            {
                "email": "test@example.com",
                "subject": "Test Subject",
                "message": "Test message",
            },
        )
        self.p_response_invalid = self.client.post(
            self.url, {"email": "test@example.com", "subject": "Test Subject"}
        )

    def test_get_form_in_context(self):
        response = self.g_response
        self.assertIsInstance(response.context["form"], ContactForm)

    def test_get_form_is_unbound(self):
        response = self.g_response
        self.assertFalse(response.context["form"].is_bound)

    def test_post_valid_form_status_code(self):
        response = self.p_response_valid
        self.assertEqual(response.status_code, 200)

    def test_post_valid_form_template_used(self):
        response = self.p_response_valid
        self.assertTemplateUsed(response, "web/success.html")

    def test_post_invalid_form_in_context(self):
        response = self.p_response_invalid
        self.assertIsInstance(response.context["form"], ContactForm)

    def test_post_invalid_form_is_bound(self):
        response = self.p_response_invalid
        self.assertTrue(response.context["form"].is_bound)

    def test_post_invalid_form_status_code(self):
        response = self.p_response_invalid
        self.assertEqual(response.status_code, 200)

    def test_post_invalid_form_template_used(self):
        response = self.p_response_invalid
        self.assertTemplateUsed(response, "web/contact.html")

    def test_post_form_missing_message_invalid(self):
        response = self.client.post(
            self.url, {"email": "test@example.com", "subject": "Test Subject"}
        )
        self.assertFalse(response.context["form"].is_valid())

    def test_post_form_missing_subject_invalid(self):
        response = self.client.post(
            self.url, {"email": "test@example.com", "message": "Test message"}
        )
        self.assertFalse(response.context["form"].is_valid())

    def test_post_form_missing_email_invalid(self):
        response = self.client.post(
            self.url, {"subject": "Test Subject", "message": "Test message"}
        )
        self.assertFalse(response.context["form"].is_valid())
