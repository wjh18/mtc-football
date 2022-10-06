from django.apps import apps

from apps.teams.setup import read_team_info_from_csv


def get_conference_data():
    """Get league conference names"""
    conferences = [{"name": "American"}, {"name": "National"}]

    return conferences


def get_division_data():
    """Get league division names"""
    divisions = [
        {"name": "American East"},
        {"name": "American North"},
        {"name": "American South"},
        {"name": "American West"},
        {"name": "National East"},
        {"name": "National North"},
        {"name": "National South"},
        {"name": "National West"},
    ]

    return divisions


def create_league_structure(league):
    """
    Creates a league's structure and teams.
    Called during initial save of new League instance in models.py.
    """
    Team = apps.get_model("teams.Team")
    Season = apps.get_model("seasons.Season")
    Conference = apps.get_model("leagues.Conference")
    Division = apps.get_model("leagues.Division")

    # Get conference and division data
    conferences = get_conference_data()
    divisions = get_division_data()

    # Create conferences and divisions
    conference_objs = Conference.objects.bulk_create(
        [Conference(league=league, **c) for c in conferences]
    )
    conf1, conf2 = conference_objs[0], conference_objs[1]

    for division in divisions:
        division_conf = division["name"].split(" ")[0]
        if division_conf == conf1.name:
            Division.objects.create(conference=conf1, **division)
        elif division_conf == conf2.name:
            Division.objects.create(conference=conf2, **division)

    # Read team information from CSV
    team_info = read_team_info_from_csv()
    abbreviations = [*team_info.keys()]
    team_info = [*team_info.values()]

    # Create 32 teams for this league
    for team in range(0, 32):
        team_conference = Conference.objects.get(name=team_info[team][2], league=league)
        team_division = Division.objects.get(
            name=team_info[team][3], conference=team_conference
        )
        Team.objects.create(
            location=team_info[team][0],
            name=team_info[team][1],
            abbreviation=abbreviations[team],
            division=team_division,
            conference=team_conference,
            league=league,
        )

    # Create first season in league
    Season.objects.create(league=league)
