from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist


def user_team(request):
    """
    Make active UserTeam available in template context
    """
    if hasattr(request, "resolver_match"):
        League = apps.get_model("leagues.League")
        league_slug = request.resolver_match.kwargs.get("league")
    try:
        league = League.objects.get(slug=league_slug)
        active_user_team = league.user_teams.get(is_active_team=True)
        return {
            "active_user_team": active_user_team,
        }
    except ObjectDoesNotExist:
        return {}
