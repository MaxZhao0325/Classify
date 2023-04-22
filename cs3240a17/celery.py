
from __future__ import absolute_import
import os
from celery import Celery

from celery.schedules import crontab # scheduler

# default django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cs3240a17.settings')

app = Celery('cs3240a17')

app.conf.timezone = 'UTC'

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

app.conf.beat_schedule = {
    # executes every 2 minute
    'scraping-task-10-min': {
        'task': 'classify.tasks.hacker',
        'schedule': crontab(minute='*/10'),
    },
    # executes every 15 minutes
    # 'scraping-task-fifteen-min': {
    #     'task': 'classify.tasks.hacker',
    #     'schedule': crontab(minute='*/15')
    # },
    # # executes daily at midnight
    # 'scraping-task-midnight-daily': {
    #     'task': 'tasks.hacker',
    #     'schedule': crontab(minute=0, hour=0)
    # }
}