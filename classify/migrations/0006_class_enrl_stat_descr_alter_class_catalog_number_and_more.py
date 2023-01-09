# Generated by Django 4.0.2 on 2023-01-09 03:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classify', '0005_class_enrollment_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='class',
            name='enrl_stat_descr',
            field=models.CharField(default='', max_length=10),
        ),
        migrations.AlterField(
            model_name='class',
            name='catalog_number',
            field=models.CharField(default='', max_length=10),
        ),
        migrations.AlterField(
            model_name='class',
            name='course_section',
            field=models.CharField(default='', max_length=10),
        ),
        migrations.AlterField(
            model_name='class',
            name='description',
            field=models.CharField(default='', max_length=1000),
        ),
        migrations.AlterField(
            model_name='class',
            name='instructor_email',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='class',
            name='instructor_name',
            field=models.CharField(default='', max_length=100),
        ),
    ]