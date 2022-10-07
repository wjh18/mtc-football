from django.apps import apps
from django.db.models import F

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

    # Create 32 teams in the correct confs and divs
    team_dicts = read_team_info_from_csv()

    Team.objects.bulk_create(
        [
            Team(
                location=team_dict["loc"],
                name=team_dict["name"],
                abbreviation=team_dict["abbr"],
                conference=Conference.objects.get(
                    name=team_dict["conf"], league=league
                ),
                division=Division.objects.get(
                    name=team_dict["div"], conference=F("conference")
                ),
                league=league,
            )
            for team_dict in team_dicts
        ]
    )

    # Create first season in league
    Season.objects.create(league=league)
