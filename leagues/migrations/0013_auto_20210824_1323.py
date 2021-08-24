# Generated by Django 3.2.6 on 2021-08-24 17:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0012_conference_division'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='conference',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='teams', to='leagues.conference'),
        ),
        migrations.AddField(
            model_name='team',
            name='division',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='teams', to='leagues.division'),
        ),
    ]