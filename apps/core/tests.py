from django.contrib.sites.models import Site
from django.test import (
    Client,
    RequestFactory,
    SimpleTestCase,
    TestCase,
    override_settings,
)
from django.urls import reverse

from .services import show_toolbar
from .utils import env_to_bool


class EnvToBoolTest(SimpleTestCase):
    """
    Test env variable to bool conversion utility.

    We explicity use assertIs here because many Django security settings
    that are used in env variables don't accept Truthy or Falsy values.
    """

    def test_bool_returns_self(self):
        expected = True
        obj = env_to_bool(expected)
        self.assertEqual(obj, expected)
        self.assertIs(obj, True)

    def test_true_strings_return_true(self):
        for string in ("true", "True", "TRUE"):
            obj = env_to_bool(string)
            self.assertIs(obj, True)

    def non_true_returns_false(self):
        for string in ("False", "foo", "bar"):
            obj = env_to_bool(string)
            self.assertIs(obj, False)


class SiteContextProcessorTest(TestCase):
    """Tests for global site object context processor."""

    def setUp(self):
        c = Client()
        response = c.get(reverse("web:home"))

        self.current_site = Site.objects.get_current()
        try:
            self.current_settings = self.current_site.settings
        except AttributeError:
            self.current_settings = None

        self.site_context = response.context.get("site")
        try:
            self.site_settings = self.site_context.settings
        except AttributeError:
            self.site_settings = None

    def test_site_context_is_not_none(self):
        self.assertIsNotNone(self.site_context)

    def test_site_settings_is_not_none(self):
        self.assertIsNotNone(self.site_settings)

    def test_site_context_equals_current_site(self):
        self.assertEqual(self.site_context, self.current_site)

    def test_site_settings_equals_current_settings(self):
        self.assertEqual(self.site_settings, self.current_settings)


@override_settings(INTERNAL_IPS=["127.0.0.1"])
class ShowToolbarTests(TestCase):
    """
    Test custom callback to ensure Debug Toolbar is enabled or disabled
    based on settings and request headers.
    """

    def setUp(self):
        factory = RequestFactory()
        remote_addr = {"REMOTE_ADDR": "127.0.0.1"}
        self.request = factory.get("/some/url/", **remote_addr)

    @override_settings(DEBUG=True, SHOW_TOOLBAR=True)
    def test_show_toolbar_debug_true(self):
        show_tb = show_toolbar(self.request)
        self.assertTrue(show_tb)

    @override_settings(DEBUG=False, SHOW_TOOLBAR=True)
    def test_hide_toolbar_debug_false(self):
        show_tb = show_toolbar(self.request)
        self.assertFalse(show_tb)

    @override_settings(SHOW_TOOLBAR=True, DEBUG=True)
    def test_show_toolbar_setting_true(self):
        show_tb = show_toolbar(self.request)
        self.assertTrue(show_tb)

    @override_settings(SHOW_TOOLBAR=False, DEBUG=True)
    def test_hide_toolbar_setting_false(self):
        show_tb = show_toolbar(self.request)
        self.assertFalse(show_tb)


# SuperUserRequiredTest

# CreateSiteSettingsTest

# RandomStringGeneratorTest

# UniqueSlugifyTest
