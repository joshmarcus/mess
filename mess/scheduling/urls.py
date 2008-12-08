from django.conf.urls.defaults import *
from mess.scheduling.models import *

# commented out until there are actual views to point at -- 
# phantom urls wreak havoc with {% url %} and reverse()
urlpatterns = patterns('mess.scheduling.views',
    url(r'^task_list/(?P<date>\d{4}-\d+-\d+)$', 'task_list', name="task-list"),
    url(r'^task_list/$', 'task_list', name="task-list-today"),
    
    url(r'^open_task_list_month/(?P<date>\d{4}-\d+)$', 'open_task_list_month', name="open-task-list-month"),
    url(r'^open_task_list_month/$', 'open_task_list_month', name="open-task-list-current-month"),
    url(r'^open_task_list/(?P<date>\d{4}-\d+-\d+)$', 'open_task_list', name="open-task-list"),
    url(r'^open_task_list/$', 'open_task_list', name="open-task-list-today"),
    
    # url(r'^task_form/(?P<task_id>\d+)', 'task_form'),
    # url(r'^task_form/', 'task_form'),
    
    url(r'^schedule/(?P<date>\d{4}-\d+-\d+)', 'schedule', name="scheduling-schedule"),
    url(r'^schedule/', 'schedule', name="scheduling-schedule-today"),
    #url(r'^assign/', 'assign', name="scheduling-assign"),
    url(r'^timecard/', 'timecard', name="scheduling-timecard"),
    url(r'^jobs/$', 'jobs', name="scheduling-jobs"),
    url(r'^jobs/(?P<job_id>\d+)/$', 'job', name="job"),
    url(r'^jobs/(?P<job_id>\d+)/edit/$', 'job_edit', name="job-edit"),
    url(r'^jobs/add/$', 'job_edit', name="job-add"),
   
#    url(r'^daily.html', 'daliy'),
#    url(r'^weekly.html', 'weekly'),
#    url(r'^job_list.html', 'job_list'),
    url(r'^task/new/', 'add_task', name="add-task"),
    url(r'^task/update/(?P<object_id>\d+)', 'update_task', name="update-task"),
    url(r'^task/delete/(?P<object_id>\d+)', 'delete_task', name="del-task"),
    url(r'^worker-form$', 'worker_form', name='scheduling-worker-form'),
   
    #url(r'^task/(?P<task_id>\d+)/assign-to/(?P<member_id>\d+)', 'assign_task', name="assign-task")
)
