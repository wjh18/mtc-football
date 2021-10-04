import os
import random
import csv
import datetime


def read_team_info_from_csv():
    """
    Read locations, names, and abbr of teams from CSV.
    Return a dict w/ locations as keys, list of names & abbrs as values.
    """
    with open(os.path.join(
        os.path.dirname(__file__), '../data/nfl-teams.csv'
    ), 'r') as team_data_file:

        team_reader = csv.reader(team_data_file, delimiter=',')

        team_info = {}
        for row in team_reader:
            if row[1] != 'Name':
                loc, name, abbr, conf, div = row[1:6]
                team_info[abbr] = [loc, name, conf, f'{conf} {div}']

    return team_info


def get_conference_data():
    """Set league conference names"""
    conferences = [
        {'name': 'AFC'},
        {'name': 'NFC'}
    ]

    return conferences


def get_division_data():
    """Set league division names"""
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


def create_season_details(season):
    """
    Generates a season's schedule, matchups, scoreboards and initial rankings
    - called during initial save of new Team instance in models.py.
    """
    from .schedule import create_schedule
    from ..models import Matchup, TeamStanding, TeamRanking
    from simulation.models import Scoreboard
    league_id = season.league.pk
    matchups = create_schedule(str(league_id))
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
