from django.db import models


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

    # Find a way to pass team slug despite ManyToMany
    # def get_absolute_url(self):
    #     # self.league.teams.all()
    #     return reverse("personnel:player_detail",
    #                     args=[self.league, self.contract.team.slug,
    #                           self.slug])


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
    def get_league(self):
        return self.team.league

    def __str__(self):
        return (
            f"{self.player} contract - "
            f"{self.team.abbreviation} - {self.team.league}"
        )
