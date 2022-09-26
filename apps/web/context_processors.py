from django.conf import settings


def google_tag_manager_id(request):
    """
    Adds Google Tag Manager ID to the context of all requests.
    """
    if settings.GTM_ID:
        return {
            "GTM_ID": settings.GTM_ID,
        }
    else:
        return {}
