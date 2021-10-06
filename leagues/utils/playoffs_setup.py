from django.apps import apps
from django.utils.text import slugify


def get_playoff_teams_by_conf(season):
    """
    Return conference standings ordered by conf rank.
    Limited to playoff teams only (top 7 from each conf).
    """
    TeamStanding = apps.get_model('leagues.TeamStanding')
    league_standings = TeamStanding.objects.filter(season=season, week_number=19)
    conferences = season.league.conferences.all()

    both_conf_standings = []
    for conference in conferences:
        conf_standings = league_standings.filter(
            team__division__conference=conference,
            ranking__conference_ranking__lte=7).order_by(
                'ranking__conference_ranking')
        both_conf_standings.append(conf_standings)

    return both_conf_standings


def generate_wildcard_matchups(season, conf_standings):
    """
    Create wildcard matchups for first week of playoffs.
    Rank 1 in each conference gets a bye. Matchups by rank:
    (2 @ 7) (3 @ 6) (4 @ 5)
    """
    Matchup = apps.get_model('leagues.Matchup')
    Scoreboard = apps.get_model('simulation.Scoreboard')

    for cs in conf_standings:

        # Set wildcard matchup constants based on conf ranks
        MATCHUPS = [
            (cs[1], cs[6]),
            (cs[2], cs[5]),
            (cs[3], cs[4])
        ]

        # Bulk create wildcard Matchups
        wildcard_matchups = Matchup.objects.bulk_create([
            Matchup(
                home_team=matchup[0].team,
                away_team=matchup[1].team,
                season=season,
                week_number=season.week_number,
                date=season.current_date,
                is_postseason=True,
                slug=slugify(
                    f'{matchup[0].team.abbreviation}-{matchup[1].team.abbreviation} \
                    -season-{season.season_number}-wildcard'
                )
            ) for matchup in MATCHUPS
        ])

        # Bulk create Scoreboards for wildcard Matchups
        Scoreboard.objects.bulk_create([
            Scoreboard(matchup=matchup) for matchup in wildcard_matchups])


def setup_playoffs(season):
    conf_standings = get_playoff_teams_by_conf(season)
    generate_wildcard_matchups(season, conf_standings)
