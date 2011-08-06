from django.utils import simplejson
from django.template import RequestContext, Context
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.db.models import Q
from django.utils.safestring import mark_safe

import django.conf as conf

from mess.membership import models as m_models
from mess.accounting import models as a_models

import datetime
import urllib2
import time
import md5
from decimal import Decimal 

def index(request):
    # verify secret
    if not request.GET.has_key('secret') or request.GET['secret'] != conf.settings.IS4C_SECRET or conf.settings.IS4C_SECRET == 'fakesecret':
        return HttpResponse('Wrong IS4C secret!!')

    if request.method == 'POST':
        # read the specific request type and act accordingly.
        pass
    return HttpResponse('{"json":"yes!"}', mimetype='application/json')


def account(request, account_id):
    # all requests will have some get variables, at the very least the secret is a get variable.
    # verify secret
    if not request.GET.has_key('secret') or request.GET['secret'] != conf.settings.IS4C_SECRET or conf.settings.IS4C_SECRET == 'fakesecret':
        return HttpResponse('Wrong IS4C secret!!')

    account = get_object_or_404(m_models.Account, id=account_id)
    result = simplejson.dumps(getacctdict(account))
    return HttpResponse(result, mimetype='application/json')

def accounts(request):
    # all requests will have some get variables, at the very least the secret is a get variable.
    # verify secret
    if not request.GET.has_key('secret') or request.GET['secret'] != conf.settings.IS4C_SECRET or conf.settings.IS4C_SECRET == 'fakesecret':
        return HttpResponse('Wrong IS4C secret!!')

    accounts = [getacctdict(account) for account in m_models.Account.objects.all()]
    result = simplejson.dumps(accounts)
    return HttpResponse(result, mimetype='application/json')

# helper method
def getacctdict(account):
    """
    stuff is4c needs:
    * account id
    * account name #in model
    * account balance limit #calculated from elsewhere
    * account status: active, frozen #calculated elsewhere; we might have to customize
    * account balance #in model, should match transaction table
    * account discount #does not exist yet
    * account cashier notes #calculated field, account flags
    * account receipt notes  #future calculated fields
    * account active members
    """
    template = get_template('accounting/snippets/acct_flags.html')
    acct_flags = template.render(Context({'account':account}))
    
    return {'id':account.id,
        'name':account.name,
        'balance_limit':str(account.max_allowed_to_owe()),
        'balance':str(account.balance),
        'discount':str(account.discount), 
        'json_flags':account.frozen_flags(),
        'html_flags':acct_flags,
        'receipt_notes':'Thank you for shopping!',
	'active_member_count': account.active_member_count}

def member(request, member_id):
    # all requests will have some get variables, at the very least the secret is a get variable.
    # verify secret
    if not request.GET.has_key('secret') or request.GET['secret'] != conf.settings.IS4C_SECRET or conf.settings.IS4C_SECRET == 'fakesecret':
        return HttpResponse('Wrong IS4C secret!!')

    member = get_object_or_404(m_models.Member, id=member_id)
    result = simplejson.dumps(getmemberdict(member))
    return HttpResponse(result, mimetype='application/json')

def members(request):
    # all requests will have some get variables, at the very least the secret is a get variable.
    # verify secret
    if not request.GET.has_key('secret') or request.GET['secret'] != conf.settings.IS4C_SECRET or conf.settings.IS4C_SECRET == 'fakesecret':
        return HttpResponse('Wrong IS4C secret!!')

    members = [getmemberdict(member) for member in m_models.Member.objects.all()]
    result = simplejson.dumps(members)
    return HttpResponse(result, mimetype='application/json')

# helper method
def getmemberdict(member):
    return {'memberid':member.id,
        'accounts':map(lambda a: a.id, member.accounts.all()),
        'username':member.user.username,
        'firstname':member.user.first_name,
        'lastname':member.user.last_name,
        'work_status':member.work_status,
        'equity':'please do this by hand first',
        'is_active':member.is_active,
        'is_on_loa':member.is_on_loa}

@csrf_exempt
def recordtransaction(request):
    # all requests will have some get variables, at the very least the secret is a get variable.
    # verify secret
    if not request.GET.has_key('secret') or request.GET['secret'] != conf.settings.IS4C_SECRET or conf.settings.IS4C_SECRET == 'fakesecret':
        return HttpResponse('Wrong IS4C secret!!')

    # get the transaction and sanitize it
    json = request.POST['transaction'] 
    t = simplejson.loads(json)
    t['account'] = m_models.Account.objects.get(id=t['account'])
    if 'member' in t: 
        t['member'] = m_models.Member.objects.get(id=t['member'])
    t['payment_amount'] = Decimal(str(t.get('payment_amount', 0)))
    t['purchase_amount'] = Decimal(str(t.get('purchase_amount', 0)))
    t['payment_type'] = t.get('payment_type', '')
    t['purchase_type'] = t.get('purchase_type', '')
    t['is4c_cashier_id'] = t.get('is4c_cashier_id', 0)
    t['is4c_timestamp'] = t.get('date')
    if 'date' in t: 
        del t['date']

    tnew = a_models.Transaction(**t)
    tnew.save()
    status_code = (500, 200)[tnew.pk and a_models.Transaction.objects.filter(pk=tnew.pk).exists()]
    return HttpResponse(status=status_code)

@login_required
def gotois4c(request):
    """ Send user to is4c hosted locally """
    profile = request.user.get_profile()
    data = ('username='+urllib2.quote(request.user.username)
           +'&fullname='+urllib2.quote(request.user.get_full_name())
           +'&mem_id='+urllib2.quote(str(profile.id))
           +'&user_id='+str(request.user.id)
           +'&time='+str(int(time.time()))
           +'&secret=')
    md5result = md5.md5(data + conf.settings.GOTOIS4C_SECRET).hexdigest()
    #urltarget = 'http://mariposa.4now.us/phpBB3/index.php'
    urltarget = 'http://localhost/mess-login.php'
    data = mark_safe(data)
    return render_to_response('is4c/gotois4c.html', locals(),
            context_instance=RequestContext(request))

