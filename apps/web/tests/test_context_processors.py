"""
Tests for custom web context processors.
"""

from django.test import Client, TestCase, override_settings
from django.urls import reverse


class GTMContextProcessorTest(TestCase):
    """Tests for GTM ID context processor."""

    @override_settings(GTM_ID="GTM-123456")
    def test_gtm_context_exists_and_equals_setting(self):
        """
        Test that GTM ID is available in context and equals setting.
        """
        c = Client()
        response = c.get(reverse("web:home"))
        gtm_context = response.context.get("GTM_ID")
        self.assertIsNotNone(gtm_context)
        self.assertEqual(gtm_context, "GTM-123456")

    @override_settings(GTM_ID="")
    def test_empty_setting_gtm_context_not_exists(self):
        """
        Test that GTM ID isn't available in context if empty setting.
        """
        c = Client()
        response = c.get(reverse("web:home"))
        gtm_context = response.context.get("GTM_ID")
        self.assertEqual(gtm_context, None)


class FAContextProcessorTest(TestCase):
    """Tests for Font Awesome Kit ID context processor."""

    @override_settings(FONT_AWESOME_KIT_ID="a123456789")
    def test_fa_context_exists_and_equals_setting(self):
        """
        Test that FA Kit ID is available in context and equals setting.
        """
        c = Client()
        response = c.get(reverse("web:home"))
        fa_context = response.context.get("FA_KIT_ID")
        self.assertIsNotNone(fa_context)
        self.assertEqual(fa_context, "a123456789")

    @override_settings(FONT_AWESOME_KIT_ID="")
    def test_empty_setting_fa_context_not_exists(self):
        """
        Test that FA Kit ID isn't available in context if empty setting.
        """
        c = Client()
        response = c.get(reverse("web:home"))
        fa_context = response.context.get("FA_KIT_ID")
        self.assertEqual(fa_context, None)
