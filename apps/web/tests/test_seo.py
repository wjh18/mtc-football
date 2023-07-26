"""
Tests for SEO related features.
"""

from http import HTTPStatus

from django.test import SimpleTestCase


class RobotsTest(SimpleTestCase):
    databases = "__all__"

    def test_get(self):
        response = self.client.get("/robots.txt")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response["content-type"], "text/plain")
        lines = response.content.decode().splitlines()
        self.assertEqual(lines[0], "User-Agent: *")

    def test_post(self):
        response = self.client.post("/robots.txt")

        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)
