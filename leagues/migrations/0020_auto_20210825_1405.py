# Generated by Django 3.2.6 on 2021-08-25 18:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0019_auto_20210825_1129'),
    ]

    operations = [
        migrations.CreateModel(
            name='Matchup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('away_team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='away_matchups', to='leagues.team')),
                ('home_team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='home_matchups', to='leagues.team')),
                ('season', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='matchups', to='leagues.season')),
            ],
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Scoreboard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('matchup', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='leagues.matchup')),
            ],
        ),
        migrations.RemoveField(
            model_name='playerstats',
            name='match',
        ),
        migrations.DeleteModel(
            name='Match',
        ),
        migrations.AddField(
            model_name='playerstats',
            name='matchup',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='player_stats', to='leagues.matchup'),
        ),
        migrations.AddField(
            model_name='season',
            name='schedule',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='leagues.schedule'),
        ),
    ]