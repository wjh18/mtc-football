from django.apps import apps

from apps.seasons.services.setup import create_first_season
from apps.teams.services.setup import create_teams

CONFERENCE_NAMES = ["American", "National"]
DIVISION_CARDINALS = ["East", "North", "South", "West"]


def create_league_structure(league):
    """
    Creates a league's structure, teams and first season.
    Called during initial save() of new League instance in models.py.
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

    create_teams(league)
    create_first_season(league)
