import datetime


def advance_season_weeks(season, weeks=1):
    """Advance season by week"""
    season.current_date += datetime.timedelta(days=(weeks * 7))
    season.week_number += weeks

    if season.week_number == 19:
        season.phase = 5

    season.save()
