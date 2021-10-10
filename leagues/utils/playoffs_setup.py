from django.apps import apps
from django.utils.text import slugify
from django.db.models import Q


def update_playoff_clinches(season):
    """
    Update playoff clinches based on div and conf ranking.
    """
    TeamRanking = apps.get_model('leagues.TeamRanking')
    league_rankings = TeamRanking.objects.filter(
        standing__season=season, standing__week_number=19
    )
    
    for ranking in league_rankings:
        if ranking.conference_ranking == 1:
            ranking.clinch_bye = True
            ranking.clinch_div = True
            ranking.clinch_berth = True
        elif ranking.division_ranking == 1:
            ranking.clinch_div = True
            ranking.clinch_berth = True
        elif ranking.conference_ranking <= 7:
            ranking.clinch_berth = True
        else:
            ranking.clinch_none = True
        
        ranking.save()
  
        
def update_playoff_rankings(season, round_type, winner):
    """
    Update week 19 rankings with playoff berth and win data.
    """
    TeamRanking = apps.get_model('leagues.TeamRanking')
    
    # Duplicate week 19 TeamRanking instance and assign winner    
    ranking = TeamRanking.objects.get(
        standing__team=winner, standing__season=season,
        standing__week_number=19)
    
    if round_type == 'wildcard':    
        ranking.won_wild = True
    elif round_type == 'divisional':
        ranking.won_div = True
    elif round_type == 'conference':
        ranking.won_conf = True
    else:
        ranking.won_champ = True
        
    ranking.save()


def get_playoff_teams_by_conf(season):
    """
    Return conference standings ordered by conf rank.
    Limited to playoff teams only (top 7 from each conf).
    """
    TeamRanking = apps.get_model('leagues.TeamRanking')
    league_rankings = TeamRanking.objects.filter(
        standing__season=season, standing__week_number=19
    )
    conferences = season.league.conferences.all()

    both_conf_rankings = []
    for conference in conferences:
        conf_rankings = league_rankings.filter(
            standing__team__division__conference=conference,
            clinch_berth=True).order_by(
                'conference_ranking')
        both_conf_rankings.append(conf_rankings)

    return both_conf_rankings


### Wildcard round matchups and sim

def generate_wildcard_matchups(season, conf_rankings):
    """
    Create wildcard matchups for first week of playoffs.
    Rank 1 in each conference gets a bye. Matchups by rank:
    (2 @ 7) (3 @ 6) (4 @ 5)
    """
    Matchup = apps.get_model('leagues.Matchup')
    Scoreboard = apps.get_model('simulation.Scoreboard')

    for cr in conf_rankings:

        # Set wildcard matchup constants based on conf ranks
        MATCHUPS = [
            (cr[1], cr[6]),
            (cr[2], cr[5]),
            (cr[3], cr[4])
        ]

        # Bulk create wildcard Matchups
        wildcard_matchups = Matchup.objects.bulk_create([
            Matchup(
                home_team=matchup[0].standing.team,
                away_team=matchup[1].standing.team,
                season=season,
                week_number=season.week_number + 1,
                date=season.current_date,
                is_postseason=True,
                slug=slugify(
                    f'{matchup[1].standing.team.abbreviation}-\
                      {matchup[0].standing.team.abbreviation}-\
                      season-{season.season_number}-\
                      {matchup[0].standing.team.division.conference}-wildcard'
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
    round_type = 'wildcard'
        
    # Get winner and update their ranking
    matchups = Matchup.objects.filter(
        season=season, week_number=current_week)

    winners = []
    for matchup in matchups:
        matchup.scoreboard.get_score()
        winner = matchup.scoreboard.get_winner()
        winners.append(winner)
        
        update_playoff_rankings(season, round_type, winner)  

    return winners


### Divisional round matchups and sim

def generate_divisional_matchups(season, conf_rankings, wc_winners):
    """
    Create divisional matchups for second week of playoffs.
    Rank 1 in each conference and wildcard winners. Matchups by rank:
    (1 @ lowest_rank) (2nd_highest @ 3rd_highest)
    """
    Matchup = apps.get_model('leagues.Matchup')
    Scoreboard = apps.get_model('simulation.Scoreboard')

    for cr in conf_rankings:
        
        # Filter conf standings by teams who won wc round and rank 1 team
        cr = cr.filter(
            Q(standing__team__in=wc_winners) | Q(conference_ranking=1)
        )
        
        # Set divisional matchup constants based on conf ranks
        MATCHUPS = [
            (cr[0], cr[3]),
            (cr[1], cr[2])
        ]

        # Bulk create divisional Matchups
        divisional_matchups = Matchup.objects.bulk_create([
            Matchup(
                home_team=matchup[0].standing.team,
                away_team=matchup[1].standing.team,
                season=season,
                week_number=season.week_number + 1,
                date=season.current_date,
                is_postseason=True,
                slug=slugify(
                    f'{matchup[1].standing.team.abbreviation}-\
                      {matchup[0].standing.team.abbreviation}-\
                      season-{season.season_number}-\
                      {matchup[0].standing.team.division.conference}-divisional'
                )
            ) for matchup in MATCHUPS
        ])

        # Bulk create Scoreboards for divisional Matchups
        Scoreboard.objects.bulk_create([
            Scoreboard(matchup=matchup) for matchup in divisional_matchups])


def sim_divisional_matchups(season):
    """Sim divisional round matchups."""
    Matchup = apps.get_model('leagues.Matchup')
    current_week = season.week_number
    round_type = 'divisional'

    matchups = Matchup.objects.filter(
        season=season, week_number=current_week)

    winners = []
    for matchup in matchups:
        matchup.scoreboard.get_score()
        winner = matchup.scoreboard.get_winner()
        winners.append(winner)
        
        update_playoff_rankings(season, round_type, winner)         

    return winners


### Conference final matchups and sim

def generate_conference_matchups(season, conf_rankings, div_winners):
    """
    Create conference matchups for third week of playoffs.
    Divisional winners by conference ranks. Matchups by rank:
    (highest_rank @ lowest_rank) (2nd_highest @ 3rd_highest)
    """
    Matchup = apps.get_model('leagues.Matchup')
    Scoreboard = apps.get_model('simulation.Scoreboard')

    for cr in conf_rankings:
        
        # Filter conf standings by teams who won div
        cr = cr.filter(Q(standing__team__in=div_winners))
        
        # Set conference matchup constants based on conf ranks
        MATCHUPS = [
            (cr[0], cr[1])
        ]

        # Bulk create conference Matchups
        conference_matchups = Matchup.objects.bulk_create([
            Matchup(
                home_team=matchup[0].standing.team,
                away_team=matchup[1].standing.team,
                season=season,
                week_number=season.week_number + 1,
                date=season.current_date,
                is_postseason=True,
                slug=slugify(
                    f'{matchup[1].standing.team.abbreviation}-\
                      {matchup[0].standing.team.abbreviation}-\
                      season-{season.season_number}-\
                      {matchup[0].standing.team.division.conference}-conference-final'
                )
            ) for matchup in MATCHUPS
        ])

        # Bulk create Scoreboards for conference Matchups
        Scoreboard.objects.bulk_create([
            Scoreboard(matchup=matchup) for matchup in conference_matchups])


def sim_conference_matchups(season):
    """Sim conference round matchups."""
    Matchup = apps.get_model('leagues.Matchup')
    current_week = season.week_number
    round_type = 'conference'

    matchups = Matchup.objects.filter(
        season=season, week_number=current_week)

    winners = []
    for matchup in matchups:
        matchup.scoreboard.get_score()
        winner = matchup.scoreboard.get_winner()
        winners.append(winner)
        
        update_playoff_rankings(season, round_type, winner)

    return winners


### Championship matchups and sim

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
            f'{conf_winners[1].abbreviation}-\
                {conf_winners[0].abbreviation}-\
                season-{season.season_number}-championship'
        )
    )
    
    # Create Scoreboard for championship Matchup
    Scoreboard.objects.create(matchup=championship_matchup)


def sim_championship_matchup(season):
    """Sim championship matchup."""
    Matchup = apps.get_model('leagues.Matchup')
    current_week = season.week_number
    round_type = 'championship'

    matchup = Matchup.objects.get(
        season=season, week_number=current_week)
  
    matchup.scoreboard.get_score()
    winner = matchup.scoreboard.get_winner()
    
    update_playoff_rankings(season, round_type, winner)

    return winner


### Functions to set up each playoff round

def advance_to_wildcard_playoffs(season):
    update_playoff_clinches(season)
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