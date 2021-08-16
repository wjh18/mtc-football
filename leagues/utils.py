import os
import random
import csv


def read_player_names_from_csv():
    # Read names of retired NFL players from CSV, shuffle them randomly
    # Store in dict with first names as keys, last names as values
    with open(os.path.join(os.path.dirname(__file__), 'data/retired-players.csv'), 'r') as player_name_file:
        name_reader = csv.reader(player_name_file, delimiter=',')
        player_names = {row[1]: row[2] for row in name_reader}

        # Shuffle first and last names
        first_names = list(player_names.keys())
        random.shuffle(first_names)
        player_names = dict(zip(first_names, player_names))

    return player_names

def read_team_info_from_csv():
    # Read locations, mascots, and acronyms of teams from CSV
    # Store in dict w/ team locations as keys, list of mascots / acronyms as values
    with open(os.path.join(os.path.dirname(__file__), 'data/nfl-teams.csv'), 'r') as team_data_file:
        team_reader = csv.reader(team_data_file, delimiter=',')
        team_info = {row[1]: [row[2], row[3]] for row in team_reader if row[1] != 'Name'}

    return team_info