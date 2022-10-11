import datetime

from django.apps import apps
from django.utils.text import slugify

from .schedule import create_schedule


def create_first_season(league):
    """
    Create the first season in a league
    Called from create_league_structure() in apps.leagues.services.setup
    """
    Season = apps.get_model("seasons.Season")
    Season.objects.create(league=league)


def create_season_details(season):
    """
    Generates a season's schedule, matchups, scoreboards and initial rankings.
    Called during initial save of new Season instance in models.py.
    """
    Matchup = apps.get_model("matchups.Matchup")
    Scoreboard = apps.get_model("matchups.Scoreboard")
    TeamStanding = apps.get_model("seasons.TeamStanding")

    matchups = create_schedule(season)

    # Bulk create Matchups based on schedule
    Matchup.objects.bulk_create(
        [
            Matchup(
                home_team=matchup[0],
                away_team=matchup[1],
                season=season,
                week_number=week_num,
                date=season.start_date + (week_num * datetime.timedelta(days=7)),
                slug=slugify(
                    f"{matchup[1].abbreviation}-{matchup[0].abbreviation} \
                -week-{week_num}-season-{season.season_number}"
                ),
            )
            for week_num in range(1, len(matchups) + 1)
            for matchup in matchups[week_num - 1]
        ]
    )

    # Add matchup type fields and update instances
    matchup_qs = Matchup.objects.filter(season=season)
    matchup_list = []
    for matchup in matchup_qs:
        if matchup.home_team.division == matchup.away_team.division:
            matchup.is_divisional = True
        if matchup.home_team.conference == matchup.away_team.conference:
            matchup.is_conference = True
        matchup_list.append(matchup)
    Matchup.objects.bulk_update(matchup_list, ["is_divisional", "is_conference"])

    # Bulk create Scoreboards for new Matchups
    Scoreboard.objects.bulk_create(
        [Scoreboard(matchup=matchup) for matchup in matchup_list]
    )

    # Bulk create TeamStanding for each team
    TeamStanding.objects.bulk_create(
        [TeamStanding(team=team, season=season) for team in season.league.teams.all()]
    )
