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


def font_awesome_kit_id(request):
    """
    Adds Font Awesome Kit ID to the context of all requests.
    """
    if settings.FONT_AWESOME_KIT_ID:
        return {
            "FA_KIT_ID": settings.FONT_AWESOME_KIT_ID,
        }
    else:
        return {}
