from __future__ import absolute_import, unicode_literals
from celery import Celery
from celery import app, shared_task
import requests # pulling data
from bs4 import BeautifulSoup # xml parsing
from datetime import datetime # for time stamps
import json # exporting to files
from classify.models import Class, Dept, Profile, ProfileForm, Schedule, ScheduleForm, Friend_Request, Comment
import lxml


from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


# save function
@shared_task(serializer='json')
def save_function(class_list):
    # source = article_list[0]['source']
    # new_count = 0

    # error = True
    # try: 
    #     latest_article = News.objects.filter(source=source).order_by('-id')[0]
    #     # print(latest_article.published)
    #     print('var TestTest: ', latest_article, 'type: ', type(latest_article))
    # except Exception as e:
    #     print('Exception at latest_article: ')
    #     print(e)
    #     error = False
    #     pass
    # finally:
    #     # if the latest_article has an index out of range (nothing in model) it will fail
    #     # this catches failure so it passes the first if statement
        
    #     if error is not True:
    #         latest_article = None

    # with open('articles.txt', 'w') as outfile:
    #     json.dump(class_list, outfile)

    for r in class_list:

        class_to_update = Class(
            instructor_name = r['instructor_name'],
            instructor_email = r['instructor_email'],
            course_number = r['course_number'],
            semester_code = r['semester_code'],
            course_section = r['course_section'],
            subject = r['subject'],
            catalog_number = r['catalog_number'],
            description = r['description'],
            units = r['units'],
            component = r['component'],
            class_capacity = r['class_capacity'],
            wait_list = r['wait_list'],
            wait_cap = r['wait_cap'],
            enrollment_total = r['enrollment_total'],
            enrollment_available = r['enrollment_available'],
            enrollment_status = r['enrollment_status'],
            topic = r['topic'],
            meetings_days = r['meetings_days'],
            meetings_start_time = r['meetings_start_time'],
            meetings_end_time = r['meetings_end_time'],
            facility_description = r['facility_description'],
        )
        # if the course has never stored in the database before, store it
        if (Class.objects.filter(course_number=r['course_number'])):

            # fetch the same course stored in the database
            class_in_database = Class.objects.all().get(course_number=r['course_number'])
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
        else:
            class_to_update.save()
    # for article in article_list:

    #     # latest_article is None signifies empty DB
    #     if latest_article is None:
    #         try:
    #             News.objects.create(
    #                 title = article['title'],
    #                 link = article['link'],
                    
    #                 source = article['source']
    #             )
    #             new_count += 1
    #         except Exception as e:
    #             print('failed at latest_article is none')
    #             print(e)
    #             break
        
    #     # latest_article.published date < article['published']
    #     # halts the save, to avoid repetitive DB calls on already existing articles
        
    #     else:
    #         return print('news scraping failed')

    # logger.info(f'New articles: {new_count} articles(s) added.')
    # return print('finished')



# scraping function
@shared_task
def hacker():

    class_list=[]

    # subject_list=['AAS','ACCT','AIRS','ALAR','AMST','ANTH','APMA','ARAB','ARAD','ARAH','ARCH','ARCY','ARH','ARTH','ARTR','ARTS','ASL','ASTR',
    # 'BIMS',''
    # ]
    # Get all the subject types
    response = requests.get('http://luthers-list.herokuapp.com/api/deptlist/')
    subject_list = response.json()

    for subj in subject_list:
        page_num = 1
        page=str(page_num)
        url_search='https://sisuva.admin.virginia.edu/psc/ihprd/UVSS/SA/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula.IScript_ClassSearch?institution=UVA01&term=1232&date_from=&date_thru=&subject=%s&subject_like=&catalog_nbr=&time_range=&days=&campus=&location=&x_acad_career=&acad_group=&rqmnt_designtn=&instruction_mode=&keyword=&class_nbr=&acad_org=&enrl_stat=&crse_attr=&crse_attr_value=&instructor_name=&session_code=&units=&page=%s' % (subj['subject'], page)
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
                topic = s['topic']
                
                item = {
                    'instructor_name': instructor_name,
                    'instructor_email' : instructor_email,
                    'course_number' : course_number,
                    'semester_code' : semester_code,
                    'course_section' : course_section,
                    'subject' : subject,
                    'catalog_number' : catalog_number,
                    'description' : description,
                    'units' : units,
                    'component' : component,
                    'class_capacity' : class_capacity,
                    'wait_list' : wait_list,
                    'wait_cap' : wait_cap,
                    'enrollment_total' : enrollment_total,
                    'enrollment_available' : enrollment_available,
                    'enrollment_status' : enrollment_status,
                    'topic' : topic,
                    'meetings_days' : meetings_days,
                    'meetings_start_time' : start_time,
                    'meetings_end_time' : end_time,
                    'facility_description' : facility_description,
                }

                    # append my "article_list" with each "article" object
                class_list.append(item)

            page_num+=1
            page=str(page_num)
            url_search='https://sisuva.admin.virginia.edu/psc/ihprd/UVSS/SA/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula.IScript_ClassSearch?institution=UVA01&term=1232&date_from=&date_thru=&subject=%s&subject_like=&catalog_nbr=&time_range=&days=&campus=&location=&x_acad_career=&acad_group=&rqmnt_designtn=&instruction_mode=&keyword=&class_nbr=&acad_org=&enrl_stat=&crse_attr=&crse_attr_value=&instructor_name=&session_code=&units=&page=%s' % (subj, page)
            r = requests.get(url_search)
            data = r.json()

    return save_function(class_list)

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