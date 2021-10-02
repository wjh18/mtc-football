import datetime

    
# Progress by week
def advance_season_weeks(season, weeks=1):
    season.current_date += datetime.timedelta(days=(weeks*7))
    season.week_number += weeks
    if season.week_number == 19:
        season.phase = 5
    season.save()