import datetime


def progress_season(season, days):
    season.current_date += datetime.timedelta(days=days)
    if days == 7:
        season.week_number += 1
    if season.week_number == 17:
        season.phase = 7
    season.save()