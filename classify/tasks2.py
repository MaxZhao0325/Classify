import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cs3240a17.settings')  # replace 'myproject.settings' with your actual settings module
django.setup()

from classify.models import Class, Dept, Profile, ProfileForm, Schedule, ScheduleForm, Friend_Request, Comment
for profile in Profile.objects.all():
    print(profile.courses)

# Retrieve multiple instances
instances = Class.objects.filter(semester_code='1242')  # Retrieves all instances that match the filter

# Delete the instances
print(len(instances))