from .forms import AdvanceSeasonForm


def advance_season_form(request):
    """
    Custom context processor (added to config/settings.py).
    Makes AdvanceSeasonForm available in leagues/_league_base.html
    as {{ advance_season_form }}.
    """
    return {
        'advance_season_form': AdvanceSeasonForm()
    }