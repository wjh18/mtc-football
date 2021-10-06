import datetime

from .playoffs_setup import (advance_to_wildcard_playoffs,
    advance_to_divisional_playoffs, advance_to_conference_playoffs,
    advance_to_championship, sim_championship_matchup)


def advance_season_weeks(season, weeks=1):
    """Advance season by week"""
    next_week = season.week_number + 1
    
    if next_week == 19:
        # Enter playoffs, generate wildcard matchups
        season.phase = 5
        advance_to_wildcard_playoffs(season)   
    if next_week == 20:
        # Sim wildcard round and advance to div round
        advance_to_divisional_playoffs(season)
    elif next_week == 21:
        # Sim div round and advance to conf round
        advance_to_conference_playoffs(season)
    elif next_week == 22:
        # Sim conf round and advance to championship
        advance_to_championship(season)
    elif next_week == 23:
        # Sim championship, enter offseason
        champion = sim_championship_matchup(season)
        season.phase = 6

    season.current_date += datetime.timedelta(days=(weeks * 7))
    season.week_number += weeks
    season.save()
