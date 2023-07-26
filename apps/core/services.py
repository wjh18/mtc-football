from django.conf import settings


def show_toolbar(request):
    """
    Callback that overrides debug_toolbar.middleware.show_toolbar
    to customize when to display the toolbar.
    """
    default_config = (
        settings.DEBUG and request.META.get("REMOTE_ADDR") in settings.INTERNAL_IPS
    )
    return default_config and settings.SHOW_TOOLBAR
