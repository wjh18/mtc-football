# Generated by Django 3.2.6 on 2021-08-24 16:55

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0009_auto_20210824_1237'),
    ]

    operations = [
        migrations.AddField(
            model_name='season',
            name='current_date',
            field=models.DateField(default=datetime.date(2021, 8, 29)),
        ),
    ]
