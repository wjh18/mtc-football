from django.contrib import admin

from .models import SiteSettings


class SiteSettingAdmin(admin.ModelAdmin):
    model = SiteSettings
    list_display = [
        "site",
        "meta_description",
        "twitter_handle",
        "author",
        "server_root",
        "og_type",
        "tc_type",
    ]


admin.site.register(SiteSettings, SiteSettingAdmin)
