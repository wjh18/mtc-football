import datetime

    
# Progress by week
def advance_season_weeks(season, weeks=1):
    season.current_date += datetime.timedelta(days=(weeks*7))
    season.week_number += weeks
    if season.week_number == 17:
        season.phase = 5
    season.save()
    
# Progress to a specific phase, end of current phase, or end of season
def advance_season_phases(season, phases):
    season.phase += phases
    season.save()