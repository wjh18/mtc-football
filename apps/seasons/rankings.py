from django.apps import apps
from django.db.models import F, Window
from django.db.models.functions import Rank

from .models import TeamStanding


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
            for standing in division_rankings[division]:
                if standing.team == team:
                    standing.division_ranking = standing.rank
                    standing.save()


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
            division_ranking=1,
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
            )
            .exclude(division_ranking=1)
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

        for standing in top_4_conference:
            standing.conference_ranking = standing.rank
            standing.save()

        for standing in bottom_12_conference:
            standing.conference_ranking = standing.rank + 4
            standing.save()


def generate_league_rankings(season):
    """
    Generate league rankings based on new standings for next week.
    """
    league_rankings = TeamStanding.objects.filter(season=season,).annotate(
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
                standing.power_ranking = standing.rank
                standing.save()


def update_rankings(season):
    """
    Update league rankings based on new standings for next week.
    """
    generate_division_rankings(season)
    generate_conference_rankings(season)
    generate_league_rankings(season)
