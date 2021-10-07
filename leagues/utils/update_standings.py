from django.db.models import F, Window
from django.db.models.functions import DenseRank

from ..models import TeamStanding, TeamRanking, Division, Conference


def get_matchup_type(matchup):
    """
    Determine whether the matchup is Divisional, Conference or Non-Conference.
    """
    home_team = matchup.home_team
    away_team = matchup.away_team
    if home_team.division == away_team.division:
        return 'Divisional'
    elif home_team.division.conference == away_team.division.conference:
        return 'Conference'
    else:
        return 'Non-Conference'


def update_standings_for_byes(season, current_week):
    """
    Update the standings of teams that have a 'bye' week this week
    by copying their current week's TeamStanding instance.
    """
    byes = season.get_byes()
    for team in byes:
        current_standing = TeamStanding.objects.get(
            team=team, season=season,
            week_number=current_week)
        current_standing.pk = None        
        current_standing._state.adding = True
        current_standing.week_number = current_week + 1
        current_standing.save()

                       
def update_standings(season, current_week, matchups):
    """
    Generate scores and results for the current week, update standings.
    """
    for matchup in matchups:
        scores = matchup.scoreboard.get_score()
        winner = matchup.scoreboard.get_winner()
        matchup_type = get_matchup_type(matchup)
        
        for team in (matchup.home_team, matchup.away_team):
            current_standing = TeamStanding.objects.get(
                team=team, season=season,
                week_number=current_week)  
                 
            # Get current regular standings        
            wins = current_standing.wins
            losses = current_standing.losses
            ties = current_standing.ties
            streak = current_standing.streak
            points_for = current_standing.points_for
            points_against = current_standing.points_against
            # Get current home and away standings
            home_wins = current_standing.home_wins
            home_losses = current_standing.home_losses
            home_ties = current_standing.home_ties
            away_wins = current_standing.away_wins
            away_losses = current_standing.away_losses
            away_ties = current_standing.away_ties
            # Get current entity standings
            div_wins = current_standing.div_wins
            div_losses = current_standing.div_losses
            div_ties = current_standing.div_ties
            conf_wins = current_standing.conf_wins
            conf_losses = current_standing.conf_losses
            conf_ties = current_standing.conf_ties
            non_conf_wins = current_standing.non_conf_wins
            non_conf_losses = current_standing.non_conf_losses
            non_conf_ties = current_standing.non_conf_ties
            
            if streak > 0:
                pass # team is on a win streak
                streak_win = streak + 1
                streak_loss = -1
                streak_tie = 0
            elif streak < 0:
                pass # team is on a losing streak
                streak_win = 1
                streak_loss = streak - 1
                streak_tie = 0
            else:
                pass # first game of season
                streak_win = 1
                streak_loss = -1
                streak_tie = streak

            # Update W/L/T, PF/PA, and Home/Away standings
            if team == matchup.home_team:
                points_for += scores['Home']
                points_against += scores['Away']
                if winner == 'Tie':
                    ties += 1
                    home_ties += 1
                    streak = streak_tie
                elif winner == team:
                    wins += 1
                    home_wins += 1
                    streak = streak_win
                else:
                    losses += 1
                    home_losses += 1
                    streak = streak_loss
            else:
                points_for += scores['Away']
                points_against += scores['Home']
                if winner == 'Tie':
                    ties += 1
                    away_ties += 1
                    streak = streak_tie
                elif winner == team:
                    wins += 1
                    away_wins += 1
                    streak = streak_win
                else:
                    losses += 1
                    away_losses += 1
                    streak = streak_loss
                    
            # Update type standings    
            if matchup_type == 'Divisional':
                if winner == 'Tie':
                    div_ties += 1                    
                elif winner == team:
                    div_wins += 1
                else:
                    div_losses += 1
            elif matchup_type == 'Conference':
                if winner == 'Tie':
                    conf_ties += 1                    
                elif winner == team:
                    conf_wins += 1
                else:
                    conf_losses += 1
            else:
                if winner == 'Tie':
                    non_conf_ties += 1                    
                elif winner == team:
                    non_conf_wins += 1
                else:
                    non_conf_losses += 1
            
            # Update Last 5 standings
            if current_week > 4:
                last_5_week_num = current_week - 4
            else:
                last_5_week_num = current_week - (current_week - 1)
                
            last_5_standing = TeamStanding.objects.get(
                team=team, season=season,
                week_number=last_5_week_num)
            
            last_5_wins = wins - last_5_standing.wins
            last_5_losses = losses - last_5_standing.losses
            last_5_ties = ties - last_5_standing.ties

            TeamStanding.objects.create(
                team=team, season=season, week_number=current_week + 1,
                wins=wins, losses=losses, ties=ties, streak=streak,
                points_for=points_for, points_against=points_against,
                home_wins=home_wins, home_losses=home_losses, home_ties=home_ties,
                away_wins=away_wins, away_losses=away_losses, away_ties=away_ties,
                div_wins=div_wins, div_losses=div_losses, div_ties=div_ties,
                conf_wins=conf_wins, conf_losses=conf_losses, conf_ties=conf_ties,
                non_conf_wins=non_conf_wins, non_conf_losses=non_conf_losses,
                non_conf_ties=non_conf_ties, last_5_wins=last_5_wins,
                last_5_losses=last_5_losses, last_5_ties=last_5_ties)


def generate_division_rankings(season):
    """
    Generate division rankings based on new standings for next week.
    """
    divisions = Division.objects.filter(conference__league=season.league)
    division_rankings = {}
    for division in divisions:
        division_rank_qs = TeamStanding.objects.filter(
            season=season,
            week_number=season.week_number + 1,
            team__division__exact=division
        ).annotate(
            rank=Window(
                expression=DenseRank(),
                order_by=[
                    F('wins').desc(), F('losses'),
                    F('points_for').desc(),
                    F('points_against')
                ],
            )
        )
        division_rankings[division] = division_rank_qs
        for team in division.teams.all():
            for division_rank in division_rankings[division]:
                if division_rank.team == team:
                    TeamRanking.objects.create(
                        standing=division_rank,
                        division_ranking=division_rank.rank
                    )

    
def generate_conference_rankings(season):
    """
    Generate conference rankings based on new standings for next week.
    """
    conferences = Conference.objects.filter(league=season.league)
    for conference in conferences:
        
        top_4_conference = TeamStanding.objects.filter(
            season=season,
            team__division__conference=conference,
            ranking__division_ranking=1,
            week_number=season.week_number + 1).annotate(
                rank=Window(
                    expression=DenseRank(),
                    order_by=[
                        F('wins').desc(), F('losses'),
                        F('points_for').desc(),
                        F('points_against')
                    ],
                )
            )

        bottom_12_conference = TeamStanding.objects.filter(
            season=season,
            team__division__conference=conference,
            week_number=season.week_number + 1).exclude(
                ranking__division_ranking=1).annotate(
                    rank=Window(
                        expression=DenseRank(),
                        order_by=[
                            F('wins').desc(), F('losses'),
                            F('points_for').desc(),
                            F('points_against')
                        ],
                    )
                )
                           
        for top_4_with_rank in top_4_conference:
            team_ranking = TeamRanking.objects.get(
                standing=top_4_with_rank,
            )
            team_ranking.conference_ranking = top_4_with_rank.rank
            team_ranking.save()
            
        for bottom_12_with_rank in bottom_12_conference:
            team_ranking = TeamRanking.objects.get(
                standing=bottom_12_with_rank,
            )
            team_ranking.conference_ranking = bottom_12_with_rank.rank + 4
            team_ranking.save()


def generate_league_rankings(season):
    """
    Generate league rankings based on new standings for next week.
    """
    league_rankings = TeamStanding.objects.filter(
        season=season,
        week_number=season.week_number + 1,
    ).annotate(
        rank=Window(
            expression=DenseRank(),
            order_by=[
                F('wins').desc(), F('losses'),
                F('team__overall_rating'),
                F('streak').desc(),
                F('points_for').desc(),
                F('points_against')
            ],
        )
    )

    for team in season.league.teams.all():           
        for standing in league_rankings:
            if standing.team == team:
                league_rank = standing.rank
                
        tr = TeamRanking.objects.get(
            standing=TeamStanding.objects.get(
                        team=team, season=season,
                        week_number=season.week_number + 1),
        )
        tr.power_ranking = league_rank
        tr.save()

          
def update_rankings(season):
    """
    Update league rankings based on new standings for next week.
    """
    generate_division_rankings(season)
    generate_conference_rankings(season)
    generate_league_rankings(season)
    
    
