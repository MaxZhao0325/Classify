from email import message
from http.client import HTTPResponse
from ssl import AlertDescription
import requests
from django.contrib import messages
# Create your views here.
from email.policy import HTTP
from select import select
from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Max

# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect ,Http404

from django.template import loader
from django.urls import reverse
from django.utils import timezone
from django.views import generic
from django.shortcuts import redirect

from classify.models import Class, Dept, Profile, ProfileForm, Schedule, ScheduleForm, Friend_Request, Comment
# import logging
# logger = logging.getLogger(__name__)
from django.conf import settings
import json
from django.contrib.auth.models import User
from django.utils import timezone
import datetime

def search(request):
    if 'q' in request.GET:
        message = 'You submitted: %r' % request.GET['q']
    else:
        message = 'You submitted nothing!'

    return HttpResponse(message)

# the user does not have to login in order to search or browse the courses
def index(request):
    isSearchError = False; # used to show an error if the user improperly searches
    typeOfError = '' # used to show the type of the error

    # Get the list of departments
    dept_results = {}
    # response = requests.get('http://luthers-list.herokuapp.com/api/deptlist/')
    # data = response.json()
    
    dept_results = Dept.objects.all()

    deptlist = dept_results.order_by('subject')
    query_results = {}
    query_results_classified ={}
    semester_list=["1232,1238,1242"]
    
    # deal with the condition when user trys to add a course to the shoppingcart
    # if the user clicks on star, then do not clear the Class database 
    if request.method == "POST" and request.POST.get("course_pk") and request.POST.get("semester_code"):
        # if the user wants to use the shoppingcart but did not login, redirect to login page
        if(not request.user.is_authenticated):
            return redirect("/accounts/google/login/")
        course_id = request.POST.get("course_pk")
        semester_code = request.POST.get("semester_code")
        course = Class.objects.get(course_number = course_id, semester_code=semester_code)
        request.user.profile.courses.add(course)
        message_display = course.subject+course.catalog_number+"("+course.course_section+")"
        messages.success(request,(f'{message_display} has been added to your Favorited Classes.'))
        # after user just used the shoppingcart, fetch the last department viewed by the user
        subject_sq = request.session['subject_sq']
        cat_num_sq = request.session['cat_num_sq']
        course_num_sq = request.session['course_num_sq']
        units_sq = request.session['units_sq']
        component_sq = request.session['component_sq']
        status_sq = request.session['status_sq']
        semester_code = request.session['semester_code']
        semester = request.session['semester']
        attribute = request.session['attribute']
        
    else:
    # if not the case when the user trys to add a course to the shoppingcart, reload the page with new department database
        # the default semester code
        semester_code = '1242'
        semester = 'Spring2024'
        # first check if the user selects a semester_code that is different from the current semester
        if(request.POST.get('semester_search')):
            if(request.POST.get('semester_search')=='Spring2023'):
                semester_code = '1232'
                semester='Spring2023'
            if(request.POST.get('semester_search')=='Fall2023'):
                semester_code = '1238'
                semester='Fall2023'

        # second check if there is valid value for the search bar
        subject_sq = request.POST.get('subject_search', None)
        cat_num_sq = request.POST.get('cat_num_search', None)
        course_num_sq = request.POST.get('course_num_search', None)
        units_sq = request.POST.get('units_search', None)
        component_sq = request.POST.get('component_search', None)
        status_sq = request.POST.get('status_search', None)
        attribute = request.POST.get('attribute_search', None)

        if(subject_sq or component_sq or cat_num_sq or course_num_sq or status_sq):
            if(subject_sq):
                subject_sq = str.upper(subject_sq)
            if(component_sq):
                component_sq = str.upper(component_sq)
            if(status_sq):
                status_sq = str.upper(status_sq)

            #  check searching bar to see if it is a valid search
            # early error handling - these will prevent results from being returned if search is not valid
            if subject_sq and subject_sq!='' and (len(subject_sq) > 4 or 0 < len(subject_sq) < 2):
                isSearchError = True
                typeOfError = 'Your subject code is invalid. Please enter a valid code (e.g. "APMA").'
            elif cat_num_sq and cat_num_sq!='' and (not cat_num_sq.isnumeric()):
                isSearchError = True
                typeOfError = 'Your catalog number is invalid. Please enter a valid number (e.g. "3240").'
            elif course_num_sq and course_num_sq!='' and (not course_num_sq.isnumeric()):
                isSearchError = True
                typeOfError = 'Your course number is invalid. Please enter a valid number (e.g. "12320").'

        # immediately returns some errors earlier, if there is no chance of a result being returned
        if isSearchError:
            messages.error(request, typeOfError)
            return redirect('/')

        # first check if the user pushes the button of a dept name
        if(not subject_sq and not cat_num_sq and not course_num_sq and not units_sq and not component_sq and not status_sq):
            for dept in dept_results:
                dept_string = dept.subject
                if not subject_sq:
                    subject_sq = request.POST.get(dept_string, None)
            if(subject_sq):
                subject_sq = str.upper(str(subject_sq))


        # if the subject searched is not searched before, then add course classes to the database
        # if 'stored_subject' not in request.session:
        #     request.session['stored_subject']=[]

        # if the department is first time viewed, add that department to the session and store the course data for that department
        # if subject_sq is not None and subject_sq != '' and subject_sq not in request.session['stored_subject']:
        #     request.session['stored_subject'].append(subject_sq)
        #     response = requests.get('http://luthers-list.herokuapp.com/api/dept/%s/' % subject_sq)
        #     data = response.json()
        #     results = data

        #     for r in results:
        #         # convert the start_time and end_time into readable manner
        #         if (r["meetings"]):
        #             start_time = r["meetings"][0]["start_time"][0:5]
        #             end_time = r["meetings"][0]["end_time"][0:5]
        #             meeting_days = r['meetings'][0]['days']
        #             facility_description = r['meetings'][0]['facility_description']
        #         else:
        #             start_time=''
        #             end_time=''
        #             meeting_days=''
        #             facility_description=''
        #         if(start_time!=""):
        #             if(float(start_time)<10):
        #                 start_time = start_time[1:]
        #             if(float(start_time)>=12):
        #                 if(float(start_time)>=13):
        #                     start_time = str("{:.2f}".format(float(start_time)-12))+"pm"
        #                 else:
        #                     start_time=start_time+"pm"
        #             else:
        #                 start_time = start_time+"am"
                
        #         if(end_time!=""):
        #             if(float(end_time)<10):
        #                 end_time = end_time[1:]
        #             if(float(end_time)>=12):
        #                 if(float(end_time)>=13):
        #                     end_time = str("{:.2f}".format(float(end_time)-12))+"pm"
        #                 else:
        #                     end_time=end_time+"pm"
        #             else:
        #                 end_time = end_time+"am"
                
        #         result_info = Class(
        #             instructor_name = r['instructor']['name'],
        #             instructor_email = r['instructor']['email'],
        #             course_number = r['course_number'],
        #             semester_code = r['semester_code'],
        #             course_section = r['course_section'],
        #             subject = r['subject'],
        #             catalog_number = r['catalog_number'],
        #             description = r['description'],
        #             units = r['units'],
        #             component = r['component'],
        #             class_capacity = r['class_capacity'],
        #             wait_list = r['wait_list'],
        #             wait_cap = r['wait_cap'],
        #             enrollment_total = r['enrollment_total'],
        #             enrollment_available = r['enrollment_available'],
        #             topic = r['topic'],
        #             meetings_days = meeting_days,
        #             meetings_start_time = start_time,
        #             meetings_end_time = end_time,
        #             facility_description = facility_description,
        #     )
        #         result_info.save()
        # # remove potential duplicates for classes in the database
        # for duplicates in Class.objects.values("course_number").annotate(
        #         records=Count("course_number")
        #     ).filter(records__gt=1):
        #     for tag in Class.objects.filter(course_number=duplicates["course_number"])[1:]:
        #         tag.delete()


        # this session stores all search informations of the last view so that the user will be back to the last page after add a course to shoppingcart
        request.session['subject_sq']=subject_sq
        request.session['cat_num_sq']=cat_num_sq
        request.session['course_num_sq']=course_num_sq
        request.session['units_sq']=units_sq
        request.session['component_sq']=component_sq
        request.session['status_sq']=status_sq
        request.session['semester_code']=semester_code
        request.session['semester']=semester
        request.session['attribute']=attribute

    attribute_map = {'Artistic, Interpretive, Phil': 'AIP',"Chem/Math/Physical Universe":"CMP",'Cultures/Societies World':'CSW',"First Writing":'R21C1','Historical Perspective':'HP','Living Systems':'LS', 'Public Interest Technology':'PIT', 'Quantif, Comptutation, Data an':'QCD', 'Science & Society':'SS', 'Second Writing':'R21C2', 'Social & Economic Systems':'SES','World Language':'WL'}
    if(attribute):
        attribute = attribute_map[attribute]
    if(subject_sq or cat_num_sq or course_num_sq or units_sq or component_sq or status_sq or attribute):
        query_results = Class.objects
        # only display the course for current searching semester
        query_results = query_results.filter(semester_code=semester_code)
        if(subject_sq):
            query_results = query_results.filter(subject=subject_sq)
            if(not query_results):
                messages.error(request, 'No results found.')
                return redirect('/')
        if(cat_num_sq):
            query_results = query_results.filter(catalog_number=cat_num_sq)
            if(not query_results):
                messages.error(request, 'No results found.')
                return redirect('/')
        if(course_num_sq):
            query_results = query_results.filter(course_number=course_num_sq)
            if(not query_results):
                messages.error(request, 'No results found.')
                return redirect('/')
        if(units_sq):
            query_results = query_results.filter(units=units_sq)
            if(not query_results):
                messages.error(request, 'No results found.')
                return redirect('/')
        if(component_sq):
            query_results = query_results.filter(component=component_sq)
            if(not query_results):
                messages.error(request, 'No results found.')
                return redirect('/')
        if(status_sq):
            query_results = query_results.filter(enrl_stat_descr=status_sq)
            if(not query_results):
                messages.error(request, 'No results found.')
                return redirect('/')
        if(attribute):
            query_results = query_results.filter(course_attribute__icontains=attribute)
            if(not query_results):
                messages.error(request, 'No results found.')
                return redirect('/')
        query_results = query_results.order_by('subject','catalog_number','course_section')

        # classify the classes into dept + catalog number (cs3240) so that the index page can display as such
        for course in query_results:
            subject = course.subject
            catalog = course.catalog_number
            group_name=subject+catalog
            # only display courses in the most recent semester
            query_results_classified[group_name]=query_results.filter(subject=subject, catalog_number=catalog)

    # if(subject_sq and cat_num_sq):
    #     query_results = Class.objects.filter(subject=subject_sq, catalog_number=cat_num_sq).order_by('id')
    #     if(not query_results):
    #         messages.error(request, 'No results found.')
    #         return redirect('/classify')
    # elif(subject_sq):
    #     query_results = Class.objects.filter(subject=subject_sq).order_by('id')
    #     if(not query_results):
    #         messages.error(request, 'No results found.')
    #         return redirect('/classify')
    # elif(cat_num_sq):
    #     query_results = Class.objects.filter(catalog_number=cat_num_sq).order_by('subject')
    #     if(not query_results):
    #         messages.error(request, 'No results found.')
    #         return redirect('/classify')
        
    return render(request, 'classify/index.html', {
        # map feature
        #"google_api_key": settings.GOOGLE_API_KEY,
        "query_results": query_results,
        "query_results_classified": query_results_classified,
        'deptlist': deptlist,
        'semester':semester,
    })


def user(request):
    if (request.user.is_authenticated):
        schedule = ScheduleForm(instance=request.user.profile.schedule)
        profile = ProfileForm(instance=request.user.profile)

        # if the delete_all button is clicked, delete all courses in the shoppingcart and the schedule
        if request.method == 'POST' and request.POST.get('delete_all'):
            for course in request.user.profile.courses.all():
                request.user.profile.courses.remove(course)
            messages.success(request, 'All your courses has been deleted from your Favorited Classes.')
            return redirect('/user')

        # if the user tries to delete a course from the shopping cart, fetch the course by its course_number and delete it from user's shopping cart.
        if request.method == 'POST' and request.POST.get('delete_course') and request.POST.get('semester_code'):
            CourseNumToDelete = request.POST.get('delete_course')
            semester_code = request.POST.get('semester_code')
            # User remove instead of delete to remove a course from the user profile without deleting the course itself in the Class model
            CourseToDelete = request.user.profile.courses.all().get(course_number=CourseNumToDelete, semester_code=semester_code)
            # remove the course from both shoppingcart and the schedule
            request.user.profile.courses.remove(CourseToDelete)
            request.user.profile.schedule.courses.remove(CourseToDelete)
            messages.success(request, (f'{CourseToDelete.subject}{CourseToDelete.catalog_number} has been deleted from your Favorited Classes and your Schedule.'))
            # CourseToDelete.save()
            return redirect('/user')

        conflict = False
        # if the user adds a class to the schedule, add that class to the user's schedule model
        if request.method == 'POST' and request.POST.get('add_to_schedule') and request.POST.get('semester_code'):
            CourseNumToAdd = request.POST.get('add_to_schedule')
            semester_code = request.POST.get('semester_code')
            CourseToAdd = request.user.profile.courses.all().get(course_number=CourseNumToAdd, semester_code=semester_code)
            # if a course in the schedule conflicts with this one, it cannot be added
            # if this course already exists in the schedule at a different time, it cannot be added (i.e. cannot enroll in two sections)
            meetings_days = CourseToAdd.meetings_days
            meetings_start_time = CourseToAdd.meetings_start_time
            for course in request.user.profile.schedule.courses.all():
                # no same course
                if((CourseToAdd.subject == course.subject) and (CourseToAdd.catalog_number == course.catalog_number) and (CourseToAdd.component == course.component) and (CourseToAdd.semester_code == course.semester_code)):
                    messages.error(request, (f'{CourseToAdd.subject}{CourseToAdd.catalog_number} is already in your Schedule.'))
                    conflict = True
                    break
                # no same time
                else:
                    if((CourseToAdd.meetings_days != "-") and (course.meetings_days != "-")):
                        conflict = conflict_check(CourseToAdd, course)
                        if(conflict):
                            messages.error(request, (f'{CourseToAdd.subject}{CourseToAdd.catalog_number} has a time conflict with {course.subject}{course.catalog_number} in your Schedule.'))
                            break
            if not conflict:
                messages.success(request, (f'{CourseToAdd.subject}{CourseToAdd.catalog_number} added to your schedule'))
                request.user.profile.schedule.courses.add(CourseToAdd)
        class_list = request.user.profile.courses.order_by("subject", "catalog_number", "course_section")

        # get the list of muted classes for the user
        muted_course = request.user.profile.muted_course.all()

        semester_list={1232:'Spring2023', 1238:'Fall2023', 1242:'Spring2024'}
        return render(request, 'classify/user.html', {"user":request.user, "profile":profile, "schedule":schedule, "conflict":conflict, "class_list": class_list, "muted_course": muted_course, "semester_list":semester_list})
    else:
        return redirect("/accounts/google/login/")

# determine if two courses conflict
def conflict_check(course_one, course_two):
    meetings_days_one = course_one.meetings_days
    meetings_days_two = course_two.meetings_days
    conflict = False
    if(("Mo" in meetings_days_one) and ("Mo" in meetings_days_two)):
        conflict = conflict or conflict_on_day(course_one, course_two)
    if(("Tu" in meetings_days_one) and ("Tu" in meetings_days_two)):
        conflict = conflict or conflict_on_day(course_one, course_two)
    if(("We" in meetings_days_one) and ("We" in meetings_days_two)):
        conflict = conflict or conflict_on_day(course_one, course_two)
    if(("Th" in meetings_days_one) and ("Th" in meetings_days_two)):
        conflict = conflict or conflict_on_day(course_one, course_two)
    if(("Fr" in meetings_days_one) and ("Fr" in meetings_days_two)):
        conflict = conflict or conflict_on_day(course_one, course_two)
    return conflict

# determine if two courses on the same day conflict
def conflict_on_day(course_one, course_two):
    #Get strings of start and end times
    meetings_start_one = course_one.meetings_start_time
    meetings_end_one = course_one.meetings_end_time
    meetings_start_two = course_two.meetings_start_time
    meetings_end_two = course_two.meetings_end_time

    integer_start_one = time_to_float(meetings_start_one)
    integer_end_one = time_to_float(meetings_end_one)
    integer_start_two = time_to_float(meetings_start_two)
    integer_end_two = time_to_float(meetings_end_two)

    #Conflict if start_two <= end_one <= end_two (I.e. class one ends during class two)
    if(integer_end_one >= integer_start_two and integer_end_one <= integer_end_two):
        return True
    #Conflict if start_one <= end_two <= end_one (I.e. class two ends during class one)
    if(integer_end_two >= integer_start_one and integer_end_two <= integer_end_one):
        return True
    return False

# Turns a string of format 11.00am into a float 11.00 or 1.00 pm into 13
def time_to_float(time_string):
    time_float = float(time_string[:len(time_string)-2])
    #Add 12 if PM, but not if 12 PM
    if("pm" in time_string and "12" not in time_string[:2]):
        time_float += 12
    #Subtract 12 if 12 AM. Possibly an astronomy lab could happen near midnight, still need comparison
    if("am" in time_string and "12" in time_string[:2]):
        time_float -= 12
    return time_float

# Get the time_float of a course start time
def get_time_float_start(course):
    return time_to_float(course.meetings_start_time)

# show the schedule of the current user
def schedule(request):
    if (request.user.is_authenticated):

        # if clear_all_schedule is clicked, remove all courses from user's scheduel
        if request.method == 'POST' and request.POST.get('delete_all_schedule'):
            for course in request.user.profile.schedule.courses.all():
                request.user.profile.schedule.courses.remove(course)
            messages.success(request, 'All your courses has been deleted from your Schedule.')
            return redirect('/user/schedule')

        # if the user tries to delete a course from the schedule, access below
        if request.method == 'POST' and request.POST.get('delete_from_schedule') and request.POST.get('semester_code'):
            CourseNumToDelete = request.POST.get('delete_from_schedule')
            semester_code = request.POST.get('semester_code')
            print(CourseNumToDelete, semester_code)
            CourseToDelete = request.user.profile.schedule.courses.all().get(course_number=CourseNumToDelete, semester_code=semester_code)
            # using remove for manytomany relationship can remove the object from somewhere without deleting itself
            request.user.profile.schedule.courses.remove(CourseToDelete)
            messages.success(request, (f'{CourseToDelete.subject}{CourseToDelete.catalog_number} has been deleted from your Schedule.'))
            return redirect('/user/schedule')

        # if the user tries to add a course from the schedule, access below
        if request.method == 'POST' and request.POST.get('add_to_schedule') and request.POST.get('semester_code'):
            CourseNumToAdd = request.POST.get('add_to_schedule')
            semester_code = request.POST.get('semester_code')
            CourseToAdd = request.user.profile.courses.all().get(course_number=CourseNumToAdd, semester_code=semester_code)
            conflict=False
            # if a course in the schedule conflicts with this one, it cannot be added
            # if this course already exists in the schedule at a different time, it cannot be added (i.e. cannot enroll in two sections)
            for course in request.user.profile.schedule.courses.all():
                # no same course
                if((CourseToAdd.subject == course.subject) and (CourseToAdd.catalog_number == course.catalog_number) and (CourseToAdd.component == course.component) and (CourseToAdd.semester_code == course.semester_code)):
                    messages.error(request, (f'{CourseToAdd.subject}{CourseToAdd.catalog_number} is already in your Schedule.'))
                    conflict = True
                    break
                # no same time
                else:
                    if((CourseToAdd.meetings_days != "-") and (course.meetings_days != "-")):
                        conflict = conflict_check(CourseToAdd, course)
                        if(conflict):
                            messages.error(request, (f'{CourseToAdd.subject}{CourseToAdd.catalog_number} has a time conflict with {course.subject}{course.catalog_number} in your Schedule.'))
                            break
            if not conflict:
                messages.success(request, (f'{CourseToAdd.subject}{CourseToAdd.catalog_number} added to your schedule'))
                request.user.profile.schedule.courses.add(CourseToAdd)
            return redirect('/user/schedule')
        
        # Put the courses into the correct days, so that the html file can access them
        monday_courses = []
        tuesday_courses = []
        wednesday_courses = []
        thursday_courses = []
        friday_courses = []
        other_courses = []
        for course in request.user.profile.schedule.courses.all():
            if "Mo" in course.meetings_days:
                monday_courses.append(course)
            if "Tu" in course.meetings_days:
                tuesday_courses.append(course)
            if "We" in course.meetings_days:
                wednesday_courses.append(course)
            if "Th" in course.meetings_days:
                thursday_courses.append(course)
            if "Fr" in course.meetings_days:
                friday_courses.append(course)
            if "Mo" not in course.meetings_days:
                if "Tu" not in course.meetings_days:
                    if "We" not in course.meetings_days:
                        if "Th" not in course.meetings_days:
                            if "Fr" not in course.meetings_days:
                                other_courses.append(course)

        # Sort the list of days
        monday_courses.sort(key=get_time_float_start)
        tuesday_courses.sort(key=get_time_float_start)
        wednesday_courses.sort(key=get_time_float_start)
        thursday_courses.sort(key=get_time_float_start)
        friday_courses.sort(key=get_time_float_start)
        # Don't sort other_courses I guess?

        # get all comments that belong to my schedule
        comments = Comment.objects.filter(schedule=request.user.profile.schedule)

        # if the user votes up, then the ups for that comment +1, and then add the current user to the voted_user list of the comment to prevent second vote
        if request.POST.get('comment_up') or request.POST.get('comment_down'):
            if(request.POST.get('comment_up')):
                comment_up = request.POST.get('comment_up')
                comment = Comment.objects.get(id=comment_up)
                if request.user not in comment.voted_users.all():
                    comment.ups+=1
            elif(request.POST.get('comment_down')):
                comment_down = request.POST.get('comment_down')
                comment = Comment.objects.get(id=comment_down)
                if request.user not in comment.voted_users.all():
                    comment.downs+=1            
            if request.user not in comment.voted_users.all():
                comment.voted_users.add(request.user)
            comment.save()

        # similar code to the above for if a user upvotes or downvotes the schedule as a whole
        if request.POST.get('schedule_up') or request.POST.get('schedule_down'):
            if(request.POST.get('schedule_up')):
                schedule_up = request.POST.get('schedule_up')
                schedule = request.user.profile.schedule
                if request.user not in schedule.voted_users.all():
                    schedule.ups+=1
            elif(request.POST.get('schedule_down')):
                schedule_down = request.POST.get('schedule_down')
                schedule = request.user.profile.schedule
                if request.user not in schedule.voted_users.all():
                    schedule.downs+=1            
            if request.user not in schedule.voted_users.all():
                schedule.voted_users.add(request.user)
            schedule.save()
        
        schedule_courses = request.user.profile.schedule.courses.all().order_by("subject","catalog_number","course_section")
        favorite_courses = request.user.profile.courses.all().order_by("subject","catalog_number","course_section")
        for course in schedule_courses:
            print(course.subject, course.catalog_number)
        return render(request, 'classify/schedule.html', {"favorite_courses":favorite_courses, "schedule_courses":schedule_courses, "user":request.user, "schedule": request.user.profile.schedule, 'comments':comments, "monday_courses": monday_courses, "tuesday_courses": tuesday_courses, "wednesday_courses": wednesday_courses, "thursday_courses": thursday_courses, "friday_courses": friday_courses, "other_courses": other_courses})
    else:
        return redirect("/accounts/google/login/")

# implement a map feature where the user can check the position of a course on google map.
# Handles directions from Google by implementing googleapis jason map data

# def Directions(*args, **kwargs):

#     current_position = kwargs.get("current_position")
#     target_position = kwargs.get("target_position")

#     find_current_position_id = requests.get(
#         'https://maps.googleapis.com/maps/api/place/findplacefromtext/json?',
#         params={
#             'input': current_position,
#             'inputtype' : 'textquery',
#             "key": settings.GOOGLE_API_KEY
#         })
#     if find_current_position_id.json()["status"] == "OK":
#         current_position_id = find_current_position_id.json()["candidates"][0]["place_id"]

#     find_target_position_id = requests.get(
#         'https://maps.googleapis.com/maps/api/place/findplacefromtext/json?',
#         params={
#             'input': target_position,
#             'inputtype' : 'textquery',
#             "key": settings.GOOGLE_API_KEY
#         })
#     if find_target_position_id.json()["status"] == "OK":
#         target_position_id = find_target_position_id.json()["candidates"][0]["place_id"]

#     result = requests.get(
#         'https://maps.googleapis.com/maps/api/directions/json?',
#          params={
#          'origin': 'place_id:'+current_position_id,
#          'destination': 'place_id:'+target_position_id,
#          'mode' : 'walking',
#          "key": settings.GOOGLE_API_KEY
#          })

#     directions = result.json()

#     if directions["status"] == "OK":

#         route = directions["routes"][0]["legs"][0]
#         origin = current_position
#         destination = target_position
#         distance = route["distance"]["text"]
#         duration = route["duration"]["text"]

#         # steps = [
#         #     [
#         #         s["distance"]["text"],
#         #         s["duration"]["text"],
#         #         s["html_instructions"],

#         #     ]
#         #     for s in route["steps"]]

#     return {
#         "origin": origin,
#         "destination": destination,
#         "distance": distance,
#         "duration": duration,
#         # "steps": steps
#         }

# # define the map
# def map(request):
#     if(request.GET.get("current_position")):
#         current_position = request.GET.get("current_position")
#         target_position = request.GET.get("target_position")
#         directions = Directions(
#             current_position= current_position,
#             target_position=target_position,
#             )

#         context = {
#         "google_api_key": settings.GOOGLE_API_KEY,
#         "origin": current_position,
#         "destination": target_position,
#         "directions": directions,

#         }
#         return render(request, 'classify/map.html', context)   
    
#     messages.warning(request, "You must choose a course to show its location.")
#     return redirect ("/classify")  

# define the user friend request
def send_friend_request(request, userID):
    from_user = request.user
    to_user = User.objects.get(id=userID)
    if(to_user in from_user.profile.friends.all()):
        messages.error(request, 'You are already friends.')
        return redirect('/user/friend_search')
    friend_request, created = Friend_Request.objects.get_or_create(from_user=from_user, to_user=to_user)
    if created:
        messages.success(request, f'A friend request to {to_user} has been sent.')
    else:
        messages.warning(request, f'A friend request to {to_user} has already been sent.')
    return redirect('/user/friend_search')

# accept the user friend request
def accept_friend_request(request, requestID):
    friend_request = Friend_Request.objects.get(id=requestID)
    # if the current user is the right target and both sides are not friends for now, then add them to friends
    if friend_request.to_user == request.user and friend_request.from_user not in request.user.profile.friends.all():
        friend_request.to_user.profile.friends.add(friend_request.from_user)
        friend_request.from_user.profile.friends.add(friend_request.to_user)
        # delete friend request alfter adding friends
        friend_request.delete()
        messages.success(request, f'Friend request accepted.')
    else:
        friend_request.delete()
        messages.error(request, f'You are already friends!')
    return redirect('/user/friends')

# decline the user friend request
def decline_friend_request(request, requestID):
    friend_request = Friend_Request.objects.get(id=requestID)
    # simply delete the friend request
    friend_request.delete()
    messages.success(request, f'Friend request declined.')
    return redirect('/user/friends')

# mute notification of a certain class
def mute_notification(request, userID, course_number, semester_code):
    user = User.objects.get(id=userID)
    class_to_mute = Class.objects.get(course_number=course_number, semester_code=semester_code)
    if(class_to_mute not in user.profile.muted_course.all()):
        user.profile.muted_course.add(class_to_mute)
    messages.success(request, f'You have muted {class_to_mute.subject} {class_to_mute.catalog_number}-{class_to_mute.course_section}.')
    return redirect('/user')

# unmute notification of a certain class
def unmute_notification(request, userID, course_number, semester_code):
    user = User.objects.get(id=userID)
    class_to_unmute = Class.objects.get(course_number=course_number, semester_code=semester_code)
    if(class_to_unmute in user.profile.muted_course.all()):
        user.profile.muted_course.remove(class_to_unmute)
    messages.success(request, f'You have unmuted {class_to_unmute.subject} {class_to_unmute.catalog_number}-{class_to_unmute.course_section}.')
    return redirect('/user')
    
# open friend search page
def friend_search(request):
    if (request.user.is_authenticated):
        search = request.POST.get('friend_search')
        if(search!=''):        
            return render(request, 'classify/friend_search.html', {'user':request.user, 'users':User.objects.filter(username=search)})
        else:
            return render(request, 'classify/friend_search.html', {'user':request.user})
    else:
        return redirect("/accounts/google/login/")

# page for display friends and their schedules
def friends(request):
    if (request.user.is_authenticated):
        # if a request of friends delete
        if request.method == 'POST' and request.POST.get('delete_friend'):
            FriendIDToDelete = request.POST.get('delete_friend')
            FriendToDelete = User.objects.get(id=FriendIDToDelete)        
            # delete the friend from user side
            request.user.profile.friends.remove(FriendToDelete)
            # delete the user from his/her friends' side
            FriendToDelete.profile.friends.remove(request.user)
            messages.success(request, (f'You have removed {FriendToDelete} from your Friends list.'))
            return redirect('/user/friends')

        # process if the user check the schedule of a friend or the user comments
        if request.method == 'POST' and (request.POST.get('check_friend_schedule') or request.POST.get('friend_id')):
            # get user id from different situations
            if request.POST.get('check_friend_schedule'):
                friend_id = request.POST.get('check_friend_schedule')
            else:
                friend_id = request.POST.get('friend_id')
            friend = User.objects.get(id=friend_id)
            friend_schedule=friend.profile.schedule

            # if the user comments, create a new comment object and add that to the friend's schedule
            if request.POST.get('comment'):
                content = request.POST.get('comment')
                comment = Comment(
                    schedule = friend_schedule,
                    content = content,
                    pub_date = timezone.now(),
                )
                comment.save()
                
            # get all comments of a friend's schedule
            comments = Comment.objects.filter(schedule=friend_schedule)

            # if the user votes up, then the ups for that comment +1, and then add the current user to the voted_user list of the comment to prevent second vote
            if request.POST.get('comment_up') or request.POST.get('comment_down'):
                if(request.POST.get('comment_up')):
                    comment_up = request.POST.get('comment_up')
                    comment = Comment.objects.get(id=comment_up)
                    if request.user not in comment.voted_users.all():
                        comment.ups+=1
                elif(request.POST.get('comment_down')):
                    comment_down = request.POST.get('comment_down')
                    comment = Comment.objects.get(id=comment_down)
                    if request.user not in comment.voted_users.all():
                        comment.downs+=1            
                if request.user not in comment.voted_users.all():
                    comment.voted_users.add(request.user)
                comment.save()

            # remove potential duplicates for comments in the database
            for duplicates in comments.values("content").annotate(records=Count("content")).filter(records__gt=1):
                for tag in comments.filter(content=duplicates["content"])[1:]:
                    tag.delete()
            # order the comments by its publishing time
            comments=comments.order_by('pub_date')

            # similar code to the above for if a user upvotes or downvotes the schedule as a whole
            if request.POST.get('schedule_up') or request.POST.get('schedule_down'):
                if(request.POST.get('schedule_up')):
                    schedule_up = request.POST.get('schedule_up')
                    if request.user not in friend_schedule.voted_users.all():
                        friend_schedule.ups+=1
                elif(request.POST.get('schedule_down')):
                    schedule_down = request.POST.get('schedule_down')
                    if request.user not in friend_schedule.voted_users.all():
                        friend_schedule.downs+=1            
                if request.user not in friend_schedule.voted_users.all():
                    friend_schedule.voted_users.add(request.user)
                friend_schedule.save()

            # Put the courses into the correct days, so that the html file can access them
            monday_courses = []
            tuesday_courses = []
            wednesday_courses = []
            thursday_courses = []
            friday_courses = []
            other_courses = []
            for course in friend_schedule.courses.all():
                if "Mo" in course.meetings_days:
                    monday_courses.append(course)
                if "Tu" in course.meetings_days:
                    tuesday_courses.append(course)
                if "We" in course.meetings_days:
                    wednesday_courses.append(course)
                if "Th" in course.meetings_days:
                    thursday_courses.append(course)
                if "Fr" in course.meetings_days:
                    friday_courses.append(course)
                if "Mo" not in course.meetings_days:
                    if "Tu" not in course.meetings_days:
                        if "We" not in course.meetings_days:
                            if "Th" not in course.meetings_days:
                                if "Fr" not in course.meetings_days:
                                    other_courses.append(course)
            # Sort the list of days
            monday_courses.sort(key=get_time_float_start)
            tuesday_courses.sort(key=get_time_float_start)
            wednesday_courses.sort(key=get_time_float_start)
            thursday_courses.sort(key=get_time_float_start)
            friday_courses.sort(key=get_time_float_start)
            courses = friend.profile.schedule.courses.all().order_by("subject","catalog_number","course_section")
            return render(request, 'classify/friends.html', {'courses':courses, 'user':request.user, 'friend':friend, 'comments':comments, 'friend_request': Friend_Request.objects.filter(to_user=request.user), 'friend_schedule':friend_schedule, "monday_courses": monday_courses, "tuesday_courses": tuesday_courses, "wednesday_courses": wednesday_courses, "thursday_courses": thursday_courses, "friday_courses": friday_courses, "other_courses": other_courses})
        else:
            return render(request, 'classify/friends.html', {'user':request.user, 'friend_request': Friend_Request.objects.filter(to_user=request.user)})
    else:
        return redirect("/accounts/google/login/")

# for google console authentication
def google_console(request):
    return render(request, 'classify/googlef8e431e468b388bf.html')

# for detectify
def detectify(request):
    return render(request, 'download.txt')

# for wechat authentication
def wechat(request):
    return render(request, '8426e94a3d6b088bc899896481600a84.txt')