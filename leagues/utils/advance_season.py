import datetime

from .playoffs_setup import setup_playoffs


def advance_season_weeks(season, weeks=1):
    """Advance season by week"""
    season.current_date += datetime.timedelta(days=(weeks * 7))
    season.week_number += weeks

    # Change phase from regular season to playoffs
    if season.week_number == 19:
        season.phase = 5
        setup_playoffs(season)

    season.save()
