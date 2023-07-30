from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.db import models
from django.urls import reverse


class Person(models.Model):
    league = models.ForeignKey(
        "leagues.League", on_delete=models.CASCADE, related_name="players"
    )
    team = models.ManyToManyField("teams.Team", through="Contract")
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    age = models.PositiveSmallIntegerField()
    experience = models.PositiveSmallIntegerField()
    prototype = models.CharField(max_length=50)
    overall_rating = models.PositiveSmallIntegerField()
    potential = models.PositiveSmallIntegerField()
    confidence = models.PositiveSmallIntegerField()
    iq = models.PositiveSmallIntegerField()
    is_free_agent = models.BooleanField(default=False)

    class Meta:
        abstract = True


class Player(Person):
    position = models.CharField(max_length=50)
    speed = models.PositiveSmallIntegerField()
    strength = models.PositiveSmallIntegerField()
    agility = models.PositiveSmallIntegerField()
    awareness = models.PositiveSmallIntegerField()
    stamina = models.PositiveSmallIntegerField()
    injury = models.PositiveSmallIntegerField()
    run_off = models.PositiveSmallIntegerField()
    pass_off = models.PositiveSmallIntegerField()
    special_off = models.PositiveSmallIntegerField()
    run_def = models.PositiveSmallIntegerField()
    pass_def = models.PositiveSmallIntegerField()
    special_def = models.PositiveSmallIntegerField()
    slug = models.SlugField(blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_absolute_url(self):
        return reverse("personnel:player_detail", args=[self.league.slug, self.slug])

    @property
    def active_contract(self):
        """Get the player's active contract.
        Returns None if no contract is active.
        """
        try:
            contract = self.contracts.get(is_active=True)
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            contract = None
        return contract

    @property
    def current_team(self):
        """Get the player's current team.
        Returns None if no contract is active.
        """
        contract = self.active_contract
        if contract is not None:
            return contract.team


class Contract(models.Model):
    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name="contracts",
    )
    team = models.ForeignKey(
        "teams.Team", on_delete=models.CASCADE, related_name="contracts"
    )
    is_active = models.BooleanField(default=True)

    @property
    def league(self):
        return self.team.league

    def __str__(self):
        return (
            f"{self.player} contract - "
            f"{self.team.abbreviation} - {self.team.league}"
        )
