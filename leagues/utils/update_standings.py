from ..models import TeamStanding, TeamRanking, Division, Conference

from django.db.models import F, Window
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
        current_standing.pk = None        
        current_standing._state.adding = True
        current_standing.week_number = current_week + 1
        current_standing.save()
        # wins = current_standing.wins
        # losses = current_standing.losses
        # ties = current_standing.ties
        # streak = current_standing.streak
        # points_for = current_standing.points_for
        # points_against = current_standing.points_against
        # home_wins = current_standing.
        # home_losses = current_standing.
        # home_ties = current_standing.
        # away_wins = current_standing.
        # away_losses = current_standing.
        # away_ties = current_standing.
        # div_wins = current_standing.
        # div_losses = current_standing.
        # div_ties = current_standing.
        # conf_wins = current_standing.
        # conf_losses = current_standing.
        # conf_ties = current_standing.
        # non_conf_wins = current_standing.
        # non_conf_losses = current_standing.
        # non_conf_ties = current_standing.
        # last_5_wins = current_standing.
        # last_5_losses = current_standing.
        # last_5_ties = current_standing.

        # TeamStanding.objects.create(
        #     team=team, season=season,
        #     week_number=current_week + 1, wins=wins, losses=losses,
        #     ties=ties, streak=streak, points_for=points_for,
        #     points_against=points_against)
                       
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
    """
    Generate division rankings based on new standings for next week.
    """
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
    
def generate_conference_rankings(season):
    """
    Generate conference rankings based on new standings for next week.
    """
    conferences = Conference.objects.filter(league=season.league)
    for conference in conferences:
        
        top_4_conference = TeamStanding.objects.filter(
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
    league_rank_qs = TeamStanding.objects.filter(
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
    return league_rank_qs
          
def update_rankings(season):
    """
    Update league rankings based on new standings for next week.
    """
    generate_division_rankings(season)
    generate_conference_rankings(season)
    league_rankings = generate_league_rankings(season)
    
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