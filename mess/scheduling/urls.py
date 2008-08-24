from django.conf.urls.defaults import *
from mess.scheduling.models import *

# commented out until there are actual views to point at -- 
# phantom urls wreak havoc with {% url %} and reverse()
urlpatterns = patterns('mess.scheduling.views',
    url(r'^task_list/(?P<date>\d{4}-\d+-\d+)$', 'task_list', name="task-list"),
    url(r'^task_list/$', 'task_list', name="task-list-today"),
    url(r'^task_form/(?P<task_id>\d+)', 'task_form'),
    url(r'^task_form/', 'task_form'),
    url(r'^schedule/(?P<date>\d{4}-\d+-\d+)', 'schedule'),
    url(r'^schedule/', 'schedule', name="manage-schedule"),
    url(r'^timecard/', 'timecard', name="manage-timecard"),
    url(r'^jobs/', 'jobs', name="manage-jobs"),
    
#    url(r'^daily.html', 'daliy'),
#    url(r'^weekly.html', 'weekly'),
#    url(r'^job_list.html', 'job_list'),

    url(r'^task/new/', 'add_task', name="add-task"),
    url(r'^task/update/(?P<object_id>\d+)', 'update_task', name="update-task"),
    url(r'^task/delete/(?P<object_id>\d+)', 'delete_task', name="del-task"),
    
    url(r'^task/(?P<task_id>\d+)/assign-to/(?P<member_id>\d+)', 'assign_task', name="assign-task")
)
