from django.test import SimpleTestCase
from django.urls import reverse, resolve
from .views import ContactPageView, HomePageView, AboutPageView


class HomepageTests(SimpleTestCase):

    def setUp(self):
        url = reverse('pages:home')
        self.response = self.client.get(url)

    def test_homepage_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_homepage_template(self):
        self.assertTemplateUsed(self.response, 'home.html')

    def test_homepage_contains_correct_html(self):
        self.assertContains(self.response, 'Welcome to Move the Chains football!')

    def test_homepage_does_not_contain_incorrect_html(self):
        self.assertNotContains(
            self.response, 'Hi there! I should not be on the page.')
    
    def test_homepage_url_resolves_homepageview(self):
        view = resolve('/')
        self.assertEqual(
            view.func.__name__,
            HomePageView.as_view().__name__
        )


class AboutPageTests(SimpleTestCase):

    def setUp(self):
        url = reverse('pages:about')
        self.response = self.client.get(url)
    
    def test_aboutpage_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_aboutpage_template(self):
        self.assertTemplateUsed(self.response, 'about.html')

    def test_aboutpage_contains_correct_html(self):
        self.assertContains(self.response, 'About Page')

    def test_aboutpage_does_not_contain_incorrect_html(self):
        self.assertNotContains(
            self.response, 'Hi there! I should not be on the page.')

    def test_aboutpage_url_resolves_aboutpageview(self):
        view = resolve('/about/')
        self.assertEqual(
            view.func.__name__,
            AboutPageView.as_view().__name__
        )


class ContactPageTests(SimpleTestCase):

    def setUp(self):
        url = reverse('pages:contact')
        self.response = self.client.get(url)
    
    def test_contactpage_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_contactpage_template(self):
        self.assertTemplateUsed(self.response, 'contact.html')

    def test_contactpage_contains_correct_html(self):
        self.assertContains(self.response, 'Contact Page')

    def test_contactpage_does_not_contain_incorrect_html(self):
        self.assertNotContains(
            self.response, 'Hi there! I should not be on the page.')

    def test_contactpage_url_resolves_contactpageview(self):
        view = resolve('/contact/')
        self.assertEqual(
            view.func.__name__,
            ContactPageView.as_view().__name__
        )