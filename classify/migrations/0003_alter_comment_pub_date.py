# Generated by Django 4.0.2 on 2023-01-06 20:49

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classify', '0002_alter_comment_pub_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2023, 1, 6, 20, 49, 16, 773883), verbose_name='date published'),
        ),
    ]
