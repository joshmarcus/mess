from datetime import date, timedelta
import datetime
import time

from django.contrib.auth.decorators import user_passes_test
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.template.loader import get_template
from django.template import Template, Context
from django.utils.safestring import mark_safe

from mess.accounting import models as a_models
from mess.accounting.models import Transaction
from mess.membership import models as m_models
from mess.scheduling import models as s_models
#from mess.accounting.models import get_credit_choices, get_debit_choices
#from mess.accounting.models import get_trans_total
from mess.reporting import forms

from mess.utils.search import list_usernames_from_fullname

def find_dups(mems):
    uniqs = {}
    dups = []
    found_dups = {}
    for member in mems:
        fullname = member.user.get_full_name()
        if fullname in uniqs:
            dups.append(member)
            if fullname not in found_dups:
                dups.append(uniqs[fullname])
                found_dups[fullname] = 1
        else:
            uniqs[fullname] = member
    return dups

@user_passes_test(lambda u: u.is_staff)
def anomalies(request):
    blips = 0
    report = ''
    mems = m_models.Member.objects.all()
    issues = [
        ('Missing Firstname', mems.filter(user__first_name='Firstname')),
        ('Semicolon in Name', mems.filter(user__first_name__contains=';')),
        ('Comma in Name', mems.filter(user__first_name__contains=',')),
        ('Missing Lastname', mems.filter(user__last_name='Lastname')),
        ('Duplicate Name', find_dups(mems)),
        ('Email without @', mems.filter(emails__isnull=False).exclude(emails__email__contains='@')),
        ]
    for issue, afflicteds in issues:
        report += '<h3>%s (%d members)</h3>\n' % (issue, len(afflicteds))
        blips += len(afflicteds)
        for m in afflicteds:
            report += '<a href="/membership/members/%s">%s</a> \
                (<a href="/membership/accounts/%s">%s</a>)<br>\n' % \
                (m.user.username, m, m.primary_account().id, m.primary_account())

    report = '<h1>Anomalies Report (%d blips)</h1>\n' % blips + report
    return HttpResponse(report)

@user_passes_test(lambda u: u.is_staff)
def contact(request):
    context = RequestContext(request)
    members = m_models.Member.objects.filter(status='a', accountmember__shopper=False)
    context['emailable'] = members.filter(emails__isnull=False)
    context['nonemailable'] = members.exclude(emails__isnull=False)
    template = get_template('reporting/contact.html')
    return HttpResponse(template.render(context))


@user_passes_test(lambda u: u.is_staff)
def reports(request):
    context = RequestContext(request)
    context['prepacked_account_lists'] = [
          {'name':'Active Contact List',
           'filter':'members__status__in=La',
           'include_inactive':True,
           'output':'members\r\n'+
                '{% for y in x.members.all %}{% for z in y.phones.all %}{{ y.user.first_name }}: {{ z }}<br>{% endfor %}{% endfor %}\Phones\r\n'+
                '{% for y in x.members.all %}{% for z in y.emails.all %}{{ y.user.first_name }}: {{ z }}<br>{% endfor %}{% endfor %}\Emails'},
          {'name':'With Permanent Shifts',
           'filter':'task__time__year='+str(datetime.date.today().year+1),
           'output':'{% for m in x.members.all %}{{ m }}: {{ m.next_shift }}<br>{% endfor %}\\Shifts by Member\r\nnote'},
          {'name':'With A Work Exemption',
           'filter':'members__work_status=e',
           'output':'{% for m in x.members.all %}{{ m }}: {{ m.get_work_status_display }}<br>{% endfor %}\\Members\r\nnote'},
          {'name':'With Committee or Commitment Work',
           'filter':'members__work_status=c',
           'output':'{% for m in x.members.all %}{{ m }}: {{ m.get_work_status_display }}<br>{% endfor %}\\Members\r\nnote'},
          {'name':'Needing Shifts? Incomplete List',
           'filter':'task__time__gte!='+str(datetime.date.today())+'\r\nmembers__work_status__in!=ec',
           'output':'note'},
          {'name':'With A Member On LOA',
           'filter':'members__status=L',
           'include_inactive':True,
           'output':'{% for m in x.members.all %}{{ m }}: {{ m.get_status_display }}<br>{% endfor %}\\Members\r\nnote'},
          {'name':'With No Proxy Shoppers',
           'filter':'accountmember__shopper!=True',
           'output':'active_member_count'},
          {'name':'With At Least $50 Deposit',
           'filter':'deposit__gte=50.00',
           'output':'deposit'},
          {'name':'Frozen',
           'filter':'can_shop=False',
           'output':'can_shop\r\ndeposit\r\nbalance\r\nhours_balance'},
          {'name':'Owing 1 Hour or More',
           'filter':'hours_balance__gte=1.00',
           'output':'hours_balance\r\nnote'},
        ]
    template = get_template('reporting/reports.html')    
    return HttpResponse(template.render(context))


@user_passes_test(lambda u: u.is_staff)
def list(request):
    template = get_template('reporting/list.html')
    context = RequestContext(request)
    context['form'] = forms.ListFilterForm(request.GET)
    context['errors'] = []
    if request.GET.has_key('desc'):
        context['desc'] = request.GET['desc']

    for requestfield in ['object','include_inactive','filter','output']:
        if request.GET.has_key('object') and context['form'].is_valid():
            context[requestfield] = context['form'].cleaned_data[requestfield]
        else:
            context[requestfield] = ''
    
    if context['object'] == 'Accounts':
        objects = m_models.Account.objects.all()
        if not context['include_inactive']:
            objects = objects.filter(members__status='a', 
                        accountmember__shopper=False).distinct()
        blank_object = m_models.Account()
        outputters = [ListOutputter('<a href="{% url account x.id %}">{{ x }}</a>',blank_object, 'Account')]
    elif context['object'] == 'Members':
        objects = m_models.Member.objects.all()
        if not context['include_inactive']:
            objects = objects.filter(status='a')
        blank_object = m_models.Member()
        outputters = [ListOutputter('<a href="{% url member x.user.username %}">{{ x }}</a>',blank_object, 'Member')]
    elif context['object'] == 'Tasks':
        objects = s_models.Task.objects.all()
        if not context['include_inactive']:
            # show only tasks in the next 6 weeks...
            objects = objects.filter(time__range=(datetime.date.today(),datetime.date.today()+datetime.timedelta(weeks=6)))
            # ...or in the next 4 weeks if we're sure it's a 4-week rotation
            objects = objects.exclude(time__gt=datetime.date.today()+datetime.timedelta(weeks=4), recur_rule__interval=4)
        blank_object = s_models.Task()
        outputters = [ListOutputter('<a href="{% url scheduling-task x.id %}">{{ x }}</a>', blank_object, 'Task')]
    else:
        objects = [] 
        outputters = []

    for filterline in context['filter'].split('\r\n'):
        if len(filterline) == 0:
            continue
        try:
            filterq, filterval = filterline.split('=')
            if filterval == 'True': 
                filterval = True
            if filterval == 'False': 
                filterval = False
            if filterq[-1] == '!':
                objects = objects.exclude(**{str(filterq[:-1]):filterval})
            else:
                objects = objects.filter(**{str(filterq):filterval}).distinct()
        except:
            context['errors'].append(filterline)

    for outfield in context['output'].split('\r\n'):
        if len(outfield) == 0:
            pass
        elif outfield[:4] == 'Box:':
            y = ListOutputter(outfield[4:], blank_object)
            context['textarea'] = [y.render(x) for x in objects]
        else:
            outputters.append(ListOutputter(outfield, blank_object))

    context['result'] = [[y.render(x) for y in outputters] for x in objects]
    context['outputfieldnames'] = outputters
    return HttpResponse(template.render(context))

class ListOutputter:
    def __init__(self, field, blank_object, name=None):
        self.field = field
        self.name = name or field.title()
        if '{' in field:
            self.render = self.render_as_template
            if '\\' in field:
                self.field, self.name = field.split('\\',1)
            self.template = Template(self.field)
        else:
            self.fieldpath = self.field.split('.')
            self.render = self.render_by_getattr

    def render_as_template(self, object):
        object_context = Context({'x':object})
        try:
            return self.template.render(object_context)
        except:
            return 'error: '+self.field
        
    def render_by_getattr(self, object):
        for pathpiece in self.fieldpath:
            if not hasattr(object, pathpiece):
                return 'error: '+self.field
            object = getattr(object, pathpiece)
        if hasattr(object, 'all'):
            return '\n'.join([unicode(relobj) for relobj in object.all()])
        elif hasattr(object, 'url'):
            # mark_safe  tells the template not to escape the <html tags>
            return mark_safe(u'<a href="%s">%s</a>' % (object.url, object))
        else:
            return unicode(object)

    def __unicode__(self):
        return self.name

def transaction_list_report(request):
    # c is the context to be passed to the template
    c = RequestContext(request)
    c['page_name'] = 'Transaction List'
    c['report_title'] = 'List of Transactions Matching Filter'

    # start with all transactions
    trans = Transaction.objects

    # if account or member specified, filter that
    if request.GET.has_key('account'): 
        c['account']=request.GET.get('account')
        if c['account'] != "":
            trans = trans.filter(account__name = c['account'])
    if request.GET.has_key('member'):
        c['member'] = request.GET.get('member')
        if c['member'] != "":
            c['usernames'] = list_usernames_from_fullname(c['member'])
            trans = trans.filter(member__user__username__in = c['usernames'])

    # Filter date range -- default to 1900-today.
    # If query date is invalid, error is ugly.  But that shouldn't happen.
    # strptime is hard to use, so here I do yyyy-mm-dd2date as slices.
    # End would be midnight before, but we want midnight after, so timedelta.
    if request.GET.has_key('start'):
        ymd = request.GET.get('start')
        c['start'] = date(int(ymd[:4]),int(ymd[5:7]),int(ymd[8:]))
    else: c['start'] = date(1900,1,1)
    if request.GET.has_key('end'): 
        ymd = request.GET.get('end')
        c['end'] = date(int(ymd[:4]),int(ymd[5:7]),int(ymd[8:]))
    else: c['end'] = date.today()
    if c['end'] < c['start']: (c['start'],c['end']) = (c['end'],c['start'])
    trans = trans.filter(date__range=(c['start'], c['end']+timedelta(days=1)))

    c['transactions'] = trans
    return render_to_response('reporting/transactions_list.html', c)


def transaction_report(request, report='all'):
    """View to summerize transactions by type."""
    context = {}
    context['page_name'] = 'Transaction Summaries'
    if report == 'all':
        report_title = 'Summary of All Transactions'
        start_date = date(1900, 01, 01)        
        end_date = date.today() + timedelta(days=1) 
    elif report == 'today':
        start_date = date.today()
        end_date = start_date + timedelta(days=1)                
        formatted_date = start_date.strftime('%A, %B %d, %Y')        
        report_title = 'Transactions Summary for Today, %s' % formatted_date
    elif report == 'yesterday':
        start_date = date.today() - timedelta(days=1)        
        end_date = date.today()
        formatted_date = start_date.strftime('%A, %B %d, %Y')        
        report_title = 'Transactions Summary for Yesterday, ' + formatted_date
    elif report == 'week':
        d = date.today()
        start_date = d - timedelta(days=d.weekday())        
        end_date = date.today() + timedelta(days=1)
        formatted_date = start_date.strftime('%A, %B %d, %Y')        
        report_title = 'Transaction Summary for the Week Beginning ' + formatted_date
    elif report == 'month':
        start_date = date(date.today().year, date.today().month , 01)        
        end_date = date.today() + timedelta(days=1)
        formatted_date = start_date.strftime('%B, %Y')        
        report_title = 'Transactions Summary for the Month of ' + formatted_date
    elif report == 'year':
        start_date =  date(date.today().year, 01, 01)
        end_date = date.today() + timedelta(days=1)
        formatted_date = start_date.strftime('%Y')        
        report_title = 'Transaction Summary for Year of ' + formatted_date
    elif report == 'custom':
        start_date = date.today() - timedelta(days=1)        
        end_date = date.today()
        formatted_date = start_date.strftime('%A, %B %d, %Y')        
        report_title = 'Transaction Summary from ' + formatted_date
        report_title += 'to ' + end_date.strftime('%A, %B %d, %Y')

    context['report_title'] = report_title
    context['total_credits'] = 0
    context['total_debits'] = 0
    #d = date.today()
    #context['date'] = d.strftime('%A, %B %d, %Y')
    for type, name in a_models.PURCHASE_CHOICES:
        name = name.lower().replace(' ','_')
        total_name = 'total_' + name
        transactions = Transaction.objects.filter(
                timestamp__range=(start_date, end_date),
                purchase_type=type)
        context[name] = transactions
        context[total_name] = get_trans_total(transactions, 'purchase')
        context['total_credits'] += context[total_name]
    for type, name in a_models.PAYMENT_CHOICES:
        name = name.lower().replace(' ','_')
        total_name = 'total_' + name
        transactions = Transaction.objects.filter(
                timestamp__range=(start_date, end_date),
                payment_type=type)
        context[name] = transactions
        context[total_name] = get_trans_total(transactions, 'payment')
        context['total_debits'] += context[total_name]

    return render_to_response('reporting/transactions_summary.html', context,
            context_instance=RequestContext(request))


# helper functions below

def get_trans_total(trans, type='all'):
    total = 0
    if type == 'all' or type == 'purchase':
        for tran in trans:
            total += tran.purchase_amount
    if type == 'all' or type == 'payment':
        for tran in trans:
            total += tran.payment_amount
    return total

    #def transaction_list_report(request, report='all'):
#    """View to list transactions."""
#    context = {}
#    context['page_name'] = 'Transactions'
#    if report == 'all':
#        report_title = 'All Transactions'
#        start_date = date(1900, 01, 01)        
#        end_date = date.today() + timedelta(days=1) 
#    elif report == 'today':
#        start_date = date.today()
#        end_date = start_date + timedelta(days=1)                
#        formatted_date = start_date.strftime('%A, %B %d, %Y')        
#        report_title = 'Transactions Summary for Today, ' + formatted_date
#    elif report == 'yesterday':
#        start_date = date.today() - timedelta(days=1)        
#        end_date = date.today()
#        formatted_date = start_date.strftime('%A, %B %d, %Y')        
#        report_title = 'Transactions Summary for Yesterday, ' + formatted_date
#    elif report == 'week':
#        d = date.today()
#        start_date = d - timedelta(days=d.weekday())        
#        end_date = date.today()
#        formatted_date = start_date.strftime('%A, %B %d, %Y')        
#        report_title = 'Transaction Summary for the Week Beginning ' + formatted_date
#    elif report == 'month':
#        start_date = date(date.today().year, date.today().month , 01)        
#        end_date = date.today()
#        formatted_date = start_date.strftime('%B, %Y')        
#        report_title = 'Transactions Summary for the Month of ' + formatted_date
#    elif report == 'year':
#        start_date = date(date.today().year, 01, 01)  
#        end_date = date.today() + timedelta(days=1)
#        formatted_date = start_date.strftime('%Y')        
#        report_title = 'Transaction Summary for Year of ' + formatted_date
#    elif report == 'custom':
#        start_date = date.today() - timedelta(days=1)        
#        end_date = date.today()
#        formatted_date = start_date.strftime('%A, %B %d, %Y')        
#        report_title = 'Transaction Summary from ' + formatted_date
#        report_title += 'to ' + end_date.strftime('%A, %B %d, %Y')
#
#    context['report_title'] = report_title
#    context['transactions'] = Transaction.objects.filter(date__range =
#                                                    (start_date, end_date),)
#    
#    return render_to_response('reporting/transactions_list.html', context,
#                                context_instance=RequestContext(request))
