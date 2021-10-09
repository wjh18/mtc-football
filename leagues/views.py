# Django imports
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.db.models import Q, F, FloatField, When, Case
from django.db.models.functions import Cast
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.base import ContextMixin
from django.contrib.auth.mixins import (
    LoginRequiredMixin, UserPassesTestMixin)

# App imports
from .models import (
    League, Player, Team, UserTeam,
    Season, Matchup, TeamStanding,
    Conference)
from leagues.utils.advance_season import (
    advance_season_weeks, advance_to_next_season)
from leagues.utils.update_standings import (
    update_standings_for_off_weeks,
    update_standings,
    update_rankings)


### Custom Mixins & Decorators ###

class LeagueContextMixin(ContextMixin):
    """
    Mixin for reducing duplicate get_context_data calls for league data.
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
     
        if self.kwargs.get('league'):
            league = League.objects.get(slug=self.kwargs['league'])
        else:
            # Fallback for generic views where league kwarg is 'object'
            league = self.object
        
        context['league'] = league
        context['season'] = Season.objects.get(league=league, is_current=True)

        if self.kwargs.get('team'):
            team_slug = self.kwargs['team']
            context['team'] = Team.objects.get(league=league, slug=team_slug)

        return context


### Permissions Mixins & Decorators ###

class LeagueOwnerMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin for verifying user league ownership in class-based views.
    """

    def test_func(self):
        if self.kwargs.get('league'):
            league = League.objects.get(slug=self.kwargs['league'])
            return self.request.user == league.user
        else:
            # Fallback for generic views where league kwarg is 'object'
            return self.request.user == self.get_object().user


def is_league_owner(func):
    """
    Decorator permission for function-based views that verifies
    whether the user is the league owner.
    """
    def wrap(request, *args, **kwargs):
        league = League.objects.get(slug=kwargs['league'])
        if league.user == request.user:
            return func(request, *args, **kwargs)
        else:
            raise PermissionDenied

    return wrap


### League Views ###

class LeagueListView(LoginRequiredMixin, ListView):
    """
    List the logged-in user's active leagues.
    """
    model = League
    context_object_name = 'leagues'
    template_name = 'leagues/league/league_list.html'

    def get_queryset(self):
        return League.objects.filter(user=self.request.user)


class LeagueDetailView(LeagueOwnerMixin, LeagueContextMixin, DetailView):
    """
    View an individual league's details.
    """
    model = League
    context_object_name = 'league'
    template_name = 'leagues/league/league_detail.html'
    

class LeagueCreateView(LoginRequiredMixin, CreateView):
    """
    Create a league and redirect to its list of teams.
    """
    model = League
    fields = ['name', 'gm_name']
    template_name = 'leagues/league/league_create.html'
    success_message = 'Your league has been created successfully.'

    def form_valid(self, form):
        """Overriden to add success message"""
        form.instance.user = self.request.user
        messages.success(self.request, self.success_message)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('leagues:team_list', args=[self.object.slug])


class LeagueUpdateView(LeagueOwnerMixin, UpdateView):
    """
    Update an individual league's details.
    """
    model = League
    fields = ['name', 'gm_name']
    template_name = 'leagues/league/league_update.html'
    success_message = 'Your league has been updated successfully.'

    def form_valid(self, form):
        """Overriden to add success message"""
        form.instance.user = self.request.user
        messages.success(self.request, self.success_message)
        return super().form_valid(form)


class LeagueDeleteView(LeagueOwnerMixin, DeleteView):
    """
    Delete an individual league.
    """
    model = League
    success_url = reverse_lazy('leagues:league_list')
    template_name = 'leagues/league/league_delete.html'
    success_message = 'Your league has been deleted sucessfully.'

    def delete(self, request, *args, **kwargs):
        """Overriden to add success message"""
        perform_delete = super().delete(request, *args, **kwargs)
        messages.success(self.request, self.success_message)
        return perform_delete


class WeeklyMatchupsView(LeagueOwnerMixin, LeagueContextMixin, ListView):
    """
    View weekly matchups for the active league and its current season.
    """
    model = Matchup
    context_object_name = 'matchups'
    template_name = 'leagues/league/matchups.html'

    def get_queryset(self):
        league = League.objects.get(slug=self.kwargs['league'])
        season = Season.objects.get(league=league, is_current=True)    
            
        week_kw = self.kwargs.get('week_num', False)
        weeks = range(1, 24)
        
        # Only accept valid week parameters in URL      
        if week_kw and (week_kw not in weeks or week_kw == 0):           
            raise Http404("Invalid week number supplied")
        elif not week_kw:
            week_number = season.week_number
        else:
            week_number = self.kwargs['week_num']
        
        return Matchup.objects.filter(season=season, week_number=week_number)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
                
        league = League.objects.get(slug=self.kwargs['league'])
        season = Season.objects.get(league=league, is_current=True)
        
        week_kw = self.kwargs.get('week_num', False)  
        weeks = range(1, 24)

        # Only accept valid week parameters in URL              
        if week_kw and (week_kw not in weeks or week_kw == 0):           
            raise Http404("Invalid week number supplied")
        elif not week_kw:
            week_number = season.week_number
        else:
            week_number = self.kwargs['week_num']
            
        context['week_num'] = week_number
        context['num_weeks'] = weeks
        
        context['divisional_matchups'] = Matchup.objects.filter(
            season=season, week_number=week_number,
            home_team__division=F('away_team__division')
        )
        
        context['conference_matchups'] = Matchup.objects.filter(
            season=season, week_number=week_number,
            home_team__division__conference=\
            F('away_team__division__conference')).exclude(
                home_team__division=F('away_team__division')
            )
        
        context['non_conf_matchups'] = Matchup.objects.filter(
            season=season, week_number=week_number).exclude(
                home_team__division__conference=\
                F('away_team__division__conference')
            )

        if week_number <= 18:        
            context['bye_teams'] = season.get_byes(week_number)

        return context


class MatchupDetailView(LeagueOwnerMixin, LeagueContextMixin, DetailView):
    """
    View additional details related to an individual matchup.
    """
    model = Matchup
    context_object_name = 'matchup'
    template_name = 'leagues/league/matchup_detail.html'


class LeagueStandingsView(LeagueOwnerMixin, LeagueContextMixin, ListView):
    """
    View team standings by division, conference, or league-wide.
    """
    model = TeamStanding
    context_object_name = 'standings'
    template_name = 'leagues/league/standings.html'

    def get_queryset(self):
        league = League.objects.get(slug=self.kwargs['league'])
        season = Season.objects.get(league=league, is_current=True)

        # Show final regular season standings during playoffs
        if season.week_number >= 19:
            week_number = 19
        else:
            week_number = season.week_number

        standings = TeamStanding.objects.filter(
            season=season, week_number=week_number
        ).order_by('ranking__power_ranking', '-team__overall_rating'
        ).annotate(
            pt_diff=F('points_for') - F('points_against'),
            win_pct=Case(
                When(
                    wins__gt=0,
                    then=Cast('wins', FloatField()) /
                        (F('wins') + F('losses') + F('ties'))
                ),
                default=F('wins'),
                output_field=FloatField()
            )
        )

        return standings

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        league = League.objects.get(slug=self.kwargs['league'])
        season = Season.objects.get(league=league, is_current=True)
        entity = self.kwargs.get('entity')
            
        if entity and entity not in ('conference', 'power'):
            raise Http404("Invalid standings entity supplied")    
        context['entity'] = entity

        # Show final regular season standings during playoffs
        if season.week_number >= 19:
            week_number = 19
        else:
            week_number = season.week_number

        context['division_standings'] = TeamStanding.objects.filter(
            season=season, week_number=week_number
        ).order_by('ranking__division_ranking', '-team__overall_rating'
        ).annotate(
            pt_diff=F('points_for') - F('points_against'),
            win_pct=Case(
                When(
                    wins__gt=0,
                    then=Cast('wins', FloatField()) /
                        (F('wins') + F('losses') + F('ties'))
                ),
                default=F('wins'),
                output_field=FloatField()
            )
        )

        context['conference_standings'] = TeamStanding.objects.filter(
            season=season, week_number=week_number
        ).order_by('ranking__conference_ranking', '-team__overall_rating'
        ).annotate(
            pt_diff=F('points_for') - F('points_against'),
            win_pct=Case(
                When(
                    wins__gt=0,
                    then=Cast('wins', FloatField()) /
                        (F('wins') + F('losses') + F('ties'))
                ),
                default=F('wins'),
                output_field=FloatField()
            )
        )

        return context


class PlayoffsView(LeagueOwnerMixin, LeagueContextMixin, ListView):
    """
    View playoff matchups / bracket for the current season
    """
    model = Matchup
    context_object_name = 'matchups'
    template_name = 'leagues/league/playoffs.html'

    def get_queryset(self):
        league = League.objects.get(slug=self.kwargs['league'])

        return Matchup.objects.filter(
            season__league=league,
            is_postseason=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        matchups = Matchup.objects.filter(
            season=context['season'],
            is_postseason=True)
        
        context['wildcard_matchups'] = matchups.filter(week_number=19)
        context['divisional_matchups'] = matchups.filter(week_number=20)
        context['conference_matchups'] = matchups.filter(week_number=21)
        context['championship_matchups'] = matchups.filter(week_number=22)
        
        return context


@login_required
@is_league_owner
def advance_season(request, league):
    """
    Advance the regular season, playoffs or to the next season.
    """
    league = get_object_or_404(League, slug=league)
    season = get_object_or_404(Season, league=league, is_current=True)
    current_week = season.week_number
    REGULAR_SEASON_WEEKS = 18
    LAST_WEEK_OF_PLAYOFFS = 22

    if request.method == 'POST':
        
        # Advance by X weeks or until end of phase
        if request.POST['advance'].isdigit():
            weeks = int(request.POST['advance'])
        else:
            weeks = False

        # Advance regular season
        if current_week <= REGULAR_SEASON_WEEKS:
            # Limit number of weeks if sim goes past end of reg season
            week_limit = REGULAR_SEASON_WEEKS - (current_week - 1)
            if not weeks or weeks > week_limit:
                weeks = week_limit

            # Get scores and results for each week's matchups, update standings
            for week_num in range(current_week, current_week + weeks):
                matchups = Matchup.objects.filter(
                    season=season, week_number=week_num,
                    scoreboard__is_final=False)
                update_standings_for_off_weeks(season, week_num, byes=True)
                update_standings(season, week_num, matchups)
                update_rankings(season)
                # Progress season by X weeks and save instance
                advance_season_weeks(season)
                week_num += 1

            messages.add_message(request, messages.SUCCESS,
                                f'Advanced regular season by {weeks} week(s).')
            
        # Advance playoffs
        elif REGULAR_SEASON_WEEKS + 1 <= current_week <= LAST_WEEK_OF_PLAYOFFS:
            # Limit number of weeks if it sims past end of reg season
            week_limit = LAST_WEEK_OF_PLAYOFFS - (current_week - 1)
            if not weeks or weeks > week_limit:
                weeks = week_limit
                
            # Get scores and results for each playoff round
            for week_num in range(current_week, current_week + weeks):
                advance_season_weeks(season)
                
            messages.add_message(request, messages.SUCCESS,
                                f'Advanced playoffs by {weeks} week(s).')
            
        # Conclude the season and start a new one
        elif current_week >= LAST_WEEK_OF_PLAYOFFS + 1:        
            advance_to_next_season(season)
            messages.add_message(request, messages.SUCCESS,
                                f'A new season has been started.')
        else:
            messages.add_message(request, messages.WARNING,
                f"Sorry, we aren't in the right part of the season for that!")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


### Team Views ###

class TeamListView(LeagueOwnerMixin, LeagueContextMixin, ListView):
    """
    List the teams belonging to the active league and provide context
    indicating whether the user's team has been selected.
    """
    model = Team
    context_object_name = 'team_list'
    template_name = 'leagues/league/team_list.html'

    def get_queryset(self):
        return Team.objects.filter(league__slug=self.kwargs['league'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if UserTeam.objects.filter(league=context['league']).exists():
            context['user_team'] = True
        else:
            context['user_team'] = False

        return context


class TeamDetailView(LeagueOwnerMixin, LeagueContextMixin, DetailView):
    """
    View additional details about an individual team.
    """
    model = Team
    context_object_name = 'team'
    template_name = 'leagues/team/team_detail.html'

    def get_queryset(self):
        team_slug = self.kwargs['slug']
        return Team.objects.filter(
            league__slug=self.kwargs['league'], slug=team_slug)


class TeamRosterView(LeagueOwnerMixin, LeagueContextMixin, ListView):
    """
    View an individual team's roster and player attributes,
    sorted by overall rating.
    """
    model = Team
    context_object_name = 'team'
    template_name = 'leagues/team/roster.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        team = context['team']
        context['contracts'] = team.contracts.all()
        return context


class DepthChartView(LeagueOwnerMixin, LeagueContextMixin, ListView):
    """
    View an individual team's depth chart by position.
    """
    model = Team
    context_object_name = 'team'
    template_name = 'leagues/team/depth_chart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        team = context['team']
        contracts = team.contracts.all()
        player_ids = contracts.values('player_id')
        players = Player.objects.filter(id__in=player_ids)
        
        positions = list(dict.fromkeys(
            [player.position for player in players]))
        position = self.kwargs.get('position', 'QB')
        
        if position not in positions:
            raise Http404("Position does not exist")
        
        context['positions'] = positions
        context['active_position'] = position
        context['players'] = Player.objects.filter(
            id__in=player_ids,
            position=position
        ).order_by('-overall_rating')

        return context


@login_required
@is_league_owner
def update_user_team(request, league):
    """
    Select the user-controlled team if the logged-in user is the league owner.
    """
    if request.method == 'POST':
        league = get_object_or_404(League, slug=league)

        try:
            selected_team = league.teams.get(pk=request.POST['teams'])
        except (KeyError, Team.DoesNotExist):
            # Redisplay the team selection page with an error.
            return render(request, 'leagues/league/team_list.html', {
                'league': league,
                'error_message': "You didn't select a team.",
            })
        else:
            UserTeam.objects.create(league=league, team=selected_team)
            messages.add_message(
                request, messages.SUCCESS,
                f'You are now the GM of the \
                {selected_team.location} {selected_team.name}.'
            )

            return HttpResponseRedirect(
                reverse('leagues:team_detail',
                        args=[league.slug, selected_team.slug]))


class TeamScheduleView(LeagueOwnerMixin, LeagueContextMixin, ListView):
    """
    View the schedule of matchups for an individual team's current season.
    """
    model = Matchup
    context_object_name = 'matchups'
    template_name = 'leagues/team/schedule.html'

    def get_queryset(self):
        league = League.objects.get(slug=self.kwargs['league'])
        team = Team.objects.get(league=league, slug=self.kwargs['team'])
        season = Season.objects.get(league=league, is_current=True)
        matchups = Matchup.objects.filter(
            Q(home_team=team) | Q(away_team=team), season=season
        ).order_by('week_number')

        return matchups
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        team = context['team']
        season = context['season']        
        context['bye_week'] = team.check_bye_week(season)
        
        return context


### Player views ###

class PlayerDetailView(LeagueOwnerMixin, LeagueContextMixin, DetailView):
    """
    View additional details about an individual player in a league.
    """
    model = Player
    context_object_name = 'player'
    template_name = 'leagues/player/player_detail.html'
