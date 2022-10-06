import datetime

from django.apps import apps
from django.utils.text import slugify

from .schedule import create_schedule


def create_season_details(season):
    """
    Generates a season's schedule, matchups, scoreboards and initial rankings.
    Called during initial save of new Team instance in models.py.
    """
    Matchup = apps.get_model("matchups.Matchup")
    Scoreboard = apps.get_model("matchups.Scoreboard")
    TeamStanding = apps.get_model("seasons.TeamStanding")

    # Generate nested list of weeks and matchups
    league_id = season.league.pk
    matchups = create_schedule(str(league_id))

    # Bulk create Matchups based on schedule
    matchup_objs = Matchup.objects.bulk_create(
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
    for matchup in matchup_objs:
        if matchup.home_team.division == matchup.away_team.division:
            matchup.is_divisional = True
        if matchup.home_team.conference == matchup.away_team.conference:
            matchup.is_conference = True
    Matchup.objects.bulk_update(matchup_objs, ["is_divisional", "is_conference"])

    # Bulk create Scoreboards for new Matchups
    Scoreboard.objects.bulk_create(
        [Scoreboard(matchup=matchup) for matchup in matchup_objs]
    )

    # Bulk create TeamStanding for each team
    TeamStanding.objects.bulk_create(
        [TeamStanding(team=team, season=season) for team in season.league.teams.all()]
    )
