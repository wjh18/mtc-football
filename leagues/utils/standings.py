from django.utils.text import StreamingBuffer
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
        

class UpdateStanding:
        
    def __init__(self, standing, current_week, home_score, away_score, is_div,
                is_conf, is_home=False, is_tie=False, is_winner=False):
        self.standing = standing
        self.current_week = current_week
        self.home_score = home_score
        self.away_score = away_score
        self.is_div = is_div
        self.is_conf = is_conf
        self.is_home = is_home
        self.is_tie = is_tie
        self.is_winner = is_winner
    
    def check_stats(self):
        self.update_type_stats()
        self.update_loc_stats()
        self.update_streak_stats()
        self.update_result_stats()
        self.update_pfpa_stats()
        self.update_last_5_stats()
        self.standing.save()

    def update_type_stats(self):
        if self.is_div and self.is_tie:
            self.standing.div_ties += 1
        elif self.is_div and self.is_winner:
            self.standing.div_wins += 1
        elif self.is_div and not self.is_winner:
            self.standing.div_losses += 1
        elif self.is_conf and self.is_tie:
            self.standing.conf_ties += 1
        elif self.is_conf and self.is_winner:
            self.standing.conf_wins += 1
        elif self.is_conf and not self.is_winner:
            self.standing.conf_losses += 1
        elif not self.is_div and not self.is_conf and self.is_tie:
            self.standing.non_conf_ties += 1
        elif not self.is_div and not self.is_conf and self.is_winner:
            self.standing.non_conf_wins += 1
        elif not self.is_div and not self.is_conf and not self.is_winner:
            self.standing.non_conf_losses += 1
            
    def update_loc_stats(self):
        if self.is_home and self.is_tie:
            self.standing.home_ties += 1
        elif self.is_home and self.is_winner:
            self.standing.home_wins += 1
        elif self.is_home and not self.is_winner:
            self.standing.home_losses += 1
        elif not self.is_home and self.is_tie:
            self.standing.away_ties += 1
        elif not self.is_home and self.is_winner:
            self.standing.away_wins += 1
        elif not self.is_home and not self.is_winner:
            self.standing.away_losses += 1
            
    def update_result_stats(self):
        if self.is_tie:
            self.standing.ties += 1
            self.standing.streak = self.streak_tie
        elif self.is_winner:
            self.standing.wins += 1
            self.standing.streak = self.streak_win
        else:
            self.standing.losses += 1
            self.standing.streak = self.streak_loss
            
    def update_pfpa_stats(self):
        if self.is_home:
            self.standing.points_for += self.home_score
            self.standing.points_against += self.away_score
        else:
            self.standing.points_for += self.away_score
            self.standing.points_against += self.home_score
            
    def update_streak_stats(self):
        if self.standing.streak > 0:
            # team is on a win streak
            self.streak_win = self.standing.streak + 1
            self.streak_loss = -1
            self.streak_tie = 0
        elif self.standing.streak < 0:
            # team is on a losing streak
            self.streak_win = 1
            self.streak_loss = self.standing.streak - 1
            self.streak_tie = 0
        else:
            # first game of season
            self.streak_win = 1
            self.streak_loss = -1
            self.streak_tie = self.standing.streak
            
    def update_last_5_stats(self):
        if self.current_week > 4:
            last_5_week_num = self.current_week - 4
        else:
            last_5_week_num = self.current_week - (self.current_week - 1)
        
        bye_week = self.standing.team.check_bye_week(self.standing.season)
        if last_5_week_num <= bye_week <= self.current_week:
            last_5_week_num -= 1
            
        last_5_standing = TeamStanding.objects.get(
            team=self.standing.team, season=self.standing.season,
            week_number=last_5_week_num)
        
        self.standing.last_5_wins = self.standing.wins - last_5_standing.wins
        self.standing.last_5_losses = self.standing.losses - last_5_standing.losses
        self.standing.last_5_ties = self.standing.ties - last_5_standing.ties

                       
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
                    
            # Set matchup types
            is_div = matchup.is_divisional
            is_conf = matchup.is_conference
            is_home = False
            is_tie = False
            is_winner = False
            
            if team == matchup.home_team:
                is_home = True
            
            if winner == 'Tie':
                is_tie = True
            elif winner == team:
                is_winner = True
                
            home_score = scores['Home']
            away_score = scores['Away']
                
            update_standing = UpdateStanding(
                standing, current_week, home_score, away_score,
                is_div, is_conf, is_home, is_tie, is_winner
            )
            update_standing.check_stats()
            
            # # Set matchup type
            # is_divisional = matchup.is_divisional
            # is_conference = matchup.is_conference
            
            # # Update PF and PA and check home team
            # if team == matchup.home_team:
            #     is_home = True
            #     standing.points_for += scores['Home']
            #     standing.points_against += scores['Away']
            # else:
            #     is_home = False
            #     standing.points_for += scores['Away']
            #     standing.points_against += scores['Home']
            
            # if standing.streak > 0:
            #     # team is on a win streak
            #     streak_win = standing.streak + 1
            #     streak_loss = -1
            #     streak_tie = 0
            # elif standing.streak < 0:
            #     # team is on a losing streak
            #     streak_win = 1
            #     streak_loss = standing.streak - 1
            #     streak_tie = 0
            # else:
            #     # first game of season
            #     streak_win = 1
            #     streak_loss = -1
            #     streak_tie = standing.streak
            
            # # Update standings based on result   
            # if winner == 'Tie':      
            #     standing.ties += 1
            #     standing.streak = streak_tie
                
            #     if is_home:
            #         standing.home_ties += 1
            #     else:
            #         standing.away_ties += 1
                    
            #     if is_divisional:
            #         standing.div_ties += 1
            #     elif is_conference:
            #         standing.conf_ties += 1
            #     else:
            #         standing.non_conf_ties += 1
                          
            # elif winner == team: 
            #     standing.wins += 1
            #     standing.streak = streak_win
                
            #     if is_home:
            #         standing.home_wins += 1
            #     else:
            #         standing.away_wins += 1
                    
            #     if is_divisional:
            #         standing.div_wins += 1
            #     elif is_conference:
            #         standing.conf_wins += 1
            #     else:
            #         standing.non_conf_wins += 1
                
            # else:
            #     standing.losses += 1
            #     standing.streak = streak_loss
                
            #     if is_home:
            #         standing.home_losses += 1
            #     else:
            #         standing.away_losses += 1
                    
            #     if is_divisional:
            #         standing.div_losses += 1
            #     elif is_conference:
            #         standing.conf_losses += 1
            #     else:
            #         standing.non_conf_losses += 1
            
            # # Update Last 5 standings, take bye weeks into account
            # if current_week > 4:
            #     last_5_week_num = current_week - 4
            # else:
            #     last_5_week_num = current_week - (current_week - 1)
            
            # bye_week = team.check_bye_week(season)
            # if last_5_week_num <= bye_week <= current_week:
            #     last_5_week_num -= 1
                
            # last_5_standing = TeamStanding.objects.get(
            #     team=team, season=season,
            #     week_number=last_5_week_num)
            
            # standing.last_5_wins = standing.wins - last_5_standing.wins
            # standing.last_5_losses = standing.losses - last_5_standing.losses
            # standing.last_5_ties = standing.ties - last_5_standing.ties
            
            # # Save new instance
            # standing.save()