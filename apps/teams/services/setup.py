import csv
import os

from django.apps import apps
from django.db.models import F

from apps.personnel.services.setup import create_team_players

from ..models import Team


def read_team_info_from_csv():
    """
    Read locations, names, and abbr of teams from CSV.
    Return a dict w/ abbrs as keys and remaining data as values.
    """
    with open(
        os.path.join(os.path.dirname(__file__), "../data/nfl-teams.csv"), "r"
    ) as team_data_file:

        team_reader = csv.reader(team_data_file, delimiter=",")
        next(team_reader)  # Skip headings

        team_dicts = []
        for row in team_reader:
            loc, name, abbr, conf, div = row[1:6]
            team_dict = {
                "loc": loc,
                "name": name,
                "abbr": abbr,
                "conf": conf,
                "div": f"{conf} {div}",
            }
            team_dicts.append(team_dict)

    return team_dicts


def create_teams(league):
    """
    Create 32 teams in the correct confs and divs
    Called from create_league_structure() in apps.leagues.services.setup
    """
    Conference = apps.get_model("leagues.Conference")
    Division = apps.get_model("leagues.Division")
    team_dicts = read_team_info_from_csv()
    team_objs = Team.objects.bulk_create(
        [
            Team(
                location=team_dict["loc"],
                name=team_dict["name"],
                abbreviation=team_dict["abbr"],
                slug=team_dict["abbr"],
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
    for team in team_objs:
        create_team_players(team)
