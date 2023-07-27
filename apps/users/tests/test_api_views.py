from django.contrib.auth import get_user, get_user_model
from django.test import TestCase
from rest_framework.test import APIClient


class UserAuthViewTests(TestCase):
    """
    Tests for views relating to user auth. CSRF validation is built into
    DRF SessionAuthentication so only custom functionality needs to be tested.
    """

    def setUp(self):
        User = get_user_model()
        self.email = "user@example.com"
        self.password = "foo"
        self.user = User.objects.create_user(
            email=self.email, password=self.password, is_active=True
        )

    def test_auth_user_is_logged_out_200_ok(self):
        client = APIClient(enforce_csrf_checks=False)
        logged_in = client.login(email=self.email, password=self.password)
        self.assertTrue(logged_in)

        # Log user out
        response = client.post("/api/accounts/logout/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"success": "Logout successful."})

        # Confirm user was logged out
        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)

        client.logout()

    def test_user_login_with_creds_202_accepted(self):
        client = APIClient(enforce_csrf_checks=False)
        response = client.post(
            "/api/accounts/login/",
            {"email": self.email, "password": self.password},
        )
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.data, {"success": "Login successful."})

    def test_user_login_no_creds_400_bad_request(self):
        client = APIClient(enforce_csrf_checks=False)
        response = client.post("/api/accounts/login/")
        self.assertEqual(response.status_code, 400)

    def test_user_login_no_password_400_bad_request(self):
        client = APIClient(enforce_csrf_checks=False)
        response = client.post("/api/accounts/login/", {"email": self.email})
        self.assertEqual(response.status_code, 400)

    def test_user_login_no_email_400_bad_request(self):
        client = APIClient(enforce_csrf_checks=False)
        response = client.post("/api/accounts/login/", {"password": self.password})
        self.assertEqual(response.status_code, 400)

    def test_whoami_response_200_ok(self):
        client = APIClient(enforce_csrf_checks=False)
        client.force_login(user=self.user)
        response = client.get("/api/accounts/whoami/")
        self.assertEqual(response.status_code, 200)
        expected = {
            # Excludes date fields
            "email": self.user.email,
            "is_staff": self.user.is_staff,
            "is_active": self.user.is_active,
        }
        for k in expected.keys():
            self.assertEqual(response.data[k], expected[k])

    def test_csrf_cookie_in_response_200_ok(self):
        client = APIClient(enforce_csrf_checks=False)
        response = client.get("/api/accounts/csrf/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"success": "CSRF cookie set"})
        csrf_token = response.cookies.get("csrftoken")
        self.assertIsNotNone(csrf_token)
