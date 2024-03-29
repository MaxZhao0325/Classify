# Generated by Django 4.0.2 on 2023-01-19 02:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classify', '0007_alter_dept_subject'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='muted_course',
            field=models.ManyToManyField(related_name='muted_courses', to='classify.Class'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='courses',
            field=models.ManyToManyField(related_name='favorite_courses', to='classify.Class'),
        ),
    ]
