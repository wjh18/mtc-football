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
            streak = standing.streak
            if result == "Tie":
                standing.ties += 1
                if not streak == 0:
                    streak = 0
            elif result == team:
                standing.wins += 1
                if not streak > 0:
                    streak = 1
                else:
                    streak += 1
            else:
                standing.losses += 1
                if not streak < 0:
                    streak = -1
                else:
                    streak -= 1

            # Update PF and PA
            home_score = scores["Home"]
            away_score = scores["Away"]
            pf = standing.points_for
            pa = standing.points_against

            if team == matchup.home_team:
                pf += home_score
                pa += away_score
            else:
                pf += away_score
                pa += home_score

            standing.save()
