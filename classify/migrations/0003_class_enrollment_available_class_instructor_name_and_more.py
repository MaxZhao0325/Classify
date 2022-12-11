# Generated by Django 4.1.1 on 2022-10-24 15:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("classify", "0002_dept"),
    ]

    operations = [
        migrations.AddField(
            model_name="class",
            name="enrollment_available",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="class",
            name="instructor_name",
            field=models.CharField(default="NONE", max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="class",
            name="meetings_days",
            field=models.CharField(default="NONE", max_length=15),
            preserve_default=False,
        ),
    ]
