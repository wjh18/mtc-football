from ..models import TeamStanding


def dupe_standings_for_byes(season, current_week):
    """
    Duplicate the standings of teams that have a regular season
    bye week by copying their current week's TeamStanding instance.
    """
    teams = season.get_byes()
    standings = TeamStanding.objects.filter(
        team__in=teams, season=season, week_number=current_week)
    
    for standing in standings:  
        standing.pk = None        
        standing._state.adding = True
        standing.week_number = current_week + 1
        standing.save()

                       
def update_standings(season, current_week, matchups):
    """
    Generate scores and results for the current week, update standings.
    """
    for matchup in matchups:
        scores = matchup.scoreboard.get_score()
        winner = matchup.scoreboard.get_winner()
        
        for team in (matchup.home_team, matchup.away_team):
            standing = TeamStanding.objects.get(
                team=team, season=season,
                week_number=current_week)  
            
            standing.pk = None        
            standing._state.adding = True
            standing.week_number = current_week + 1
            
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
            
            # Set matchup type
            is_divisional = matchup.is_divisional
            is_conference = matchup.is_conference

            # Update PF and PA and check home team
            if team == matchup.home_team:
                is_home = True
                standing.points_for += scores['Home']
                standing.points_against += scores['Away']
            else:
                is_home = False
                standing.points_for += scores['Away']
                standing.points_against += scores['Home']
            
            # Update standings based on result   
            if winner == 'Tie':      
                standing.ties += 1
                standing.streak = streak_tie
                
                if is_home:
                    standing.home_ties += 1
                else:
                    standing.away_ties += 1
                    
                if is_divisional:
                    standing.div_ties += 1
                elif is_conference:
                    standing.conf_ties += 1
                else:
                    standing.non_conf_ties += 1
                          
            elif winner == team: 
                standing.wins += 1
                standing.streak = streak_win
                
                if is_home:
                    standing.home_wins += 1
                else:
                    standing.away_wins += 1
                    
                if is_divisional:
                    standing.div_wins += 1
                elif is_conference:
                    standing.conf_wins += 1
                else:
                    standing.non_conf_wins += 1
                
            else:
                standing.losses += 1
                standing.streak = streak_loss
                
                if is_home:
                    standing.home_losses += 1
                else:
                    standing.away_losses += 1
                    
                if is_divisional:
                    standing.div_losses += 1
                elif is_conference:
                    standing.conf_losses += 1
                else:
                    standing.non_conf_losses += 1
            
            # Update Last 5 standings, take bye weeks into account
            if current_week > 4:
                last_5_week_num = current_week - 4
            else:
                last_5_week_num = current_week - (current_week - 1)
            
            bye_week = team.check_bye_week(season)
            if last_5_week_num <= bye_week <= current_week:
                last_5_week_num -= 1
                
            last_5_standing = TeamStanding.objects.get(
                team=team, season=season,
                week_number=last_5_week_num)
            
            standing.last_5_wins = standing.wins - last_5_standing.wins
            standing.last_5_losses = standing.losses - last_5_standing.losses
            standing.last_5_ties = standing.ties - last_5_standing.ties
            
            # Save new instance
            standing.save()