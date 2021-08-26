# Generated by Django 3.2.6 on 2021-08-26 19:35

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0024_alter_season_schedule'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='season',
            name='schedule',
        ),
        migrations.AddField(
            model_name='matchup',
            name='date',
            field=models.DateField(default=datetime.date(2021, 8, 29)),
        ),
        migrations.AddField(
            model_name='matchup',
            name='is_preseason',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='matchup',
            name='week_number',
            field=models.PositiveSmallIntegerField(default=1),
        ),
        migrations.DeleteModel(
            name='Schedule',
        ),
    ]
