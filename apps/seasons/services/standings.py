from ..models import TeamStanding


def update_result_stats(standing, is_tie, is_winner, streaks):
    streak_win, streak_loss, streak_tie = streaks
    if is_tie:
        standing.ties += 1
        standing.streak = streak_tie
    elif is_winner:
        standing.wins += 1
        standing.streak = streak_win
    else:
        standing.losses += 1
        standing.streak = streak_loss


def update_pfpa_stats(standing, is_home, home_score, away_score):
    if is_home:
        standing.points_for += home_score
        standing.points_against += away_score
    else:
        standing.points_for += away_score
        standing.points_against += home_score


def update_streak_stats(standing):
    if standing.streak > 0:
        # team is on a win streak
        streak_win = standing.streak + 1
        streak_loss = -1
        streak_tie = 0
    elif standing.streak < 0:
        # team is on a losing streak
        streak_win = 1
        streak_loss = standing.streak - 1
        streak_tie = 0
    else:
        # first game of season
        streak_win = 1
        streak_loss = -1
        streak_tie = standing.streak

    return (streak_win, streak_loss, streak_tie)


def update_standings(season, matchups):
    """
    Generate scores and results for the current week, update standings.
    """
    for matchup in matchups:
        scores = matchup.get_score()
        winner = matchup.get_winner()

        for team in (matchup.home_team, matchup.away_team):
            standing = TeamStanding.objects.get(team=team, season=season)

            # Set matchup types
            is_home = False
            is_tie = False
            is_winner = False

            if team == matchup.home_team:
                is_home = True

            if winner == "Tie":
                is_tie = True
            elif winner == team:
                is_winner = True

            home_score = scores["Home"]
            away_score = scores["Away"]

            streaks = update_streak_stats(standing)
            update_result_stats(standing, is_tie, is_winner, streaks)
            update_pfpa_stats(standing, is_home, home_score, away_score)
            standing.save()
