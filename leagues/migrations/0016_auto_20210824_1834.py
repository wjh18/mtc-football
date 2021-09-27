# Generated by Django 3.2.6 on 2021-08-24 22:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('leagues', '0015_remove_team_conference'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='team',
            name='user',
        ),
        migrations.CreateModel(
            name='UserTeam',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active_team', models.BooleanField(default=True)),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='leagues.team')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]