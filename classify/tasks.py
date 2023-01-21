from __future__ import absolute_import, unicode_literals
from celery import Celery
from celery import app, shared_task
import requests # pulling data
from bs4 import BeautifulSoup # xml parsing
from datetime import datetime # for time stamps
import json # exporting to files
from classify.models import Class, Dept, Profile, ProfileForm, Schedule, ScheduleForm, Friend_Request, Comment
from django.contrib.auth.models import User
from cs3240a17.settings import EMAIL_HOST_USER
from django.core.mail import send_mail
import lxml


from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

# scraping function
@shared_task
def hacker():

    #class_list=[]

    # subject_list=['AAS','ACCT','AIRS','ALAR','AMST','ANTH','APMA','ARAB','ARAD','ARAH','ARCH','ARCY','ARH','ARTH','ARTR','ARTS','ASL','ASTR',
    # 'BIMS',''
    # ]
    # Get all the subject types
    dept_results = Dept.objects.all()
    subject_list = dept_results.order_by('subject')
    count=0
    for subj in subject_list:
        print("starting " + str(subj.subject))
        # count the number of subjects that have been processed
        count+=1
        page_num = 1
        page=str(page_num)
        url_search='https://sisuva.admin.virginia.edu/psc/ihprd/UVSS/SA/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula.IScript_ClassSearch?institution=UVA01&term=1232&date_from=&date_thru=&subject=%s&subject_like=&catalog_nbr=&time_range=&days=&campus=&location=&x_acad_career=&acad_group=&rqmnt_designtn=&instruction_mode=&keyword=&class_nbr=&acad_org=&enrl_stat=&crse_attr=&crse_attr_value=&instructor_name=&session_code=&units=&page=%s' % (str(subj.subject), page)
        #Define header for the post request
        r = requests.get(url_search)
        data = r.json()

        while(data):
            for s in data:
                #change time scale to regular
                if (s["meetings"]):
                    start_time = s["meetings"][0]["start_time"][0:5]
                    end_time = s["meetings"][0]["end_time"][0:5]
                    meetings_days = s['meetings'][0]['days']
                    facility_description = s['meetings'][0]['facility_descr']
                else:
                    start_time=''
                    end_time=''
                    meetings_days=''
                    facility_description=''
                if(start_time!=""):
                    if(float(start_time)<10):
                        start_time = start_time[1:]
                    if(float(start_time)>=12):
                        if(float(start_time)>=13):
                            start_time = str("{:.2f}".format(float(start_time)-12))+"pm"
                        else:
                            start_time=start_time+"pm"
                    else:
                        start_time = start_time+"am"            
                if(end_time!=""):
                    if(float(end_time)<10):
                        end_time = end_time[1:]
                    if(float(end_time)>=12):
                        if(float(end_time)>=13):
                            end_time = str("{:.2f}".format(float(end_time)-12))+"pm"
                        else:
                            end_time=end_time+"pm"
                    else:
                        end_time = end_time+"am"

                instructor_name = s['instructors'][0]['name']
                instructor_email = s['instructors'][0]['email']
                course_number = s['class_nbr']
                semester_code = s['strm']
                course_section = s['class_section']
                subject = s['subject']
                catalog_number = s['catalog_nbr']
                description = s['descr']
                units = s['units']
                component = s['component']
                class_capacity = s['class_capacity']
                wait_list = s['wait_tot']
                wait_cap = s['wait_cap']
                enrollment_total = s['enrollment_total']
                enrollment_available = s['enrollment_available']
                enrollment_status = s['enrl_stat']
                enrl_stat_descr = str.upper(s['enrl_stat_descr'])
                topic = s['topic']
                
                class_to_update = Class(
                    instructor_name = instructor_name,
                    instructor_email = instructor_email,
                    course_number = course_number,
                    semester_code = semester_code,
                    course_section = course_section,
                    subject = subject,
                    catalog_number = catalog_number,
                    description = description,
                    units = units,
                    component = component,
                    class_capacity = class_capacity,
                    wait_list = wait_list,
                    wait_cap = wait_cap,
                    enrollment_total = enrollment_total,
                    enrollment_available = enrollment_available,
                    enrollment_status = enrollment_status,
                    enrl_stat_descr = enrl_stat_descr,
                    topic = topic,
                    meetings_days = meetings_days,
                    meetings_start_time = start_time,
                    meetings_end_time = end_time,
                    facility_description = facility_description,
                )

                # if the course is in the database, update it
                if (Class.objects.filter(course_number=course_number)):
                    # fetch the same course stored in the database
                    class_in_database = Class.objects.all().get(course_number=course_number)

                    # if the enrollment_status changes from Waitlist to Open, then send the email to all users who have that course in their shoppingcart.
                    if ((class_in_database.enrollment_status=='W' or class_in_database.enrollment_status=='C') and (class_to_update.enrollment_status=='O')):
                        subject='A course in your shoppingcart is open'
                        message=class_in_database.subject+class_in_database.catalog_number+'('+class_in_database.course_section+')'+' is open, you may want it.'
                        recipient_list=[]
                        namelist=""
                        for profile in Profile.objects.all():
                            # if the updated course is in user's favorite but not muted, send their message
                            if((profile.courses.filter(course_number=class_in_database.course_number)) and (class_in_database not in profile.muted_course.all())):
                                recipient_list.append(profile.user.email)
                                namelist+=" "
                                namelist+=str(profile.user.email)
                        if(recipient_list):
                            send_mail(subject, message, EMAIL_HOST_USER, recipient_list, fail_silently = False)
                            send_mail('recipient_list', message + namelist, EMAIL_HOST_USER, ['zhz990319@gmail.com'], fail_silently = False)

                    # if ((class_in_database.enrollment_status=='W' or class_in_database.enrollment_status=='C') and (class_to_update.enrollment_status=='O')):
                    #     subject='the course status changes'
                    #     message=class_in_database.subject+class_in_database.catalog_number+'('+class_in_database.course_section+')'+' is open, you may want it.'
                    #     send_mail(subject, message, EMAIL_HOST_USER, ['zhz990319@gmail.com'], fail_silently = False)

                    # if (class_to_update.wait_list>0 and class_to_update.enrollment_status=='O'):
                    #     subject='the course is open with wwaitlist'
                    #     message=class_in_database.subject+class_in_database.catalog_number+'('+class_in_database.course_section+')'+' is open, and there are people on waitlist.'
                    #     send_mail(subject, message, EMAIL_HOST_USER, ['zhz990319@gmail.com'], fail_silently = False)

                    # if they are the same, do not need to update the course info
                    # otherwise, update the course info
                    if(class_to_update.instructor_name != class_in_database.instructor_name):
                        class_in_database.instructor_name = class_to_update.instructor_name
                    if(class_to_update.instructor_email != class_in_database.instructor_email):
                        class_in_database.instructor_email = class_to_update.instructor_email
                    if(class_to_update.class_capacity != class_in_database.class_capacity):
                        class_in_database.class_capacity = class_to_update.class_capacity
                    if(class_to_update.wait_list != class_in_database.wait_list):
                        class_in_database.wait_list = class_to_update.wait_list
                    if(class_to_update.wait_cap != class_in_database.wait_cap):
                        class_in_database.wait_cap = class_to_update.wait_cap
                    if(class_to_update.enrollment_total != class_in_database.enrollment_total):
                        class_in_database.enrollment_total = class_to_update.enrollment_total
                    if(class_to_update.enrollment_available != class_in_database.enrollment_available):
                        class_in_database.enrollment_available = class_to_update.enrollment_available
                    if(class_to_update.enrollment_status != class_in_database.enrollment_status):
                        class_in_database.enrollment_status = class_to_update.enrollment_status
                    if(class_to_update.enrl_stat_descr != class_in_database.enrl_stat_descr):
                        class_in_database.enrl_stat_descr = class_to_update.enrl_stat_descr
                    if(class_to_update.topic != class_in_database.topic):
                        class_in_database.topic = class_to_update.topic
                    if(class_to_update.meetings_days != class_in_database.meetings_days):
                        class_in_database.meetings_days = class_to_update.meetings_days
                    if(class_to_update.meetings_start_time != class_in_database.meetings_start_time):
                        class_in_database.meetings_start_time = class_to_update.meetings_start_time
                    if(class_to_update.meetings_end_time != class_in_database.meetings_end_time):
                        class_in_database.meetings_end_time = class_to_update.meetings_end_time
                    if(class_to_update.facility_description != class_in_database.facility_description):
                        class_in_database.facility_description = class_to_update.facility_description
                    class_in_database.save()
                # if the course has never stored in the database before, store it
                else:
                    class_to_update.save()

            page_num+=1
            page=str(page_num)
            url_search='https://sisuva.admin.virginia.edu/psc/ihprd/UVSS/SA/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula.IScript_ClassSearch?institution=UVA01&term=1232&date_from=&date_thru=&subject=%s&subject_like=&catalog_nbr=&time_range=&days=&campus=&location=&x_acad_career=&acad_group=&rqmnt_designtn=&instruction_mode=&keyword=&class_nbr=&acad_org=&enrl_stat=&crse_attr=&crse_attr_value=&instructor_name=&session_code=&units=&page=%s' % (str(subj.subject), page)
            r = requests.get(url_search)
            data = r.json()
    print(count)

    #return save_function(class_list)

    # for p in Profile.objects.all():
    #     print(p.user.first_name+" favorite")
    #     for c in p.courses.all():
    #         print(c.subject+c.catalog_number+c.course_section)
    #     print(p.user.first_name+" mute")
    #     for d in p.muted_course.all():
    #         print(d.subject+d.catalog_number+d.course_section)
    #     print(p.user.first_name+" schedule")
    #     for d in p.schedule.courses.all():
    #         print(d.subject+d.catalog_number+d.course_section)
    #     print("end for " +p.user.first_name )

# from celery.schedules import crontab # scheduler
# # scheduled task execution
# app.conf.beat_schedule = {
#     # executes every 1 minute
#     'scraping-task-fifteen-min': {
#         'task': 'tasks.hacker',
#         'schedule': crontab(minute='*/15')
#     },
# }

# hacker()
