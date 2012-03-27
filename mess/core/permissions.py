from django.conf import settings

def has_elevated_perm(request, app_name, permission):
    if request.user.is_staff:
        return True
    elif not request.META['REMOTE_ADDR'] in settings.MARIPOSA_IPS:
        return False
    else:
        return request.user.has_perm(app_name + "." + permission)
    
    
