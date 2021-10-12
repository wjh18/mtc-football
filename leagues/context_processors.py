from .forms import AdvanceSeasonForm


def advance_season_form(request):
    return {
        'advance_season_form': AdvanceSeasonForm()
    }