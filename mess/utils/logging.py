from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_unicode

FLAG_MAP = {
    'add': ADDITION,
    'edit': CHANGE,
    'delete': DELETION,
}

def log(request, obj, action_flag, change_message='', old_values=None):
    if old_values:
        change_message_list = []
        #raise Exception, old_values['hours_balance']
        for key in old_values:
            if not key.startswith('_') and \
                    old_values[key] != obj.__dict__[key]:
                change_message_list.append('Changed %s: "%s" to "%s"' % 
                        (key, old_values[key], obj.__dict__[key]))
        change_message = '\n'.join(change_message_list)
    LogEntry.objects.log_action(
        user_id = request.user.pk,
        content_type_id = ContentType.objects.get_for_model(obj).pk,
        object_id = obj.pk,
        object_repr = force_unicode(obj),
        action_flag = FLAG_MAP[action_flag],
        change_message = change_message,
    )

