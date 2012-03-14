import datetime
import urllib
from decimal import Decimal as D
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.db.models.aggregates import Sum
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.template.loader import get_template
from django.utils import simplejson
from django.views.decorators.csrf import csrf_exempt
from django.forms.formsets import formset_factory

from mess.accounting import forms, models
from mess.accounting.forms import TransactionForm, CloseOutForm
from mess.membership import models as m_models
from mess.core.permissions import has_elevated_perm
from mess.core.context_processors import cashier_permission

today = datetime.date.today()

@csrf_exempt
def listen_to_paypal(request):
    '''
    this whole thing is documented by Paypal at: 
    https://cms.paypal.com/us/cgi-bin/?cmd=_render-content&content_ID=developer/e_howto_admin_IPNIntro
    '''
    if request.POST:
        file = open('/var/www/live/mess/listen_to_paypal.log','a')
        file.write('\n\n\nListening to Paypal...%s..\n' % datetime.datetime.today())
        file.write(repr(request))
        payer_email = request.POST['payer_email']
        receiver_email = request.POST['receiver_email']
        item_number = request.POST['item_number']
        payment_gross = request.POST['payment_gross']
        txn_id = request.POST['txn_id']
        verifyurl = 'https://www.paypal.com/cgi-bin/webscr?cmd=_notify-validate&'+urllib.urlencode(request.POST) 
        verified = urllib.urlopen(verifyurl).read()
        file.write('\n%s|%s|%s|%s|%s\n' % (payer_email, receiver_email, item_number, payment_gross, verified))
        file.close()
        assert verified == 'VERIFIED', 'Paypal not verified'
        assert receiver_email == 'finance@mariposa.coop', 'Paypal wrong receiver'
        already_did_transaction = models.Transaction.objects.filter(note__contains=txn_id).count()
        if not already_did_transaction:
            (credit_or_equity, a, account_id, m, member_id) = item_number.split('-')
            account = m_models.Account.objects.get(id=account_id)
            member = m_models.Member.objects.get(id=member_id)
            if credit_or_equity == 'Credit':
                transaction = models.Transaction.objects.create(
                    account=account,
                    member=member,
                    payment_type='Y',
                    payment_amount=D(payment_gross),
                    note='Paypal txn_id=%s from %s' % (txn_id, payer_email),
                )
            else:   # equity
                transaction = models.Transaction.objects.create(
                    account=account,
                    member=member,
                    payment_type='Y',
                    payment_amount=D(payment_gross),
                    purchase_type='O',
                    purchase_amount=D(payment_gross),
                    note='Paypal txn_id=%s from %s' % (txn_id, payer_email),
                )

    return render_to_response('accounting/test_paypal.html', locals(),
            context_instance=RequestContext(request))
    

# cashier permission is the first if
@login_required
def transaction(request):
#    if not cashier_permission(request):
#        return HttpResponse('Sorry, you do not have cashier permission. %s' 
#                             % request.META['REMOTE_ADDR'])
    if not has_elevated_perm(request, 'accounting', 'add_transaction'):
        return HttpResponseRedirect(reverse('welcome'))


    context = RequestContext(request)
    if 'getcashierinfo' in request.GET:
        account_id = request.GET['account']
        account = m_models.Account.objects.get(id=account_id)
        context['account'] = account
        if request.GET['getcashierinfo'] == 'members':
            template = get_template('accounting/snippets/members.html')
        elif request.GET['getcashierinfo'] == 'transactions':
            context['transactions'] = account.transaction_set.all()
            template = get_template('accounting/snippets/transactions.html')
        elif request.GET['getcashierinfo'] == 'acctinfo':
            template = get_template('accounting/snippets/acctinfo.html')
        return HttpResponse(template.render(context))

    if request.method == 'POST':
        form = forms.TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False) # get info from form
            transaction.entered_by = request.user # add entered_by
            transaction.save()                    # save to database
            return HttpResponseRedirect(reverse('transaction'))
    else:
        form = forms.TransactionForm()
    today = datetime.date.today()
    transactions = models.Transaction.objects.filter(
            timestamp__range=(today,today+datetime.timedelta(1)))
    context = {
        'transactions':transactions,
        'form':form,
        'can_reverse':True,
    }
    return render_to_response('accounting/transaction.html', context,
                                context_instance=RequestContext(request))

# cashier permission is the first if
@login_required
def cashsheet_input(request):
    if not cashier_permission(request):
        return HttpResponse('Sorry, you do not have cashier permission. %s' 
                             % request.META['REMOTE_ADDR'])

    if 'getcashierinfo' in request.GET:
        account_id = request.GET['account']
        account = m_models.Account.objects.get(id=account_id)
        if request.GET['getcashierinfo'] == 'balance':
            return HttpResponse(account.balance)
        elif request.GET['getcashierinfo'] == 'max_allowed_to_owe':
            return HttpResponse(str(int(account.max_allowed_to_owe())))
        elif request.GET['getcashierinfo'] == 'hours_balance':
            return HttpResponse(account.hours_balance)
        elif request.GET['getcashierinfo'] == 'transactions':
            context = RequestContext(request)
            context['transactions'] = account.transaction_set.all().order_by('-timestamp')[:25]
            template = get_template('accounting/snippets/transactions.html')
            return HttpResponse(template.render(context))
        else: # request.GET['getcashierinfo'] == 'acct_flags':
            template_file = 'accounting/snippets/acct_flags.html'
            show_acct_link = True
            return render_to_response(template_file, locals())

    if request.method == 'POST':
        if request.POST.get('action') == 'Reverse':
            reverseform = forms.ReverseForm(request.POST)
            if not reverseform.is_valid():
                return HttpResponse(repr(reverseform.errors))
            rev = reverseform.save(entered_by=request.user) 
            form = forms.CashsheetForm(tofix=rev)
            show_advanced_fields = True
        else:
            form = forms.CashsheetForm(request.POST)
            if form.is_valid():
                form.save(entered_by=request.user)
                return HttpResponseRedirect(reverse('cashsheet_input'))
            show_advanced_fields = True
    else:
        form = forms.CashsheetForm()
    transactions = models.Transaction.objects.filter(
            timestamp__range=(today,today+datetime.timedelta(1))).exclude(
            purchase_type='U').exclude(purchase_type='O')
    can_reverse = True
    if request.user.is_staff:
        show_advanced_fields = True
    return render_to_response('accounting/cashsheet_input.html', locals(),
            context_instance=RequestContext(request))

def hours_balance(request):
    if not has_elevated_perm(request, 'membership', 'change_account'):
        return HttpResponseRedirect(reverse('welcome'))
    if 'getcashierinfo' in request.GET:
        account_id = request.GET['account']
        account = m_models.Account.objects.get(id=account_id)
        return HttpResponse(account.hours_balance)
    if request.method == 'POST':
        form = forms.HoursBalanceForm(request.POST)
        if form.is_valid():
            hourstransaction = form.save(commit=False) # get info from form
            hourstransaction.entered_by = request.user # add entered_by
            hourstransaction.save()                    # save to database
            return HttpResponseRedirect(reverse('hours_balance'))
    else:
        form = forms.HoursBalanceForm()
    hours_transactions = models.HoursTransaction.objects.filter(
            timestamp__range=(today,today+datetime.timedelta(1)))
    return render_to_response('accounting/hours_balance.html', locals(),
            context_instance=RequestContext(request))

# cashier permission is the first if
@login_required
def close_out(request, date=None):
    '''Page to double-check payment amounts'''
    if not has_elevated_perm(request, 'membership', 'change_account'):
        return HttpResponseRedirect(reverse('welcome'))
    #if not cashier_permission(request):
    #    return HttpResponse('Sorry, you do not have cashier permission. %s' 
    #                         % request.META['REMOTE_ADDR'])

    if date:
        try:
            date = datetime.date(*time.strptime(date, "%Y-%m-%d")[0:3])
        except ValueError:
            raise Http404
    else:
        date = datetime.date.today()

    trans = models.Transaction.objects.filter(
                   timestamp__range=(date, date+datetime.timedelta(1)))

    columns = [{'type': 'Credit / Debit', 'total': 0,
                'transactions': trans.filter(payment_type__in=('C','D'))},
               {'type': 'Check / Money Order', 'total': 0,
                'transactions': trans.filter(payment_type__in=('K','M'))},
               {'type': 'EBT', 'total': 0,
                'transactions': trans.filter(payment_type='E')}]
    for column in columns:
        if 'order_by' in request.GET:
            order_by = request.GET['order_by']
            column['transactions'] = column['transactions'].order_by(order_by)
        for trans in column['transactions']:
            if not trans.fixes_target():
                column['total'] += trans.fixed_payment_amount()

    return render_to_response('accounting/close_out.html', locals(),
            context_instance=RequestContext(request))

def cashsheet(request):
    ''' printable cash sheet for all active accounts '''
    if request.GET.has_key('row_height'):
        form = forms.CashSheetFormatForm(request.GET)
    else:
        form = forms.CashSheetFormatForm()
    if form.is_valid():
        row_height = form.cleaned_data.get('row_height')
        rows_per_page = form.cleaned_data.get('rows_per_page')
    else:
        row_height = 2.5
        rows_per_page = 25
    # include ! accounts at top ("Mariposa" and "UNCLAIMED")
    accounts = (list(m_models.Account.objects.filter(name__startswith='!')) +
                list(m_models.Account.objects.present()))
    return render_to_response('accounting/cashsheet.html', locals(),
            context_instance=RequestContext(request))

def frozen(request):
    # list of accounts that are frozen on the cash sheets
    accounts = m_models.Account.objects.active()  # LOA may still be frozen
    accounts = accounts.filter(Q(balance__gt=0) | Q(hours_balance__gt=0))
    if request.GET.get('has_key'):
        accounts = accounts.filter(members__card_number__gt='')
    return render_to_response('accounting/frozen.html', locals(),
            context_instance=RequestContext(request))


def billing(request):
    ''' NEW 2011 view to bill equity to members, not accounts '''
    members = m_models.Member.objects.filter(Q(equity_held__gt=0) | Q(equity_due__gt=0) | Q(date_missing__isnull=True, date_departed__isnull=True))
    if request.method=='POST':
        form = forms.MemberEquityBillingForm(request.POST)
        if form.is_valid():
            for member in members:
                member.equity_due += member.potential_new_equity_due()
                member.save()
    else:
        form = forms.MemberEquityBillingForm()
    total_equity_target = 0
    total_existing_equity_held = 0
    total_existing_equity_due = 0
    total_potential_bills = 0
    for member in members:
        total_equity_target += member.equity_target()
        total_existing_equity_held += member.equity_held
        total_existing_equity_due += member.equity_due
        total_potential_bills += member.potential_new_equity_due()
    return render_to_response('accounting/billing.html', locals(),
            context_instance=RequestContext(request))

def billing_old(request):
    ''' view to bill dues and deposits for all active accounts '''
    if request.method=='POST':
        form = forms.BillingOldForm(request.POST)
        if form.is_valid():
            total_billable_members = 0
            total_deposits = 0
            total_potential_bills = 0
            accounts = m_models.Account.objects.active()
            for account in accounts:
                billable_members = account.billable_member_count
                total_billable_members += billable_members
                total_deposits += account.deposit
                potential_bill = (form.cleaned_data['amount_per_member'] * 
                                  billable_members)
                if form.cleaned_data['bill_type'] == 'O':   # O = Member Equity
                    max_deposit = (form.cleaned_data['max_deposit_per_member'] *
                                      billable_members)
                    if account.deposit + potential_bill > max_deposit:
                        potential_bill = max(max_deposit - account.deposit, 0)
                account.potential_bill = potential_bill
                total_potential_bills += potential_bill
            
            if request.POST['action'] == 'Commit':
                models.commit_potential_bills(accounts, 
                                      bill_type=form.cleaned_data['bill_type'],
                                      entered_by=request.user)
                return HttpResponse('Billing was completed.  Thank you.')
    else:
        form = forms.BillingOldForm()
    return render_to_response('accounting/billing_old.html', locals(),
            context_instance=RequestContext(request))

# cashier permission is the first if
# code copied from transactions and tweaked.  
'''
is there anything we can break out into helper functions?  :)
like maybe this 'getcashierinfo' section?
'''
@login_required
def after_hours(request):
    if not cashier_permission(request):
        return HttpResponse('Sorry, you do not have cashier permission. %s' 
                             % request.META['REMOTE_ADDR'])

    context = RequestContext(request)
    today = datetime.date.today()
    
    if 'getcashierinfo' in request.GET:
        account_id = request.GET['account']
        account = m_models.Account.objects.get(id=account_id)
        context['account'] = account
        if request.GET['getcashierinfo'] == 'members':
            template = get_template('accounting/snippets/members.html')
        elif request.GET['getcashierinfo'] == 'transactions':
            context['transactions'] = models.Transaction.objects.filter(
            timestamp__range=(today,today+datetime.timedelta(1)),
            purchase_type='A')
            template = get_template('accounting/snippets/transactions.html')
        elif request.GET['getcashierinfo'] == 'acctinfo':
            template = get_template('accounting/snippets/acctinfo.html')
        return HttpResponse(template.render(context))

    if request.method == 'POST':
        form = forms.AfterHoursForm(request.POST)
        if form.is_valid():
            a = form.cleaned_data['account']
            p = form.cleaned_data['purchases']
            p_tot = form.cleaned_data['purchase_total']
            ah_trans = models.Transaction(account=a, entered_by=request.user,
                                          purchase_type='A',
                                          purchase_amount=p_tot,
                                          note=p)
            ah_trans.save()
            return HttpResponseRedirect(reverse('after_hours'))
    else:
        form = forms.AfterHoursForm()
    context['form'] = form
    # change line below to just be after-hours transactions??
    transactions = models.Transaction.objects.filter(
            timestamp__range=(today,today+datetime.timedelta(1)),
            purchase_type='A')
    context['transactions'] = transactions
    context['can_reverse'] = True
    template = get_template('accounting/after_hours.html')
    return HttpResponse(template.render(context))


# cashier permission is the first if
# initial code copied from after-hours...
@login_required
def EBT(request):
    if not cashier_permission(request):
        return HttpResponse('Sorry, you do not have cashier permission. %s' 
                             % request.META['REMOTE_ADDR'])
    context = RequestContext(request)
    today = datetime.date.today()
    if 'getcashierinfo' in request.GET:
        account_id = request.GET['account']
        account = m_models.Account.objects.get(id=account_id)
        context['account'] = account
        if request.GET['getcashierinfo'] == 'members':
            template = get_template('accounting/snippets/members.html')
        elif request.GET['getcashierinfo'] == 'transactions':
            context['transactions'] = models.Transaction.objects.filter(
            timestamp__range=(today, today + datetime.timedelta(1)),
            payment_type='E')
            template = get_template('accounting/snippets/transactions.html')
        elif request.GET['getcashierinfo'] == 'acctinfo':
            template = get_template('accounting/snippets/acctinfo.html')
        elif request.GET['getcashierinfo'] == 'ebtbulkorders':
            template = get_template('accounting/snippets/ebtbulkorders.js')
        return HttpResponse(template.render(context))
    if request.method == 'POST':
        form = forms.EBTForm(request.POST)
        if form.is_valid():
            form.save(entered_by=request.user)
            return HttpResponseRedirect(reverse('EBT'))
    else:
        form = forms.EBTForm()
    context['form'] = form
    transactions = models.Transaction.objects.filter(
            timestamp__range=(today,today+datetime.timedelta(1)),
            payment_type='E')
    context['transactions'] = transactions
    context['can_reverse'] = True
    template = get_template('accounting/EBT.html')
    return HttpResponse(template.render(context))

def storeday(request):
    ''' set the current time as a storeday breakpoint.  or, manage storedays '''
    if request.method == 'POST':
        if 'begin_new_storeday_now' in request.POST:
            newday = models.StoreDay(start=datetime.datetime.today())
            newday.save()
            referer = request.META['HTTP_REFERER']
            if referer:
                return HttpResponseRedirect(referer)
        else:
            formset = forms.StoreDayFormSet(request.POST)
            if formset.is_valid():
                formset.save()
                return HttpResponseRedirect(reverse('storeday'))
    else:
        formset = forms.StoreDayFormSet()
    title = 'Store Day Management'
    return render_to_response('accounting/storeday.html', locals(),
            context_instance=RequestContext(request))

@login_required
def EBT_bulk_orders(request, EBTBulkOrder_id=None):
    # probably want to switch this to only list unpaid

    if not has_elevated_perm(request, 'accounting', 'add_ebt_bulk_order'):
        return HttpResponseRedirect(reverse('welcome'))

    if EBTBulkOrder_id:
        ebt_bo = get_object_or_404(models.EBTBulkOrder, id=EBTBulkOrder_id)
    else:
        ebt_bo = models.EBTBulkOrder()
    is_errors = False

    ret_resp = HttpResponseRedirect(reverse('EBT-bulk-orders'))
    if request.method == 'POST':
        if 'cancel' in request.POST:
            return ret_resp

        ebt_bo_form = forms.EBTBulkOrderForm(request.POST, instance=ebt_bo)
        if ebt_bo_form.is_valid():
            ebt_bo_form.save()
            return ret_resp
        else:
            is_errors = True
    else:
        ebt_bo_form = forms.EBTBulkOrderForm(instance=ebt_bo)

    unpaid = models.EBTBulkOrder.objects.unpaid()
    context = {
        'unpaid': unpaid.order_by('-id'),
        'total_unpaid': unpaid.aggregate(Sum('amount')).values()[0],
        'paid': models.EBTBulkOrder.objects.paid().order_by('-id')[:20],
        'ebt_bo': ebt_bo,
        'is_errors': is_errors,
        'form': ebt_bo_form,
        'add': EBTBulkOrder_id==None, #this bool determines template behavior
    }
    return render_to_response('accounting/EBT_bulk_orders.html', context,
                                context_instance=RequestContext(request))

@login_required
def diagnose_cashier_permission(request):
    ret = '<pre>Diagnosing cashier permission.\n'
    ret += 'Logged in as: %s\n' % request.user
    ret += 'User is authenticated: %s\n' % request.user.is_authenticated()
    ret += 'User is staff: %s\n' % request.user.is_staff
    ret += 'Remote Address: %s\n' % request.META['REMOTE_ADDR']
    ret += 'Mariposa IP: %s\n' % settings.MARIPOSA_IP
    ret += 'Remote Address is Mariposa IP: %s\n' % (request.META['REMOTE_ADDR'] == settings.MARIPOSA_IP)
    ret += 'User: %s\n' % request.user
    ret += 'User is cashier today: %s\n' % request.user.get_profile().is_cashier_today
    ret += 'User is cashier recently: %s\n' % request.user.get_profile().is_cashier_recently
    ret += 'Cashier permission function: %s\n' % cashier_permission(request)
    ret += 'Cashier permission: %s\n' % bool(cashier_permission(request))
    ret += '</pre>'
    return HttpResponse(ret)

def equity_transfer(request, account):
    EquityTransferFormSet = formset_factory(forms.EquityTransferForm, extra=0)
    if request.POST:
        formset = EquityTransferFormSet(request.POST)
        # we don't check formset.is_valid b/c that is causing account.deposit 
        # to be bound from the model, which was messing up the math.
        # related to github ticket 336?
        for form in formset.forms:
            if form.is_valid():
                form.save(request.user)
        return HttpResponseRedirect(reverse('equity_transfer', args=[account]))

    else:
        account = get_object_or_404(m_models.Account, id=account)
        initial = []
        active_members = account.members.active().count()
        total_members = account.members.count()
        if not total_members == 0:
            for member in account.members.active():
                initial.append({'account': account, 'member': member, 'amount': 0})
            for member in account.members.inactive():
                initial.append({'account': account, 'member': member, 'amount': 0})
            if (active_members != 0):
                for i in range(account.deposit*100):
                    initial[i%active_members]['amount'] += 1
            for entry in initial:
                entry['amount'] = (D(entry['amount'])/100).quantize(D('0.01'))

        formset = EquityTransferFormSet(initial=initial)
    return render_to_response('accounting/equity_transfer.html', locals(),
            context_instance=RequestContext(request))
