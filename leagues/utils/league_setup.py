import os
import random
import csv
import datetime

from django.apps import apps
from django.utils.text import slugify

from .schedule import create_schedule


def read_team_info_from_csv():
    """
    Read locations, names, and abbr of teams from CSV.
    Return a dict w/ abbrs as keys and remaining data as values.
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
    """Get league conference names"""
    conferences = [
        {'name': 'AFC'},
        {'name': 'NFC'}
    ]

    return conferences


def get_division_data():
    """Get league division names"""
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
    Creates a league's structure and teams.
    Called during initial save of new League instance in models.py.
    """
    Conference = apps.get_model('leagues.Conference')
    Division = apps.get_model('leagues.Division')
    Team = apps.get_model('leagues.Team')
    Season = apps.get_model('leagues.Season')

    # Get conference and division data
    conferences = get_conference_data()
    divisions = get_division_data()

    # Create conferences and divisions
    conference_objs = Conference.objects.bulk_create(
        [Conference(league=league, **c) for c in conferences])
    conf1, conf2 = conference_objs[0], conference_objs[1]

    for division in divisions:
        division_name = division['name']
        if division_name[:3] == conf1.name:
            Division.objects.create(conference=conf1, **division)
        elif division_name[:3] == conf2.name:
            Division.objects.create(conference=conf2, **division)

    # Read team information from CSV
    team_info = read_team_info_from_csv()
    abbreviations = [*team_info.keys()]
    team_info = [*team_info.values()]

    # Create 32 teams for this league
    for team in range(0, 32):
        team_conference = Conference.objects.get(
            name=team_info[team][2], league=league)
        team_division = Division.objects.get(
            name=team_info[team][3], conference=team_conference)
        Team.objects.create(
            location=team_info[team][0],
            name=team_info[team][1],
            abbreviation=abbreviations[team],
            division=team_division,
            league=league)

    # Create first season in league
    Season.objects.create(league=league)


def create_season_details(season):
    """
    Generates a season's schedule, matchups, scoreboards and initial rankings.
    Called during initial save of new Team instance in models.py.
    """
    Matchup = apps.get_model('leagues.Matchup')
    TeamStanding = apps.get_model('leagues.TeamStanding')
    TeamRanking = apps.get_model('leagues.TeamRanking')
    Scoreboard = apps.get_model('simulation.Scoreboard')

    # Generate nested list of weeks and matchups
    league_id = season.league.pk
    matchups = create_schedule(str(league_id))

    # Set start date for week 1 and week value
    progress_week = datetime.timedelta(days=7)
    date = season.start_date - progress_week

    # # Create matchups based on schedule (non-bulk)
    # for week_num in range(1, len(matchups) + 1):
    #     for matchup in matchups[week_num - 1]:
    #         new_matchup = Matchup.objects.create(
    #             home_team=matchup[0],
    #             away_team=matchup[1],
    #             season=season,
    #             week_number=week_num,
    #             date=date
    #         )
    #         Scoreboard.objects.create(
    #             matchup=new_matchup
    #         )
    #     date += progress_week

    # Bulk create Matchups based on schedule
    matchup_objs = Matchup.objects.bulk_create([
        Matchup(
            home_team=matchup[0],
            away_team=matchup[1],
            season=season,
            week_number=week_num,
            date=(date+progress_week),
            slug=slugify(
                f'{matchup[0].abbreviation}-{matchup[1].abbreviation} \
                -season-{season.season_number}-week-{week_num}'
            )
        ) for week_num in range(1, len(matchups) + 1) \
          for matchup in matchups[week_num - 1]
    ])

    # Bulk create Scoreboards for new Matchups
    Scoreboard.objects.bulk_create([
        Scoreboard(matchup=matchup) for matchup in matchup_objs])

    # Create starting Standings and Rankings for each team
    for team in season.league.teams.all():
        standing = TeamStanding.objects.create(team=team, season=season)
        TeamRanking.objects.create(standing=standing)
