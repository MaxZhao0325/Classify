# Generated by Django 4.0.2 on 2023-01-06 21:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classify', '0004_alter_comment_pub_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='class',
            name='enrollment_status',
            field=models.CharField(default='', max_length=5),
        ),
    ]
