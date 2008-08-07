from django.conf.urls.defaults import *
from mess.scheduling.models import *

# commented out until there are actual views to point at -- 
# phantom urls wreak havoc with {% url %} and reverse()
urlpatterns = patterns('mess.scheduling.views',
    url(r'^task_list/(?P<date>\d{4}-\d+-\d+)', 'task_list'),
    url(r'^monthly/(?P<date>\d{4}-\d+-\d+)', 'monthly'),
    url(r'^monthly/', 'monthly', name="staff-schedules"),
#    url(r'^daily.html', 'daliy'),
#    url(r'^weekly.html', 'weekly'),
#    url(r'^job_list.html', 'job_list'),

    url(r'^task/new/', 'add_task', name="add-task"),
    url(r'^task/update/(?P<object_id>\d+)', 'update_task', name="update-task"),
    url(r'^task/delete/(?P<object_id>\d+)', 'delete_task', name="del-task"),
)
