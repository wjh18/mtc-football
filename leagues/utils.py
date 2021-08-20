import os
import random
import csv


def read_player_names_from_csv():
    """
    Read names of retired NFL players from CSV, shuffle them randomly
    Store in dict with first names as keys, last names as values
    """
    with open(os.path.join(os.path.dirname(__file__), 'data/retired-players.csv'), 'r') as player_name_file:
        name_reader = csv.reader(player_name_file, delimiter=',')
        player_names = [[row[1], row[2]] for row in name_reader if ('last_name' or '.') not in row[2]]

        # Shuffle first and last names
        first_names = [names[0] for names in player_names]
        last_names = [names[1] for names in player_names]
        random.shuffle(first_names)
        random.shuffle(last_names)
        player_names = list(zip(first_names, last_names))

    return player_names

def read_team_info_from_csv():
    """
    Read locations, mascots, and acronyms of teams from CSV
    Store in dict w/ team locations as keys, list of mascots / acronyms as values
    """
    with open(os.path.join(os.path.dirname(__file__), 'data/nfl-teams.csv'), 'r') as team_data_file:
        team_reader = csv.reader(team_data_file, delimiter=',')
        team_info = {row[3]: [row[1], row[2]] for row in team_reader if row[1] != 'Name'}

    return team_info

def generate_player_attributes():
    """
    Return a list of 53 dictionaries containing player attributes
    that map to Player model fields. Called in Team model save() method
    """

    # Position constraints per 53 man roster
    # i.e. position_dist['QB'][1] means start with 3 QB's on the roster
    position_dist = {
        'QB': [0, 3], 'HB': [0, 3], 'FB': [0, 1], 'WR': [0, 6], 'TE': [0, 3],
        'LT': [0, 2], 'LG': [0, 2], 'C': [0, 2], 'RG': [0, 2], 'RT': [0, 2],
        'DE': [0, 4], 'DT': [0, 4], 'OLB': [0, 4], 'MLB': [0, 3], 'CB': [0, 6], 'FS': [0, 2],
        'SS': [0, 2], 'K': [0, 1], 'P': [0, 1]
    }

    player_list = []

    for p in range(0, 53):
        player = {}

        # Only assign a player a position that isn't filled on the roster
        for pos, dist in position_dist.items():
            if dist[0] < dist[1]:
                player['position'] = pos
                dist[0] += 1
                break
            else:
                continue
        
        player_list.append(player)
        
    # single_player = {
    #     'age': 25,
    #     'experience': 3,
    #     'position': 'RB',
    #     'prototype': 'Power',
    #     'overall_rating': 99.99,
    #     'potential': 99.99,
    #     'confidence': 99.99,
    #     'iq': 120,
    #     'speed': 99.99,
    #     'strength': 99.99,
    #     'agility': 99.99,
    #     'awareness': 99.99,
    #     'stamina': 99.99,
    #     'injury': 99.99,
    #     'run_off': 99.99,
    #     'pass_off': 99.99,
    #     'special_off': 99.99,
    #     'run_def': 99.99,
    #     'pass_def': 99.99,
    #     'special_def': 99.99
    # }
    return player_list