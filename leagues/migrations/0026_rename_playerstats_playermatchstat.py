# Generated by Django 3.2.6 on 2021-08-26 22:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0025_auto_20210826_1535'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='PlayerStats',
            new_name='PlayerMatchStat',
        ),
    ]
