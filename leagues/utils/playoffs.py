from django.apps import apps
from django.utils.text import slugify
from django.db.models import Q


def update_final_playoff_clinches(season):
    """
    Update final playoff clinches based on div and conf ranking
    at the end of the season.
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
        

def update_div_and_conf_clinches(standings, div=False, conf=False):
    """
    Update div and conf clinches mid-season based on
    how many games back the second ranking team is.
    """
    if div:
        lead_ranking = Q(ranking__division_ranking=1)
        clinch_false = Q(ranking__clinch_div=False)
        next_ranking = Q(ranking__division_ranking=2)       
    elif conf:
        lead_ranking = Q(ranking__conference_ranking=1)
        clinch_false = Q(ranking__clinch_bye=False)
        next_ranking = Q(ranking__conference_ranking=2)
    
    # Div or conf rank 1's who haven't clinched div or conf yet
    lead_standings = standings.filter(lead_ranking, clinch_false)
    
    for rank_1 in lead_standings:
        
        if div:
            match_entity = Q(
                team__division=rank_1.team.division)
        elif conf:
            match_entity = Q(
                team__division__conference=rank_1.team.division.conference)
        
        # Div rank 2's in same div as div rank 1's
        rank_2 = standings.get(next_ranking, match_entity)
        
        rank_1_wins = rank_1.wins + 0.5*rank_1.ties
         
        rank_2_gp = rank_2.wins + rank_2.losses + rank_2.ties
        rank_2_gl = 17 - rank_2_gp
        rank_2_wins = rank_2.wins + 0.5*rank_2.ties
        rank_2_gb = rank_1_wins - rank_2_wins

        # Rank 1 clinches div (rank 2 is too many games behind)        
        if rank_2_gb > rank_2_gl:
            if div:
                rank_1.ranking.clinch_div = True
                rank_1.ranking.clinch_berth = True
            elif conf:
                rank_1.ranking.clinch_bye = True 
                rank_1.ranking.clinch_berth = True
            
            rank_1.ranking.save()
            

def update_berths_and_eliminations(standings):
    """
    Update playoff berths and eliminations mid-season based on
    how many games back the eighth ranking and below teams are.
    """
    # Top and bottom standings who haven't clinched a berth or aren't out yet
    top_7_standings = standings.filter(
        ranking__conference_ranking__lte=7, ranking__clinch_berth=False)
    
    bottom_8_standings = standings.filter(
            ranking__conference_ranking__gte=8, ranking__clinch_none=False)
    
    for top_7 in top_7_standings:
        
        rank_8 = standings.get(
            ranking__conference_ranking=8,
            team__division__conference=top_7.team.division.conference)
        
        top_7_wins = top_7.wins + 0.5*top_7.ties
        
        rank_8_gp = rank_8.wins + rank_8.losses + rank_8.ties
        rank_8_gl = 17 - rank_8_gp
        rank_8_wins = rank_8.wins + 0.5*rank_8.ties
        rank_8_gb = top_7_wins - rank_8_wins

        # Rank 1 clinches div (rank 2 is too many games behind)        
        if rank_8_gb > rank_8_gl:
            top_7.ranking.clinch_berth = True
            top_7.ranking.save()
    
    for bottom_8 in bottom_8_standings:
        
        rank_7 = standings.get(
            ranking__conference_ranking=7,
            team__division__conference=bottom_8.team.division.conference)
        
        rank_7_wins = rank_7.wins + 0.5*rank_7.ties
        
        bottom_8_gp = bottom_8.wins + bottom_8.losses + bottom_8.ties
        bottom_8_gl = 17 - bottom_8_gp
        bottom_8_wins = bottom_8.wins + 0.5*bottom_8.ties
        bottom_8_gb = rank_7_wins - bottom_8_wins

        # Rank 1 clinches div (rank 2 is too many games behind)        
        if bottom_8_gb > bottom_8_gl:
            bottom_8.ranking.clinch_none = True
            bottom_8.ranking.save()
            
            
def update_running_playoff_clinches(season):
    """
    Helper function to update the clinches and playoff
    births for each clinch type in week 8 or later.
    """
    # Only check in week 8 or later
    # (No team can clinch or be eliminated with 8 or less games)
    if season.week_number >= 8:
        TeamStanding = apps.get_model('leagues.TeamStanding')
        standings = TeamStanding.objects.filter(
            season=season, week_number=season.week_number + 1)
        
        update_div_and_conf_clinches(standings, div=True)
        update_div_and_conf_clinches(standings, conf=True)
        update_berths_and_eliminations(standings)        
  
        
def update_playoff_rankings(season, round_type, winner):
    """
    Update week 19 rankings with playoff berth and win data.
    """
    TeamRanking = apps.get_model('leagues.TeamRanking')
    
    # Get week 19 TeamRanking instance and assign winner    
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
            clinch_berth=True
        ).order_by('conference_ranking')
        
        both_conf_rankings.append(conf_rankings)

    return both_conf_rankings


def generate_round_matchups(season, round_type=False,
                            conf_rankings=False, winners=False):
    """Generate playoff matchups for the upcoming round"""
    
    Matchup = apps.get_model('leagues.Matchup')
    Scoreboard = apps.get_model('simulation.Scoreboard')
    
    if round_type == 'conference':
        # Generate championship matchup
        champ_matchup = Matchup.objects.create(
            home_team=winners[0],
            away_team=winners[1],
            season=season,
            week_number=season.week_number + 1,
            date=season.current_date,
            is_postseason=True,
            slug=slugify(
                f'{winners[1].abbreviation}-\
                    {winners[0].abbreviation}-\
                    championship-season-{season.season_number}'
            )
        )
        
        # Create Scoreboard for championship Matchup
        Scoreboard.objects.create(matchup=champ_matchup)     
        # Return function to prevent other matchups from being created
        return
    
    for cr in conf_rankings:
        
        if not round_type:
            next_round = 'wildcard'
            
            # Set wildcard matchups for first week of playoffs.
            # Rank 1 in each conference gets a bye. Matchups by rank:
            # (2 @ 7) (3 @ 6) (4 @ 5)            
            MATCHUPS = [
                (cr[1], cr[6]),
                (cr[2], cr[5]),
                (cr[3], cr[4])
            ]
            
        elif round_type == 'wildcard':
            # Filter conf standings by teams who won wc round and rank 1 team
            cr = cr.filter(
                Q(standing__team__in=winners) | Q(conference_ranking=1)
            )
            next_round = 'divisional'
            
            # Set divisional matchups for second week of playoffs.
            # Rank 1 in each conference and wildcard winners. Matchups by rank:
            # (1 @ lowest_rank) (2nd_highest @ 3rd_highest)            
            MATCHUPS = [
                (cr[0], cr[3]),
                (cr[1], cr[2])
            ]
            
        elif round_type == 'divisional':
            # Filter conf standings by teams who won div
            cr = cr.filter(Q(standing__team__in=winners))
            next_round = 'conference'
            
            # Set conference matchups for third week of playoffs.
            # Divisional winners by conference ranks. Matchups by rank:
            # (highest_rank @ lowest_rank) (2nd_highest @ 3rd_highest)
            MATCHUPS = [
                (cr[0], cr[1])
            ]
        
        # Bulk create Matchups
        create_matchups = Matchup.objects.bulk_create([
            Matchup(
                home_team=matchup[0].standing.team,
                away_team=matchup[1].standing.team,
                season=season,
                week_number=season.week_number + 1,
                date=season.current_date,
                is_postseason=True,
                is_conference=True,
                slug=slugify(
                    f'{matchup[1].standing.team.abbreviation}-\
                      {matchup[0].standing.team.abbreviation}-\
                      {matchup[0].standing.team.division.conference.name}-{next_round}-\
                      season-{season.season_number}'
                )
            ) for matchup in MATCHUPS
        ])
        
        # Update whether matchup is divisional
        for matchup in create_matchups:
            if matchup.home_team.division == matchup.away_team.division:
                matchup.is_divisional = True
        Matchup.objects.bulk_update(create_matchups, ['is_divisional'])

        # Bulk create Scoreboards for Matchups
        Scoreboard.objects.bulk_create([
            Scoreboard(matchup=matchup) for matchup in create_matchups])


def sim_round_matchups(season, round_type):
    """Sim round matchups based on round type."""
    Matchup = apps.get_model('leagues.Matchup')
    current_week = season.week_number
    
    if round_type == 'championship':
        matchup = Matchup.objects.get(
        season=season, week_number=current_week)
  
        matchup.scoreboard.get_score()
        winner = matchup.scoreboard.get_winner()
        
        update_playoff_rankings(season, round_type, winner)
        
        return winner
    
    else:    
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
    

def advance_playoff_round(season, round_type=False):
    """Advance the playoff round based on round type"""
    conf_standings = get_playoff_teams_by_conf(season)
    
    if not round_type:
       update_final_playoff_clinches(season)
    else:
        winners = sim_round_matchups(season, round_type)
    
    if not round_type:
        generate_round_matchups(season, conf_rankings=conf_standings)
    elif round_type == 'wildcard':
        generate_round_matchups(season, round_type, conf_standings, winners)
    elif round_type == 'divisional':
        generate_round_matchups(season, round_type, conf_standings, winners)
    elif round_type == 'conference':
        generate_round_matchups(season, round_type, winners=winners)