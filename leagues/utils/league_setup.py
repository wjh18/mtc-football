import os
import random
import csv
import datetime


def read_player_names_from_csv():
    """
    Read names of retired NFL players from CSV, shuffle them randomly.
    Store in dict with first names as keys, last names as values.
    """
    with open(os.path.join(os.path.dirname(__file__), '../data/retired-players.csv'), 'r') as player_name_file:
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
    with open(os.path.join(os.path.dirname(__file__), '../data/nfl-teams.csv'), 'r') as team_data_file:
        team_reader = csv.reader(team_data_file, delimiter=',')
        team_info = {row[3]: [row[1], row[2], row[4], f'{row[4]} ' + f'{row[5]}'] for row in team_reader if row[1] != 'Name'}     
    return team_info

def generate_player_attributes():
    """
    Return a list of 53 dictionaries containing player attributes
    that map to Player model fields.
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
    
def get_conference_data():
    conferences = [
        {'name': 'AFC'},
        {'name': 'NFC'}
    ]
    return conferences

def get_division_data():
    divisions = [
        {'name': 'AFC East'},
        {'name': 'AFC North'},
        {'name': 'AFC South'},
        {'name': 'AFC West'},
        {'name': 'NFC East'},
        {'name': 'NFC North'},
        {'name': 'NFC South'},
        {'name': 'NFC West'},
    ]
    return divisions

def create_league_structure(league):
    """
    Creates a league's structure and teams
    - called during initial save of new League instance in models.py.
    """
    from ..models import Conference, Division, Season, Team
    # Get conference and division data and create them
    conferences = get_conference_data()
    divisions = get_division_data()
    Conference.objects.bulk_create(
        [Conference(league=league, **c) for c in conferences])
    afc = Conference.objects.get(name='AFC', league=league)
    nfc = Conference.objects.get(name='NFC', league=league)
    for division in divisions:
        division_name = division['name']
        if division_name[:3] == 'AFC':
            Division.objects.create(conference=afc, **division)
        elif division_name[:3] == 'NFC':
            Division.objects.create(conference=nfc, **division)
    # Read team data from CSV and create 32 teams in League
    team_info = read_team_info_from_csv()
    abbreviations = [*team_info.keys()]
    other_team_info = [*team_info.values()]
    for team in range(0, 32):
        team_conference = Conference.objects.get(
            name=other_team_info[team][2], league=league
        )
        team_division = Division.objects.get(
            name=other_team_info[team][3], conference=team_conference
        )
        Team.objects.create(
            location=other_team_info[team][0],
            name=other_team_info[team][1],
            abbreviation=abbreviations[team],
            division=team_division,
            league=league)
    # Create first season in league automatically
    Season.objects.create(
        league=league
    )
    
def create_team_players(team):
    """
    Creates players and generates their starting attributes on a per-team basis
    - called during initial save of new Team instance in models.py.
    """
    from ..models import Player
    # Read player names from CSV, generate attributes and create players
    player_attributes = generate_player_attributes()
    for player in player_attributes:
        p = Player.objects.create(
            league=team.league,
            **player
        )
        # Creates a contract b/w team and player instance
        p.team.add(team)
        
def create_season_details(season):
    """
    Generates a season's schedule, matchups, scoreboards and initial rankings
    - called during initial save of new Team instance in models.py.
    """
    from .schedule import create_schedule
    from ..models import Matchup, TeamStanding, TeamRanking
    from simulation.models import Scoreboard
    league_uuid = season.league.pk
    matchups = create_schedule(str(league_uuid))
    date = datetime.date(2021, 8, 29)
    progress_week = datetime.timedelta(days=7)
    for week_num in range(1, len(matchups) + 1):
        for matchup in matchups[week_num - 1]:
            new_matchup = Matchup.objects.create(
                home_team=matchup[0],
                away_team=matchup[1],
                season=season,
                week_number=week_num,
                date=date
            )
            Scoreboard.objects.create(
                matchup=new_matchup
            )
        date += progress_week

    for team in season.league.teams.all():
        standing = TeamStanding.objects.create(team=team, season=season)
        TeamRanking.objects.create(standing=standing)