import datetime

from django.apps import apps

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


def advance_to_next_season(season):
    """End the current season and create a new one."""
    # End the current season
    season.is_current = False
    season.save()
    # Create a new season, is current by default
    Season = apps.get_model('leagues.Season')
    new_season_start = season.start_date + datetime.timedelta(years=1)
    Season.objects.create(league=season.league,
                          season_number=season.season_number + 1,
                          date=new_season_start)