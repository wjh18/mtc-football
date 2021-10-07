# App imports
from .models import (
    League, Player, Team, UserTeam,
    Season, Matchup, TeamStanding,
    Conference)
from leagues.utils.advance_season import advance_season_weeks
from leagues.utils.update_standings import (
    update_standings_for_byes,
    update_standings,
    update_rankings)

# Django imports
from django.http import HttpResponseRedirect
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


### Custom Mixins & Decorators ###

class LeagueContextMixin(ContextMixin):
    """
    Mixin for reducing duplicate get_context_data calls for league data.
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['league'] = League.objects.get(slug=self.kwargs['league'])
        context['season'] = Season.objects.get(
            league=context['league'], is_current=True)

        if self.kwargs.get('team'):
            context['team'] = Team.objects.get(
                league=context['league'], slug=self.kwargs['team'])

        return context


### Permissions Mixins & Decorators ###

class LeagueOwnerMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin for verifying user league ownership.
    """

    def test_func(self):
        if self.kwargs.get('league'):
            league = League.objects.get(slug=self.kwargs['league'])
            return self.request.user == league.user
        else:
            # Fallback for generic views which has no valid kwarg
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
    List the logged in user's active leagues.
    """
    model = League
    context_object_name = 'leagues'
    template_name = 'leagues/league/league_list.html'

    def get_queryset(self):
        return League.objects.filter(user=self.request.user)


class LeagueDetailView(LeagueOwnerMixin, DetailView):
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
        perform_delete = super().delete(request, *args, **kwargs)
        messages.success(self.request, self.success_message)
        return perform_delete


class WeeklyMatchupsView(LeagueOwnerMixin, ListView):
    """
    View weekly matchups for the active league and its current season.
    """
    model = Matchup
    context_object_name = 'matchups'
    template_name = 'leagues/league/matchups.html'

    def get_queryset(self):
        league = League.objects.get(slug=self.kwargs['league'])
        season = Season.objects.get(league=league, is_current=True)

        if self.kwargs.get('week_num'):
            week_number = self.kwargs['week_num']
        elif season.week_number >= 23:
            week_number = 22
        else:
            week_number = season.week_number

        return Matchup.objects.filter(
            season=season,
            week_number=week_number
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['league'] = League.objects.get(slug=self.kwargs['league'])
        context['season'] = Season.objects.get(league=context['league'],
                                               is_current=True)
        league = context['league']
        season = context['season']
        if self.kwargs.get('week_num'):
            week_number = self.kwargs['week_num']
        elif season.week_number >= 23:
            week_number = 22
        else:
            week_number = season.week_number
            
        context['week_num'] = self.kwargs.get('week_num', week_number)
        context['num_weeks'] = range(1, 23)
        
        context['divisional_matchups'] = Matchup.objects.filter(
            season=season,
            week_number=week_number,
            home_team__division=F('away_team__division')
        )
        
        context['conference_matchups'] = Matchup.objects.filter(
            season=season,
            week_number=week_number,
            home_team__division__conference=F('away_team__division__conference'),            
        ).exclude(home_team__division=F('away_team__division'))
        
        context['non_conf_matchups'] = Matchup.objects.filter(
            season=season,
            week_number=week_number
        ).exclude(home_team__division__conference=F('away_team__division__conference'))

        return context


class MatchupDetailView(LeagueOwnerMixin, LeagueContextMixin, DetailView):
    """
    View additional details related to an individual matchup.
    """
    model = Matchup
    context_object_name = 'matchup'
    template_name = 'leagues/league/matchup_detail.html'


class LeagueStandingsView(LeagueOwnerMixin, ListView):
    """
    View team standings by division, conference, or league-wide.
    """
    model = TeamStanding
    context_object_name = 'standings'
    template_name = 'leagues/league/standings.html'

    def get_queryset(self):
        league = League.objects.get(slug=self.kwargs['league'])
        season = get_object_or_404(Season, league=league, is_current=True)

        # Show final regular season standings during playoffs
        if season.week_number >= 19:
            week_number = 19
        else:
            week_number = season.week_number

        standings = TeamStanding.objects.filter(
            season=season, week_number=week_number
        ).order_by(
            'ranking__power_ranking'
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
        context['league'] = league
        season = get_object_or_404(Season, league=league,
                                   is_current=True)
        context['season'] = season

        context['afc'] = Conference.objects.get(name='AFC', league=league)
        context['nfc'] = Conference.objects.get(name='NFC', league=league)
        context['type'] = self.kwargs.get('type')

        # Show final regular season standings during playoffs
        if season.week_number >= 19:
            week_number = 19
        else:
            week_number = season.week_number

        context['division_standings'] = TeamStanding.objects.filter(
            season=season, week_number=week_number
        ).order_by(
            'ranking__division_ranking'
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
        ).order_by(
            'ranking__conference_ranking'
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


class PlayoffsView(LeagueOwnerMixin, ListView):
    """
    View playoff matchups / bracket for the current season
    """
    model = Matchup
    context_object_name = 'matchups'
    template_name = 'leagues/league/playoffs.html'

    def get_queryset(self):
        league = League.objects.get(slug=self.kwargs['league'])
        season = Season.objects.get(league=league, is_current=True)

        return Matchup.objects.filter(
            season__league=league,
            is_postseason=True
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['league'] = League.objects.get(slug=self.kwargs['league'])
        context['season'] = Season.objects.get(league=context['league'],
                                               is_current=True)
        season = context['season']
        
        matchups = Matchup.objects.filter(
            season=season,
            is_postseason=True
        )
        
        context['wildcard_matchups'] = matchups.filter(week_number=19)
        context['divisional_matchups'] = matchups.filter(week_number=20)
        context['conference_matchups'] = matchups.filter(week_number=21)
        context['championship_matchups'] = matchups.filter(week_number=22)
        
        return context


@login_required
@is_league_owner
def advance_regular_season(request, league, weeks=False):
    """
    Advance the regular season by chosen number of weeks.
    """
    league = get_object_or_404(League, slug=league)
    season = get_object_or_404(Season, league=league, is_current=True)
    current_week = season.week_number
    regular_season_weeks = 18

    if request.method == 'GET' and current_week <= regular_season_weeks:

        # Advance to end of regular season, not X number of weeks
        # Limit number of weeks if it sims past end of reg season
        week_limit = regular_season_weeks - (current_week - 1)
        if not weeks or weeks > week_limit:
            weeks = week_limit

        # Get scores and results for current week's matchups, update standings
        for week_num in range(current_week, current_week + weeks):
            matchups = Matchup.objects.filter(
                season=season, week_number=week_num)
            update_standings_for_byes(season, week_num)
            update_standings(season, week_num, matchups)
            update_rankings(season)
            # Progress season by X weeks and save instance
            advance_season_weeks(season)
            week_num += 1

        # Success message
        messages.add_message(request, messages.SUCCESS,
                             f'Advanced {weeks} week(s).')
    else:
        messages.add_message(request, messages.WARNING,
            f"It's playoff time, can't advance regular season.")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required
@is_league_owner
def advance_playoffs(request, league):
    """
    Advance the playoffs by chosen number of weeks
    """
    league = get_object_or_404(League, slug=league)
    season = get_object_or_404(Season, league=league, is_current=True)
    current_week = season.week_number

    if request.method == 'GET' and 19 <= current_week <= 22:        
        # Progress season by X weeks and save instance
        advance_season_weeks(season)
    else:
        messages.add_message(request, messages.WARNING,
            f"It's the regular season, can't advance playoffs.")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


### Team Views ###

class TeamListView(LeagueOwnerMixin, ListView):
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
        context['league'] = League.objects.get(slug=self.kwargs['league'])

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
        return Team.objects.filter(league__slug=self.kwargs['league'],
                                   slug=self.kwargs['slug'])


class TeamRosterView(LeagueOwnerMixin, ListView):
    """
    View an individual team's roster and player attributes,
    sorted by overall rating.
    """
    model = Team
    context_object_name = 'team'
    template_name = 'leagues/team/roster.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['league'] = League.objects.get(slug=self.kwargs['league'])
        context['team'] = Team.objects.get(league=context['league'],
                                           slug=self.kwargs['team'])
        context['contracts'] = context['team'].contracts.all()

        return context


class DepthChartView(LeagueOwnerMixin, ListView):
    """
    View an individual team's depth chart by position.
    """
    model = Team
    context_object_name = 'team'
    template_name = 'leagues/team/depth_chart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['league'] = League.objects.get(slug=self.kwargs['league'])
        context['team'] = Team.objects.get(league=context['league'],
                                           slug=self.kwargs['team'])

        contracts = context['team'].contracts.all()
        player_ids = contracts.values('player_id')
        position = self.kwargs.get('position', 'QB')
        context['active_position'] = position

        players = Player.objects.filter(id__in=player_ids)
        context['positions'] = list(dict.fromkeys(
            [player.position for player in players]
        ))
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
        season = get_object_or_404(Season, league=league, is_current=True)
        matchups = Matchup.objects.filter(
            Q(home_team=team) | Q(away_team=team), season=season
        ).order_by('week_number')

        return matchups


### Player views ###

class PlayerDetailView(LeagueOwnerMixin, LeagueContextMixin, DetailView):
    """
    View additional details about an individual player in a league.
    """
    model = Player
    context_object_name = 'player'
    template_name = 'leagues/player/player_detail.html'
