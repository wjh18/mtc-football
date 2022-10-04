from django.apps import apps
from django.db.models import F, Window
from django.db.models.functions import Rank

from .models import TeamRanking, TeamStanding


def generate_division_rankings(season):
    """
    Generate division rankings based on new standings for next week.
    """
    Division = apps.get_model("leagues.Division")
    divisions = Division.objects.filter(conference__league=season.league)
    division_rankings = {}
    for division in divisions:
        division_rank_qs = TeamStanding.objects.filter(
            season=season,
            week_number=season.week_number + 1,
            team__division__exact=division,
        ).annotate(
            rank=Window(
                expression=Rank(),
                order_by=[
                    F("wins").desc(),
                    F("losses"),
                    F("points_for").desc(),
                    F("points_against"),
                    F("team__location"),
                ],
            )
        )
        division_rankings[division] = division_rank_qs
        for team in division.teams.all():
            for division_rank in division_rankings[division]:
                if division_rank.team == team:
                    TeamRanking.objects.create(
                        standing=division_rank, division_ranking=division_rank.rank
                    )


def generate_conference_rankings(season):
    """
    Generate conference rankings based on new standings for next week.
    """
    Conference = apps.get_model("leagues.Conference")
    conferences = Conference.objects.filter(league=season.league)
    for conference in conferences:

        top_4_conference = TeamStanding.objects.filter(
            season=season,
            team__conference=conference,
            ranking__division_ranking=1,
            week_number=season.week_number + 1,
        ).annotate(
            rank=Window(
                expression=Rank(),
                order_by=[
                    F("wins").desc(),
                    F("losses"),
                    F("points_for").desc(),
                    F("points_against"),
                    F("team__location"),
                ],
            )
        )

        bottom_12_conference = (
            TeamStanding.objects.filter(
                season=season,
                team__conference=conference,
                week_number=season.week_number + 1,
            )
            .exclude(ranking__division_ranking=1)
            .annotate(
                rank=Window(
                    expression=Rank(),
                    order_by=[
                        F("wins").desc(),
                        F("losses"),
                        F("points_for").desc(),
                        F("points_against"),
                        F("team__location"),
                    ],
                )
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
    league_rankings = TeamStanding.objects.filter(
        season=season,
        week_number=season.week_number + 1,
    ).annotate(
        rank=Window(
            expression=Rank(),
            order_by=[
                F("wins").desc(),
                F("losses"),
                F("team__overall_rating"),
                F("streak").desc(),
                F("points_for").desc(),
                F("points_against"),
                F("team__location"),
            ],
        )
    )

    for team in season.league.teams.all():
        for standing in league_rankings:
            if standing.team == team:
                league_rank = standing.rank

        tr = TeamRanking.objects.get(
            standing=TeamStanding.objects.get(
                team=team, season=season, week_number=season.week_number + 1
            ),
        )
        tr.power_ranking = league_rank
        tr.save()


def update_rankings(season):
    """
    Update league rankings based on new standings for next week.
    """
    generate_division_rankings(season)
    generate_conference_rankings(season)
    generate_league_rankings(season)
