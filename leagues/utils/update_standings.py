from ..models import TeamStanding


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