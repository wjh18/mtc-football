import datetime

from django.apps import apps
from django.contrib import messages

from ..models import Season
from .playoffs import advance_playoff_round, update_running_playoff_clinches
from .rankings import update_rankings
from .standings import update_standings


def advance_season_by_weeks(request, season, weeks=False):
    """Advance the season by X number of weeks."""
    current_week = season.week_number
    current_phase = season.get_phase_display()
    message_type = messages.SUCCESS

    round_limits_and_funcs = {
        "Regular Season": (17 - current_week, advance_regular_season),
        "Playoffs": (21 - current_week, advance_playoffs),
        "Offseason": (1, advance_to_next_season),
    }

    # Limit number of sim weeks to at most the end of the phase
    week_limit = round_limits_and_funcs[current_phase][0]
    if not weeks or weeks > week_limit:
        weeks = week_limit

    # Simulate based on selected or limited number of weeks
    for week_num in range(current_week, current_week + weeks):
        try:
            adv_func = round_limits_and_funcs[current_phase][1]
            if current_phase == "Offseason":
                new_message = adv_func(season)
            else:
                new_message = adv_func(season, weeks, week_num)
        except KeyError:
            new_message = "Sorry, we aren't in the right part of the season for that!"
            message_type = messages.WARNING
            break

        season.current_date += datetime.timedelta(days=7)
        season.week_number += 1
        season.save()

    messages.add_message(request, message_type, new_message)


def advance_regular_season(season, weeks, week_num):
    """Advance the regular season, update standings and rankings."""
    success_message = f"Advanced regular season by {weeks} week(s)."

    Matchup = apps.get_model("matchups.Matchup")
    matchups = Matchup.objects.filter(
        season=season, week_number=week_num, is_final=False
    )
    update_standings(season, matchups)
    update_rankings(season)
    update_running_playoff_clinches(season)

    if week_num == 18:
        # Enter playoffs, generate wildcard matchups
        season.phase = 5
        advance_playoff_round(season)
        success_message += " The first week of the postseason has begun."

    return success_message


def advance_playoffs(season, weeks, week_num):
    """Advance the playoffs depending on round."""
    success_message = f"Advanced playoffs by {weeks} week(s)."

    round_weeks = {19: "WLD", 20: "DIV", 21: "CNF", 22: "SHP"}
    round_name = round_weeks[week_num]
    advance_playoff_round(season, round_name)

    # Advance to next season after championship
    if round_name == "SHP":
        season.phase = 6
        success_message += " You've entered the offseason. \
            Advance at least one week to start a new season."

    return success_message


def advance_to_next_season(season):
    """End the current season and create a new one."""
    success_message = "A new season has begun."
    season.is_current = False
    season.save()

    new_season_start = season.start_date + datetime.timedelta(days=365)
    Season.objects.create(
        league=season.league,
        season_number=season.season_number + 1,
        start_date=new_season_start,
        current_date=new_season_start,
    )

    return success_message
