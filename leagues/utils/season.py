import datetime

from django.apps import apps
from django.contrib import messages

from .playoffs import (
    advance_playoff_round, sim_round_matchups,
    sim_round_matchups, update_running_playoff_clinches)
from .standings import dupe_standings_for_byes, update_standings
from .rankings import update_rankings
from ..models import Matchup


def advance_season_by_weeks(request, season, weeks=False):
    """Advance the season by X number of weeks."""
    current_week = season.week_number
    current_phase = season.get_phase_display()
    is_regular_season = current_phase == 'Regular Season'
    is_playoffs = current_phase == 'Playoffs'
    is_offseason = current_phase == 'Offseason'
    message_type = messages.SUCCESS

    # Limit number of sim weeks to at most the end of the phase
    if is_regular_season:
        week_limit = 18 - (current_week - 1)
    elif is_playoffs:
        week_limit = 22 - (current_week - 1)      
    elif is_offseason:
        week_limit = 1      
    if not weeks or weeks > week_limit:
            weeks = week_limit
            
    # Simulate based on selected or limited number of weeks    
    for week_num in range(current_week, current_week + weeks):
        if is_regular_season: 
            new_message = advance_regular_season(season, weeks, week_num)
        elif is_playoffs:        
            new_message = advance_playoffs(season, weeks, week_num) 
        elif is_offseason:
            new_message = advance_to_next_season(season)
        else:
            new_message = f"""Sorry, we aren't in the right part
                           of the season for that!"""
            message_type = messages.WARNING
            break

        season.current_date += datetime.timedelta(days=7)
        season.week_number += 1
        season.save()
    
    messages.add_message(request, message_type, new_message)


def advance_regular_season(season, weeks, week_num):
    """Advance the regular season, update standings and rankings."""
    success_message = f'Advanced regular season by {weeks} week(s).'   
    
    matchups = Matchup.objects.filter(
                season=season, week_number=week_num,
                scoreboard__is_final=False)   
    dupe_standings_for_byes(season, week_num)
    update_standings(season, week_num, matchups)
    update_rankings(season)
    update_running_playoff_clinches(season)

    if week_num == 18:
        # Enter playoffs, generate wildcard matchups
        season.phase = 5
        advance_playoff_round(season)
        success_message += f''' The first week of the postseason 
            has begun.'''
            
    return success_message


def advance_playoffs(season, weeks, week_num):
    """Advance the playoffs depending on round."""
    success_message = f'Advanced playoffs by {weeks} week(s).'
                        
    if week_num == 19:
        advance_playoff_round(season, 'wildcard')
    elif week_num == 20:
        advance_playoff_round(season, 'divisional')
    elif week_num == 21:
        advance_playoff_round(season, 'conference')
    elif week_num == 22:
        advance_playoff_round(season, 'championship')
        season.phase = 6
        success_message += f""" You've entered the offseason.
            Advance at least one week to start a new season."""
            
    return success_message


def advance_to_next_season(season):
    """End the current season and create a new one."""
    success_message = f'A new season has begun.'
    season.is_current = False
    season.save()
    
    Season = apps.get_model('leagues.Season')
    new_season_start = season.start_date + datetime.timedelta(days=365)
    Season.objects.create(league=season.league,
                          season_number=season.season_number + 1,
                          start_date=new_season_start,
                          current_date=new_season_start)
    
    return success_message