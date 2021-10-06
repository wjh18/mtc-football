from django.apps import apps
from django.utils.text import slugify
from django.db.models import Q

def get_playoff_teams_by_conf(season):
    """
    Return conference standings ordered by conf rank.
    Limited to playoff teams only (top 7 from each conf).
    """
    TeamStanding = apps.get_model('leagues.TeamStanding')
    league_standings = TeamStanding.objects.filter(
        season=season, week_number=19)
    conferences = season.league.conferences.all()

    both_conf_standings = []
    for conference in conferences:
        conf_standings = league_standings.filter(
            team__division__conference=conference,
            ranking__conference_ranking__lte=7).order_by(
                'ranking__conference_ranking')
        both_conf_standings.append(conf_standings)

    return both_conf_standings


### Wildcard round matchups and sim

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
                week_number=season.week_number + 1,
                date=season.current_date,
                is_postseason=True,
                slug=slugify(
                    f'{matchup[0].team.abbreviation}-\
                      {matchup[1].team.abbreviation}-\
                      season-{season.season_number}-\
                      {matchup[0].team.division.conference}-wildcard'
                )
            ) for matchup in MATCHUPS
        ])

        # Bulk create Scoreboards for wildcard Matchups
        Scoreboard.objects.bulk_create([
            Scoreboard(matchup=matchup) for matchup in wildcard_matchups])


def sim_wildcard_matchups(season):
    """Sim wildcard round matchups."""
    Matchup = apps.get_model('leagues.Matchup')
    current_week = season.week_number

    matchups = Matchup.objects.filter(
        season=season, week_number=current_week)

    winners = []
    for matchup in matchups:
        matchup.scoreboard.get_score()
        winner = matchup.scoreboard.get_winner()
        winners.append(winner)

    return winners


### Divisional round matchups and sim

def generate_divisional_matchups(season, conf_standings, wc_winners):
    """
    Create divisional matchups for second week of playoffs.
    Rank 1 in each conference and wildcard winners. Matchups by rank:
    (1 @ lowest_rank) (2nd_highest @ 3rd_highest)
    """
    Matchup = apps.get_model('leagues.Matchup')
    Scoreboard = apps.get_model('simulation.Scoreboard')

    for cs in conf_standings:
        
        # Filter conf standings by teams who won wc round and rank 1 team
        cs = cs.filter(
            Q(team__in=wc_winners) | Q(ranking__conference_ranking=1)
        )
        
        # Set wildcard matchup constants based on conf ranks
        MATCHUPS = [
            (cs[0], cs[3]),
            (cs[1], cs[2])
        ]

        # Bulk create wildcard Matchups
        divisional_matchups = Matchup.objects.bulk_create([
            Matchup(
                home_team=matchup[0].team,
                away_team=matchup[1].team,
                season=season,
                week_number=season.week_number + 1,
                date=season.current_date,
                is_postseason=True,
                slug=slugify(
                    f'{matchup[0].team.abbreviation}-\
                      {matchup[1].team.abbreviation}-\
                      season-{season.season_number}-\
                      {matchup[0].team.division.conference}-divisional'
                )
            ) for matchup in MATCHUPS
        ])

        # Bulk create Scoreboards for wildcard Matchups
        Scoreboard.objects.bulk_create([
            Scoreboard(matchup=matchup) for matchup in divisional_matchups])


def sim_divisional_matchups(season):
    """Sim divisional round matchups."""
    Matchup = apps.get_model('leagues.Matchup')
    current_week = season.week_number

    matchups = Matchup.objects.filter(
        season=season, week_number=current_week)

    winners = []
    for matchup in matchups:
        matchup.scoreboard.get_score()
        winner = matchup.scoreboard.get_winner()
        winners.append(winner)

    return winners


### Conference final matchups and sim

def generate_conference_matchups(season, conf_standings, div_winners):
    """
    Create conference matchups for third week of playoffs.
    Divisional winners by conference ranks. Matchups by rank:
    (highest_rank @ lowest_rank) (2nd_highest @ 3rd_highest)
    """
    Matchup = apps.get_model('leagues.Matchup')
    Scoreboard = apps.get_model('simulation.Scoreboard')

    for cs in conf_standings:
        
        # Filter conf standings by teams who won div
        cs = cs.filter(Q(team__in=div_winners))
        
        # Set wildcard matchup constants based on conf ranks
        MATCHUPS = [
            (cs[0], cs[1])
        ]

        # Bulk create wildcard Matchups
        conference_matchups = Matchup.objects.bulk_create([
            Matchup(
                home_team=matchup[0].team,
                away_team=matchup[1].team,
                season=season,
                week_number=season.week_number + 1,
                date=season.current_date,
                is_postseason=True,
                slug=slugify(
                    f'{matchup[0].team.abbreviation}-\
                      {matchup[1].team.abbreviation}-\
                      season-{season.season_number}-\
                      {matchup[0].team.division.conference}-conference-final'
                )
            ) for matchup in MATCHUPS
        ])

        # Bulk create Scoreboards for wildcard Matchups
        Scoreboard.objects.bulk_create([
            Scoreboard(matchup=matchup) for matchup in conference_matchups])


def sim_conference_matchups(season):
    """Sim conference round matchups."""
    Matchup = apps.get_model('leagues.Matchup')
    current_week = season.week_number

    matchups = Matchup.objects.filter(
        season=season, week_number=current_week)

    winners = []
    for matchup in matchups:
        matchup.scoreboard.get_score()
        winner = matchup.scoreboard.get_winner()
        winners.append(winner)

    return winners


### Conference final matchups and sim

def generate_championship_matchup(season, conf_winners):
    """
    Create championship matchup for final (4) week of playoffs.
    (highest_rank @ lowest_rank)
    """
    Matchup = apps.get_model('leagues.Matchup')
    Scoreboard = apps.get_model('simulation.Scoreboard')
    
    championship_matchup = Matchup.objects.create(
        home_team=conf_winners[0],
        away_team=conf_winners[1],
        season=season,
        week_number=season.week_number + 1,
        date=season.current_date,
        is_postseason=True,
        slug=slugify(
            f'{conf_winners[0].abbreviation}-\
                {conf_winners[1].abbreviation}-\
                season-{season.season_number}-championship'
        )
    )
    
    # Bulk create Scoreboards for wildcard Matchups
    Scoreboard.objects.create(matchup=championship_matchup)


def sim_championship_matchup(season):
    """Sim championship matchup."""
    Matchup = apps.get_model('leagues.Matchup')
    current_week = season.week_number

    matchup = Matchup.objects.get(
        season=season, week_number=current_week)
  
    matchup.scoreboard.get_score()
    winner = matchup.scoreboard.get_winner()

    return winner


### Functions to set up each playoff round

def advance_to_wildcard_playoffs(season):
    conf_standings = get_playoff_teams_by_conf(season)
    generate_wildcard_matchups(season, conf_standings)


def advance_to_divisional_playoffs(season):
    conf_standings = get_playoff_teams_by_conf(season)
    wc_winners = sim_wildcard_matchups(season)
    generate_divisional_matchups(season, conf_standings, wc_winners)
    

def advance_to_conference_playoffs(season):
    conf_standings = get_playoff_teams_by_conf(season)
    div_winners = sim_divisional_matchups(season)
    generate_conference_matchups(season, conf_standings, div_winners)
    

def advance_to_championship(season):
    conf_winners = sim_conference_matchups(season)
    generate_championship_matchup(season, conf_winners)