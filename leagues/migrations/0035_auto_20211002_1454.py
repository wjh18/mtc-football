# Generated by Django 3.2.6 on 2021-10-02 18:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0034_team_overall_rating'),
    ]

    operations = [
        migrations.AddField(
            model_name='teamstanding',
            name='away_losses',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='teamstanding',
            name='away_ties',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='teamstanding',
            name='away_wins',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='teamstanding',
            name='conf_losses',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='teamstanding',
            name='conf_ties',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='teamstanding',
            name='conf_wins',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='teamstanding',
            name='div_losses',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='teamstanding',
            name='div_ties',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='teamstanding',
            name='div_wins',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='teamstanding',
            name='home_losses',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='teamstanding',
            name='home_ties',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='teamstanding',
            name='home_wins',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='teamstanding',
            name='last_5_losses',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='teamstanding',
            name='last_5_ties',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='teamstanding',
            name='last_5_wins',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='teamstanding',
            name='non_conf_losses',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='teamstanding',
            name='non_conf_ties',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='teamstanding',
            name='non_conf_wins',
            field=models.SmallIntegerField(default=0),
        ),
    ]
