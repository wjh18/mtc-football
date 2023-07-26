from ..models import TeamStanding


def update_standings(season, matchups):
    """
    Generate scores and results for the current week, update standings.
    """
    for matchup in matchups:
        scores = matchup.get_score()
        result = matchup.get_winner()

        for team in (matchup.home_team, matchup.away_team):
            standing = TeamStanding.objects.get(team=team, season=season)

            # Update results and streaks
            if result == "Tie":
                standing.ties += 1
                if not standing.streak == 0:
                    standing.streak = 0
            elif result == team:
                standing.wins += 1
                if not standing.streak > 0:
                    standing.streak = 1
                else:
                    standing.streak += 1
            else:
                standing.losses += 1
                if not standing.streak < 0:
                    standing.streak = -1
                else:
                    standing.streak -= 1

            # Update PF and PA
            home_score = scores["Home"]
            away_score = scores["Away"]

            if team == matchup.home_team:
                standing.points_for += home_score
                standing.points_against += away_score
            else:
                standing.points_for += away_score
                standing.points_against += home_score

            standing.save()
