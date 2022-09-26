import csv
import os
import random

from django.apps import apps
from django.utils.text import slugify

from .text import random_string_generator as random_string


def read_player_names_from_csv():
    """
    Read names of retired NFL players from CSV, shuffle them randomly.
    Returns a dict with first names as keys, last names as values.
    """
    with open(
        os.path.join(os.path.dirname(__file__), "../data/retired-players.csv"), "r"
    ) as player_name_file:

        name_reader = csv.reader(player_name_file, delimiter=",")
        player_names = [
            [row[1], row[2]]
            for row in name_reader
            if ("last_name" or ".") not in row[2]
        ]

        # Shuffle first and last names
        first_names = [names[0] for names in player_names]
        last_names = [names[1] for names in player_names]
        random.shuffle(first_names)
        random.shuffle(last_names)

        player_names = list(zip(first_names, last_names))

    return player_names


def get_position_distribution():
    """
    Positional constraints per 53 man roster
    position_dist[posX][0] represents how many of posX are filled
    position_dist[posX][1] means generate Y posX's for the starting roster
    """
    position_dist = {
        "QB": [0, 3],
        "HB": [0, 3],
        "FB": [0, 1],
        "WR": [0, 6],
        "TE": [0, 3],
        "LT": [0, 2],
        "LG": [0, 2],
        "C": [0, 2],
        "RG": [0, 2],
        "RT": [0, 2],
        "DE": [0, 4],
        "DT": [0, 4],
        "OLB": [0, 4],
        "MLB": [0, 3],
        "CB": [0, 6],
        "FS": [0, 2],
        "SS": [0, 2],
        "K": [0, 1],
        "P": [0, 1],
    }

    return position_dist


def get_attribute_distribution():
    """
    Attribute weights based on position and prototype, in this order:
    [potential, confidence, iq, speed, strength, agility, awareness, stamina,
    injury, run_off, pass_off, special_off, run_def, pass_def, special_def]
    """
    attr_dist = {
        "QB": {
            "Gunslinger": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "Scrambler": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "Field General": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        },
        "HB": {
            "Elusive": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "Power": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "All-Purpose": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        },
        "FB": {
            "Blocking": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "Rushing": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        },
        "WR": {
            "Possession": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "Deep Threat": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "Route Runner": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        },
        "TE": {
            "Blocking": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "Receiving": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "Hybrid": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        },
        "LT": {
            "Pass Protector": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "Run Blocker": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        },
        "LG": {
            "Pass Protector": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "Run Blocker": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        },
        "C": {
            "Pass Protector": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "Run Blocker": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        },
        "RG": {
            "Pass Protector": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "Run Blocker": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        },
        "RT": {
            "Pass Protector": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "Run Blocker": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        },
        "DE": {
            "Pass Rusher": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "Run Stuffer": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        },
        "DT": {
            "Pass Rusher": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "Run Stuffer": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        },
        "OLB": {
            "Coverage": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "Run Stuffer": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        },
        "MLB": {
            "Coverage": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "Run Stuffer": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        },
        "CB": {
            "Ball Hawk": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "Shutdown": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        },
        "FS": {
            "Ball Hawk": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "Shutdown": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        },
        "SS": {
            "Ball Hawk": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "Run Stuffer": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        },
        "K": {
            "Accurate": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "Power": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        },
        "P": {
            "Coffin Corner": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "Power": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        },
    }

    return attr_dist


def generate_player_attributes():
    """
    Return a list of 53 dicts with player attributes
    that map to Player model fields.
    """

    # Get player position distribution
    position_dist = get_position_distribution()
    # Get player attribute distribution
    attr_dist = get_attribute_distribution()
    # Get player names from CSV
    player_names = read_player_names_from_csv()

    player_list = []

    # Generate 53 players per team
    for roster_spot in range(0, 53):
        player = {}

        # Set player names from parsed CSV data
        player["first_name"] = player_names[roster_spot][0]
        player["last_name"] = player_names[roster_spot][1]

        # Only assign player a position that isn't filled on the roster
        for pos, dist in position_dist.items():
            if dist[0] < dist[1]:
                player["position"] = pos
                # Pick a random prototype based on position
                player["prototype"] = random.choice(list(attr_dist[pos]))
                dist[0] += 1
                break
            else:
                continue

        # Assign player ages based on normal distribution
        player["age"] = int(random.gauss(1, 0.1) * random.randint(25, 35))
        default_rookie_age = 22
        player["experience"] = player["age"] - default_rookie_age
        if player["age"] < 22:
            player["experience"] = 0

        # Generate ratings based on weights and normal distribution
        base_rating = int(random.gauss(70, 20))
        position, prototype = player["position"], player["prototype"]
        pos_weights = attr_dist[position][prototype]
        # Apply position and prototype weights
        after_pos_weights = []
        for pw in range(len(pos_weights)):
            after_pos_weights.append(pos_weights[pw] + base_rating)
        # Sigmas for standard deviation
        sigmas = [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20]
        final_ratings = list(map(random.gauss, after_pos_weights, sigmas))

        i = 0
        calc_overall = []
        # Assign final ratings to player key
        for attribute in (
            "potential",
            "confidence",
            "iq",
            "speed",
            "strength",
            "agility",
            "awareness",
            "stamina",
            "injury",
            "run_off",
            "pass_off",
            "special_off",
            "run_def",
            "pass_def",
            "special_def",
        ):

            rating = int(final_ratings[i])
            if rating > 99:
                rating = 99
            elif rating < 0:
                rating = 0
            player[attribute] = rating

            calc_overall.append(rating)
            i += 1

        # Calculate overall rating and add player to list
        player["overall_rating"] = int(sum(calc_overall) / len(calc_overall))
        player_list.append(player)

    return player_list


def create_team_players(team):
    """
    Creates players and generates their starting attributes on a per-team basis
    - called during initial save of new Team instance in models.py.
    """
    Player = apps.get_model("leagues.Player")

    # Read player names from CSV, generate attributes
    player_attributes = generate_player_attributes()

    # Bulk create players
    player_objs = Player.objects.bulk_create(
        [
            Player(
                league=team.league,
                slug=slugify(
                    f'{player["first_name"]}-{player["last_name"]}\
                -{random_string()}'
                ),
                **player,
            )
            for player in player_attributes
        ]
    )

    # Bulk create ManyToMany Player -> Teams through Contract
    ThroughModel = Player.team.through
    ThroughModel.objects.bulk_create(
        [ThroughModel(team=team, player=player) for player in player_objs]
    )

    # Set initial team overall rating
    team.update_team_overall()
