from django.contrib import admin

from .models import SiteSettings


class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ("meta_description",)


admin.site.register(SiteSettings)
