from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import Client, TestCase
from django.urls import reverse

from .models import League


class LeagueViewTest(TestCase):
    
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='leagueuser',
            email='leagueuser@email.com',
            password='testpass123'
        )
        self.league = League.objects.create(
            name='Test League',
            commissioner=self.user,
            commissioner_name='Test Commissioner',
        )

    def test_league_list(self):
        self.assertEqual(f'{self.league.name}', 'Test League')
        self.assertEqual(f'{self.league.commissioner_name}', 'Test Commissioner')

    def test_league_list_view_for_logged_in_user(self):
        self.client.login(email='leagueuser@email.com', password='testpass123')
        response = self.client.get(reverse('league_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test League')
        self.assertTemplateUsed(response, 'leagues/league_list.html')

    def test_league_list_view_for_logged_out_user(self):
        self.client.logout()
        response = self.client.get(reverse('league_list'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, '%s?next=/leagues/' % (reverse('account_login')))
        response = self.client.get(
            '%s?next=/leagues/' % (reverse('account_login')))
        self.assertContains(response, 'Log In')


