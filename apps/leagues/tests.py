from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import League


class LeagueViewTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="leagueuser@example.com", password="testpass123", is_active=True
        )
        self.league = League(
            name="Test League",
            user=self.user,
            gm_name="Test GM",
        )
        self.league.save(isolate=True)

    def test_league_list(self):
        self.assertEqual(f"{self.league.name}", "Test League")
        self.assertEqual(f"{self.league.gm_name}", "Test GM")

    def test_league_list_view_for_logged_in_user(self):
        self.client.login(email="leagueuser@example.com", password="testpass123")
        response = self.client.get(reverse("leagues:league_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test League")
        self.assertTemplateUsed(response, "leagues/league_list.html")

    def test_league_list_view_for_logged_out_user(self):
        self.client.logout()
        response = self.client.get(reverse("leagues:league_list"))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "%s?next=/leagues/" % (reverse("users:login")))
        response = self.client.get("%s?next=/leagues/" % (reverse("users:login")))
        self.assertContains(response, "Log In")
