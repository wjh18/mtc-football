import csv
import os

from django.apps import apps

from apps.personnel.services.setup import (
    create_team_players,
    read_player_names_from_csv,
)

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
    team_dicts = read_team_info_from_csv()

    confs = league.conferences.all()
    Division = apps.get_model("leagues.Division")
    divs = Division.objects.filter(conference__in=confs)

    def update_team_dict_with_entity(entities, entity_name):
        """Replace conf and div names with their objects"""
        for entity in entities:
            if entity.name == team_dict[entity_name]:
                team_dict[entity_name] = entity

    for team_dict in team_dicts:
        update_team_dict_with_entity(confs, "conf")
        update_team_dict_with_entity(divs, "div")

    team_objs = Team.objects.bulk_create(
        [
            Team(
                location=team_dict["loc"],
                name=team_dict["name"],
                abbreviation=team_dict["abbr"],
                slug=team_dict["abbr"],
                conference=team_dict["conf"],
                division=team_dict["div"],
                league=league,
            )
            for team_dict in team_dicts
        ]
    )
    player_names = read_player_names_from_csv()
    for team in team_objs:
        create_team_players(league, team, player_names)
