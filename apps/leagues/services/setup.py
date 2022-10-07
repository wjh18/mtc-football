from django.apps import apps

from apps.seasons.models import Season
from apps.teams.models import Team
from apps.teams.services.setup import read_team_info_from_csv

CONFERENCE_NAMES = ["American", "National"]
DIVISION_CARDINALS = ["East", "North", "South", "West"]


def create_league_structure(league):
    """
    Creates a league's structure and teams.
    Called during initial save of new League instance in models.py.
    """
    # Can't manually import these due to circular import in models.py
    Conference = apps.get_model("leagues.Conference")
    Division = apps.get_model("leagues.Division")

    # Create conferences and divisions
    conf_objs = Conference.objects.bulk_create(
        [Conference(league=league, name=conf_name) for conf_name in CONFERENCE_NAMES]
    )
    Division.objects.bulk_create(
        [
            Division(conference=conf, name=f"{conf.name} {cardinal}")
            for cardinal in DIVISION_CARDINALS
            for conf in conf_objs
        ]
    )

    # Read team information from CSV
    team_info = read_team_info_from_csv()
    abbreviations = [*team_info.keys()]
    team_info = [*team_info.values()]

    # Create 32 teams for this league
    for team in range(0, 32):
        team_conference = Conference.objects.get(name=team_info[team][2], league=league)
        team_division = Division.objects.get(
            name=team_info[team][3], conference=team_conference
        )
        Team.objects.create(
            location=team_info[team][0],
            name=team_info[team][1],
            abbreviation=abbreviations[team],
            division=team_division,
            conference=team_conference,
            league=league,
        )

    # Create first season in league
    Season.objects.create(league=league)
