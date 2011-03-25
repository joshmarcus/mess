from django.utils import simplejson
from django.http import HttpResponse
from django.template import RequestContext, Context
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
import django.conf as conf

from mess.membership import models as m_models


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
    """
    template = get_template('accounting/snippets/acct_flags.html')
    acct_flags = template.render(Context({'account':account}))
    
    return {'id':account.id,
        'name':account.name,
        'balance_limit':str(account.max_allowed_to_owe()),
        'balance':str(account.balance),
        'discount':'???', # what is discount??
        'json_flags':account.frozen_flags(),
        'html_flags':acct_flags,
        'receipt_notes':'Thank you for shopping!'}
