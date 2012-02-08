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

def staff_permissions(request):
    cashier_perms = cashier_permission(request)
    msr_perms = member_service_rep_permission(request)
    sa_perms = staff_assistant_permission(request)

    return dict(cashier_perms.items() + msr_perms.items() + sa_perms.items())

def cashier_permission(request):
    ''' 
    used as a template context processor before showing 'cashier' tab 
    bool(returnvalue['can_cashier_now']) is trusted by template
    bool(returnvalue) is trusted by accounting/views
    '''
    if not request.user.is_authenticated():
        return {}     # no permission, bool({}) = False
    if request.user.is_staff:
        return {'can_cashier_now':True}
    if (request.META['REMOTE_ADDR'] == settings.MARIPOSA_IP
        and (request.user.get_profile().is_cashier_today
            or request.user.get_profile().is_cashier_recently
            or request.user.has_perm('accounting.add_transaction'))):
        return {'can_cashier_now':True}
    return {}     # no permission, bool({}) = False

def member_service_rep_permission(request):
    ''' 
    used as a template context processor before showing tabs
    that only a member_service_rep (or staff) should be able to
    see.

    bool(returnvalue['can_edit_timecards']) is trusted by template
    bool(returnvalue) is trusted by accounting/views
    '''
    if not request.user.is_authenticated():
        return {}     # no permission, bool({}) = False
    if request.user.is_staff:
        return {'is_member_services_rep':True}

    if (request.user.groups.filter(name="member service representative").count() > 0
        and request.META['REMOTE_ADDR'] == settings.MARIPOSA_IP):
            return {'is_member_services_rep':True}
    return {}     # no permission, bool({}) = False

def staff_assistant_permission(request):
    ''' 
    Used as a template context processor before showing tabs
    that only a staff_assistant (or staff) should be able to
    see.

    bool(returnvalue['can_cashier_now']) is trusted by template
    bool(returnvalue) is trusted by accounting/views
    '''
    if not request.user.is_authenticated():
        return {}     # no permission, bool({}) = False
    if request.user.is_staff:
        return {'is_staff_assistant':True}
    return {}     # no permission, bool({}) = False

