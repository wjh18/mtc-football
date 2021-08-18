import uuid
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from .utils import read_team_info_from_csv


class League(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    name = models.CharField(max_length=300)
    creation_date = models.DateTimeField(default=timezone.now)
    commissioner = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
    )
    commissioner_name = models.CharField(max_length=300)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Save League instance before referencing it for Team creation
        super().save(*args, **kwargs)

        # Read team data from CSV and create 32 teams in League
        team_info = read_team_info_from_csv()
        abbreviations = [*team_info.keys()]
        locations_and_names = [*team_info.values()]
        for team in range(0, 32):
            Team.objects.create(
                location=locations_and_names[team][0],
                name=locations_and_names[team][1],
                abbreviation=abbreviations[team],
                league=self)

    def get_absolute_url(self):
        return reverse("league_detail", args=[str(self.id)])
    

class Team(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    location = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=3)
    league = models.ForeignKey(
        League, on_delete=models.CASCADE,
        related_name='teams',
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("team_detail", args=[str(self.id)])
    