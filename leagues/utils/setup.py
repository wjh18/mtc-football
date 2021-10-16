import os
import csv
import datetime

from django.apps import apps
from django.utils.text import slugify
from django.db.models import F, When, Case
from django.db.models.fields import BooleanField

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

    # Bulk create Matchups based on schedule
    matchup_objs = Matchup.objects.bulk_create([
        Matchup(
            home_team=matchup[0],
            away_team=matchup[1],
            season=season,
            week_number=week_num,
            date=season.start_date+(week_num*datetime.timedelta(days=7)),
            slug=slugify(
                f'{matchup[1].abbreviation}-{matchup[0].abbreviation} \
                -week-{week_num}-season-{season.season_number}'
            ),
            is_conference=Case(
                    When(
                        home_team__division__conference=F('away_team__division__conference'),
                        then=True
                    ),
                    default=False,
                    output_field=BooleanField()
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
