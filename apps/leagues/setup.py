from django.apps import apps

from apps.teams.setup import read_team_info_from_csv

CONFERENCE_NAMES = ["American", "National"]

DIVISION_NAMES = [
    "American East",
    "American North",
    "American South",
    "American West",
    "National East",
    "National North",
    "National South",
    "National West",
]


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
    conferences = CONFERENCE_NAMES
    divisions = DIVISION_NAMES

    # Create conferences and divisions
    conference_objs = Conference.objects.bulk_create(
        [Conference(league=league, name=name) for name in conferences]
    )
    conf1, conf2 = conference_objs[0], conference_objs[1]

    for division in divisions:
        division_conf = division.split(" ")[0]
        if division_conf == conf1.name:
            conf = conf1
        elif division_conf == conf2.name:
            conf = conf2
        Division.objects.create(conference=conf, name=division)

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
