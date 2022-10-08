import copy
import csv
import os
import random

from django.utils.text import slugify

from apps.core.utils import random_string_generator as random_string

from ..models import Player
from .distributions import ATTR_DIST, POSITION_DIST


def read_player_names_from_csv():
    """
    Read names of retired NFL players from CSV, shuffle them randomly.
    Returns a dict with first names as keys, last names as values.
    """
    with open(
        os.path.join(os.path.dirname(__file__), "../data/retired-players.csv"), "r"
    ) as player_name_file:

        name_reader = csv.reader(player_name_file, delimiter=",")
        next(name_reader)  # Skip headings

        player_names = [
            [row[1], row[2]]
            for row in name_reader
            # Skip last names that are only middle initials (CSV format issue)
            if "." not in row[2]
        ]

        # Shuffle first and last names
        first_names = [names[0] for names in player_names]
        last_names = [names[1] for names in player_names]
        random.shuffle(first_names)
        random.shuffle(last_names)

        # Limit player names to 32 teams * 53 players = 1696 names
        player_names = list(zip(first_names, last_names))[:1696]

    return player_names


def generate_player_attributes(player_names):
    """
    Return a list of 53 dicts with player attributes
    that map to Player model fields.
    """

    position_dist = copy.deepcopy(POSITION_DIST)
    attr_dist = copy.deepcopy(ATTR_DIST)

    player_list = []

    # Generate 53 players per team
    num_players = 0
    while num_players < 53:
        player = {}

        # Set player names from parsed CSV data
        player_name = player_names.pop()
        player["first_name"], player["last_name"] = player_name[0], player_name[1]

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

        num_players += 1

    return player_list


def create_team_players(team, player_names):
    """
    Creates players and generates their starting attributes on a per-team basis
    - called during initial save of new Team instance in models.py.
    """

    # Read player names from CSV, generate attributes
    player_attributes = generate_player_attributes(player_names)

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
    Contract = Player.team.through
    Contract.objects.bulk_create(
        [Contract(team=team, player=player) for player in player_objs]
    )

    # Set initial team overall rating
    team.update_team_overall()
