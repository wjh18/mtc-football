from ..models import TeamStanding, TeamRanking

from django.db.models import F, Q, Window
from django.db.models.functions import Rank


def update_standings_for_byes(season, current_week):
    """For teams on a bye week, update their standings"""
    byes = season.get_byes()
    for team in byes:
        current_standing = TeamStanding.objects.get(
            team=team, season=season,
            week_number=current_week)
        wins = current_standing.wins
        losses = current_standing.losses
        ties = current_standing.ties
        streak = current_standing.streak
        points_for = current_standing.points_for
        points_against = current_standing.points_against

        TeamStanding.objects.create(
            team=team, season=season,
            week_number=current_week + 1, wins=wins, losses=losses,
            ties=ties, streak=streak, points_for=points_for,
            points_against=points_against)
                       
def update_standings(season, current_week, matchups):
    """Get scores and results for this weeks matchup, then update standings"""
    for matchup in matchups:
        scores = matchup.scoreboard.get_score()
        winner = matchup.scoreboard.get_winner()

        for team in (matchup.home_team, matchup.away_team):
            current_standing = TeamStanding.objects.get(
                team=team, season=season,
                week_number=current_week)

            wins = current_standing.wins
            losses = current_standing.losses
            ties = current_standing.ties
            streak = current_standing.streak

            if winner == 'Tie':
                ties = current_standing.ties + 1
                streak = 0
            elif winner == team:
                wins = current_standing.wins + 1
                streak = current_standing.streak + 1
            else:
                losses = current_standing.losses + 1
                streak = 0

            if team == matchup.home_team:
                points_for = current_standing.points_for + scores['Home']
                points_against = current_standing.points_against + \
                    scores['Away']
            else:
                points_for = current_standing.points_for + scores['Away']
                points_against = current_standing.points_against + \
                    scores['Home']

            TeamStanding.objects.create(
                team=team, season=season,
                week_number=current_week + 1, wins=wins, losses=losses,
                ties=ties, streak=streak, points_for=points_for,
                points_against=points_against)
            
def update_rankings(season):
    
    for team in season.league.teams.all():
        
        division_rank_qs = TeamStanding.objects.filter(
            week_number=season.week_number + 1,
            team__division__exact=team.division
        ).annotate(
            rank=Window(
                expression=Rank(),
                order_by=[F('wins').desc(), F('losses'),F('points_for').desc(),
                        F('points_against')],
            )
        )
        for standing in division_rank_qs:
            if standing.team == team:
                division_rank = standing.rank
             
        conference_rank_qs = TeamStanding.objects.filter(
            week_number=season.week_number + 1,
            team__division__conference__exact=team.division.conference
        ).annotate(
            rank=Window(
                expression=Rank(),
                order_by=[F('wins').desc(), F('losses'),F('points_for').desc(),
                        F('points_against')],
            )
        )
        for standing in conference_rank_qs:
            if standing.team == team:
                conference_rank = standing.rank
                
        league_rank_qs = TeamStanding.objects.filter(
                week_number=season.week_number + 1,
        ).annotate(
            rank=Window(
                expression=Rank(),
                order_by=[F('wins').desc(), F('losses'),F('points_for').desc(),
                        F('points_against')],
            )
        )
        for standing in league_rank_qs:
            if standing.team == team:
                league_rank = standing.rank   
                
        TeamRanking.objects.create(standing=TeamStanding.objects.get(
                                                team=team, season=season,
                                                week_number=season.week_number + 1),
                                   division_ranking=division_rank,
                                   conference_ranking=conference_rank,
                                   power_ranking=league_rank,
                                   )
        
        # standings = TeamStanding.objects.filter(week_number=season.week_number + 1)
        # league_standings = standings.order_by(
        #     '-wins', 'losses', '-points_for', 'points_against')
    
        # division_standings = standings.filter(
        #     team__division__exact=team.division).order_by(
        #         '-wins', 'losses', '-points_for', 'points_against')        
        # conference_standings = standings.filter(
        #     team__division__conference__exact=team.division.conference).order_by(
        #         '-wins', 'losses', '-points_for', 'points_against')
            
        # d_rank = 1
        # for team_standing in division_standings:
        #     if team_standing.team == team:
        #         team_ranking.division_ranking = d_rank
        #         team_ranking.save()
        #     d_rank += 1
                
        # c_rank = 1
        # for team_standing in conference_standings:
        #     if team_standing.team == team:
        #         team_ranking.conference_ranking = c_rank
        #         team_ranking.save()
        #     c_rank += 1
            
        # l_rank = 1
        # for team_standing in league_standings:
        #     if team_standing.team == team:
        #         team_ranking.power_ranking = l_rank
        #         team_ranking.save()
        #     l_rank += 1