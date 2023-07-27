from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.http import Http404
from django.test import RequestFactory, TestCase
from django.views.defaults import (
    bad_request,
    page_not_found,
    permission_denied,
    server_error,
)


class ErrorTemplateTest(TestCase):
    """
    Test that Django's default error views render custom error templates.
    """

    def test_400_template(self):
        request = RequestFactory().get("/placeholder-url/")
        response = bad_request(request, SuspiciousOperation)
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, "Bad Request", status_code=400)

    def test_403_template(self):
        request = RequestFactory().get("/placeholder-url/")
        response = permission_denied(request, PermissionDenied)
        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "Permission Denied", status_code=403)

    def test_404_template(self):
        request = RequestFactory().get("/placeholder-url/")
        response = page_not_found(request, Http404())
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Page Not Found", status_code=404)

    def test_500_template(self):
        request = RequestFactory().get("/placeholder-url/")
        response = server_error(request)
        self.assertEqual(response.status_code, 500)
        self.assertContains(response, "Server Error", status_code=500)
