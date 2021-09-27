# Generated by Django 3.2.6 on 2021-09-27 06:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0031_teamstanding_week_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='season',
            name='phase',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Re-signing'), (2, 'Free Agent Signing'), (3, 'Draft'), (4, 'Regular Season'), (5, 'Playoffs'), (6, 'Offseason')], default=4),
        ),
        migrations.CreateModel(
            name='TeamRanking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('power_ranking', models.PositiveSmallIntegerField(default=1)),
                ('conference_ranking', models.PositiveSmallIntegerField(default=1)),
                ('division_ranking', models.PositiveSmallIntegerField(default=1)),
                ('standing', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='leagues.teamstanding')),
            ],
        ),
    ]
