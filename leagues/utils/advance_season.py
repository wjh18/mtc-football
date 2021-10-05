import datetime


def advance_season_weeks(season, weeks=1):
    """Advance season by week"""
    season.current_date += datetime.timedelta(days=(weeks * 7))

    ## Sim to end of regular season if < 4 weeks are remaining
    # weeks_until_playoffs = 19 - season.week_number
    # if weeks_until_playoffs < 4:
    #     season.week_number += weeks_until_playoffs
    # else:
    #     season.week_number += weeks

    season.week_number += weeks

    # Change phase from regular season to playoffs
    if season.week_number == 19:
        season.phase = 5

    season.save()
