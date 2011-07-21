from django.contrib.sites.models import Site
from django.conf import settings

def location(request):
    location = {}
    current_site = Site.objects.get_current()
    location['site'] = current_site
    script_name = request.META['SCRIPT_NAME']
    location['script_name'] = script_name
    path = request.META['PATH_INFO']
    location['path'] = path
    url = 'http://%s%s%s' % (current_site, script_name, path)
    location['url'] = url
    return {'location': location}

def cashier_permission(request):
    ''' 
    used as a template context processor before showing 'cashier' tab 
    bool(returnvalue['can_cashier_now']) is trusted by template
    bool(returnvalue) is trusted by accounting/views
    '''
    if not request.user.is_authenticated():
        return {}     # no permission, bool({}) = False
    if request.user.has_perm('accounting.add_transaction'):
        return {'can_cashier_now':True}
    if (request.META['REMOTE_ADDR'] == settings.MARIPOSA_IP
        and (request.user.get_profile().is_cashier_today
            or request.user.get_profile().is_cashier_recently)):
        return {'can_cashier_now':True}
    return {}     # no permission, bool({}) = False

