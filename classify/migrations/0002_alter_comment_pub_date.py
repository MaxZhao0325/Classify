# Generated by Django 4.0.2 on 2023-01-06 20:49

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classify', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2023, 1, 6, 20, 49, 3, 580356), verbose_name='date published'),
        ),
    ]