# Generated by Django 3.2.6 on 2021-10-04 03:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0003_auto_20211003_2257'),
    ]

    operations = [
        migrations.AlterField(
            model_name='matchup',
            name='slug',
            field=models.SlugField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='player',
            name='slug',
            field=models.SlugField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='team',
            name='slug',
            field=models.SlugField(blank=True, null=True),
        ),
    ]