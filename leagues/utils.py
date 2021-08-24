import os
import random
import csv


def read_player_names_from_csv():
    """
    Read names of retired NFL players from CSV, shuffle them randomly.
    Store in dict with first names as keys, last names as values.
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
    Read locations, mascots, and acronyms of teams from CSV.
    Store in dict w/ team locations as keys, list of mascots / acronyms as values.
    """
    with open(os.path.join(os.path.dirname(__file__), 'data/nfl-teams.csv'), 'r') as team_data_file:
        team_reader = csv.reader(team_data_file, delimiter=',')
        team_info = {row[3]: [row[1], row[2]] for row in team_reader if row[1] != 'Name'}

    return team_info

def generate_player_attributes():
    """
    Return a list of 53 dictionaries containing player attributes
    that map to Player model fields.
    Called in leagues/models.py Team model save() method.
    """

    # Positional constraints per 53 man roster
    # position_dist[posX][0] represents how many of posX are filled
    # position_dist[posX][1] means generate Y posX's for the starting roster
    position_dist = {
        'QB': [0, 3], 'HB': [0, 3], 'FB': [0, 1], 'WR': [0, 6],
        'TE': [0, 3], 'LT': [0, 2], 'LG': [0, 2], 'C': [0, 2],
        'RG': [0, 2], 'RT': [0, 2], 'DE': [0, 4], 'DT': [0, 4],
        'OLB': [0, 4], 'MLB': [0, 3], 'CB': [0, 6], 'FS': [0, 2],
        'SS': [0, 2], 'K': [0, 1], 'P': [0, 1]
    }

    # ATTRIBUTE WEIGHTING BASED ON POS AND PROTOTYPE, IN THIS ORDER:
    # potential, confidence, iq, speed, strength, agility, awareness, stamina,
    # injury, run_off, pass_off, special_off, run_def, pass_def, special_def
    attr_dist = {
        'QB': {
            'Gunslinger': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'Scrambler': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'Field General': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        },
        'HB': {
            'Elusive': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'Power': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'All-Purpose': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        },
        'FB': {
            'Blocking': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'Rushing': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        },
        'WR': {
            'Possession': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'Deep Threat': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'Route Runner': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        },
        'TE': {
            'Blocking': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'Receiving': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'Hybrid': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        },
        'LT': {
            'Pass Protector': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'Run Blocker': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        },
        'LG': {
            'Pass Protector': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'Run Blocker': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        },
        'C': {
            'Pass Protector': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'Run Blocker': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        },
        'RG': {
            'Pass Protector': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'Run Blocker': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        },
        'RT': {
            'Pass Protector': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'Run Blocker': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        },
        'DE': {
            'Pass Rusher': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'Run Stuffer': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        },
        'DT': {
            'Pass Rusher': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'Run Stuffer': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        },
        'OLB': {
            'Coverage': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'Run Stuffer': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        },
        'MLB': {
            'Coverage': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'Run Stuffer': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        },
        'CB': {
            'Ball Hawk': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'Shutdown': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        },
        'FS': {
            'Ball Hawk': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'Shutdown': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        },
        'SS': {
            'Ball Hawk': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'Run Stuffer': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        },
        'K': {
            'Accurate': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'Power': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        },
        'P': {
            'Coffin Corner': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'Power': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        }
    }

    player_list = []
    player_names = read_player_names_from_csv()

    # Generate 53 players per team
    for p in range(0, 53):
        player = {}

        # Random player names from csv
        player['first_name'] = player_names[p][0]
        player['last_name'] = player_names[p][1]

        # Only assign player a position that isn't filled on the roster
        for pos, dist in position_dist.items():
            if dist[0] < dist[1]:
                player['position'] = pos
                # Pick a random prototype based on position
                player['prototype'] = random.choice(list(attr_dist[pos]))
                dist[0] += 1
                break
            else:
                continue

        # Assign random age and experience
        player['age'] = int(random.gauss(1, 0.1) * random.randint(25, 35)) # Normal distribution of ages
        player['experience'] = player['age'] - 22 # Experience assuming player entered league at age 22
        if player['experience'] < 0:
            player['experience'] = 0

        # Generate attributes based on weights and normal distribution
        base_rating = int(random.gauss(70, 20))
        weights = attr_dist[player['position']][player['prototype']]
        after_weights = []
        for i in range(len(weights)):
            after_weights.append(weights[i] + base_rating)
        sigmas = [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20]
        final_ratings = list(map(random.gauss, after_weights, sigmas))

        # Assign attributes to player dict
        i = 0
        calc_overall = []
        for attribute in ('potential', 'confidence', 'iq', 'speed', 'strength', 'agility', 'awareness', 'stamina',
                    'injury', 'run_off', 'pass_off', 'special_off', 'run_def', 'pass_def', 'special_def'):
            rating = int(final_ratings[i])
            if rating > 99:
                rating = 99
            elif rating < 0:
                rating = 0
            player[attribute] = rating
            calc_overall.append(rating)
            i += 1

        # Calculate overall rating and add player to list
        player['overall_rating'] = int(sum(calc_overall) / len(calc_overall))
        player_list.append(player)

    return player_list
    