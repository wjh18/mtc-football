# Generated by Django 4.1.1 on 2022-10-06 02:42

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seasons', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='season',
            name='current_date',
            field=models.DateField(default=datetime.date(2022, 8, 29)),
        ),
        migrations.AlterField(
            model_name='season',
            name='start_date',
            field=models.DateField(default=datetime.date(2022, 8, 29)),
        ),
    ]
