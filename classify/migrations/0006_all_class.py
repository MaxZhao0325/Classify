# Generated by Django 4.0.2 on 2022-10-31 03:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classify', '0005_class_course_number'),
    ]

    operations = [
        migrations.CreateModel(
            name='All_class',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course_number', models.IntegerField(default=0)),
                ('catalog_number', models.SlugField(max_length=12)),
                ('instructor_name', models.CharField(max_length=200)),
                ('name', models.CharField(max_length=200)),
                ('subject', models.CharField(max_length=4)),
                ('description', models.CharField(max_length=5000)),
                ('units', models.CharField(max_length=2)),
                ('enrollment_available', models.IntegerField(default=0)),
                ('class_capacity', models.IntegerField(default=0)),
                ('wait_list', models.IntegerField(default=0)),
                ('wait_cap', models.IntegerField(default=0)),
                ('meetings_days', models.CharField(max_length=15)),
            ],
        ),
    ]
