from django.contrib import sitemaps
from django.urls import reverse


class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = "daily"
    protocol = "https"

    def items(self):
        return ["web:home", "web:about", "web:contact", "web:terms", "web:privacy"]

    def location(self, item):
        return reverse(item)
