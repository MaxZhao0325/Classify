from classify.models import Class, Dept, Profile, ProfileForm, Schedule, ScheduleForm, Friend_Request, Comment
for profile in Profile.objects.all():
    print(profile.courses)