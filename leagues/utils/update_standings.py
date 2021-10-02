from ..models import TeamStanding, TeamRanking, Division, Conference

from django.db.models import Q, F, Window, Case, When, Value, IntegerField
from django.db.models.functions import DenseRank


def update_standings_for_byes(season, current_week):
    """
    Update the standings of teams that have a 'bye' week this week.
    """
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
    """
    Generate scores and results for the current week, update standings.
    """
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

def generate_division_rankings(season):
    divisions = Division.objects.filter(conference__league=season.league)
    division_rankings = {}
    for division in divisions:
        division_rank_qs = TeamStanding.objects.filter(
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
    return division_rankings
    
def generate_conference_rankings(season):
    conferences = Conference.objects.filter(league=season.league)
    for conference in conferences:
        
        top_4_standings = TeamStanding.objects.filter(
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

        bottom_12_standings = TeamStanding.objects.filter(
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
                           
        for top_4_with_rank in top_4_standings:
            print(top_4_with_rank.rank)
            team_ranking = TeamRanking.objects.get(
                standing=top_4_with_rank,
            )
            team_ranking.conference_ranking = top_4_with_rank.rank
            team_ranking.save()
            
        for bottom_12_with_rank in bottom_12_standings:
            print(bottom_12_with_rank.rank)
            team_ranking = TeamRanking.objects.get(
                standing=bottom_12_with_rank,
            )
            team_ranking.conference_ranking = bottom_12_with_rank.rank + 4
            team_ranking.save()

def get_league_rankings(season):
    league_rank_qs = TeamStanding.objects.filter(
        week_number=season.week_number + 1,
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
    return league_rank_qs
          
def update_rankings(season):
    """
    Update league rankings based on new standings for next week.
    """
    generate_division_rankings(season)
    generate_conference_rankings(season)
    league_rankings = get_league_rankings(season)
    
    for team in season.league.teams.all():
                
        # for standing in division_rankings[team.division]:
        #     if standing.team == team:
        #         division_rank = standing.rank
                
        # for standing in conference_rankings[team.division.conference]:
        #     if standing.team == team:
        #         conference_rank = standing.rank
                
        for standing in league_rankings:
            if standing.team == team:
                league_rank = standing.rank
                
        tr = TeamRanking.objects.get(
            standing=TeamStanding.objects.get(
                        team=team, season=season,
                        week_number=season.week_number + 1),
            # division_ranking=division_rank,
            # conference_ranking=conference_rank,
        )
        tr.power_ranking = league_rank
        tr.save()