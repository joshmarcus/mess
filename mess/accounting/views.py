import datetime

from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import get_template
from django.utils import simplejson

from mess.accounting import forms, models
from mess.accounting.forms import TransactionForm, CloseOutForm
from mess.membership import models as m_models

# cashier permission is the first if
@user_passes_test(lambda u: u.is_authenticated())
def transaction(request):
    if not m_models.cashier_permission(request):
        return HttpResponse('Sorry, you do not have cashier permission. %s' 
                             % request.META['REMOTE_ADDR'])

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
            transaction = form.save(commit=False)
            transaction.entered_by = request.user
            transaction.save()
            return HttpResponseRedirect(reverse('transaction'))
    else:
        form = forms.TransactionForm()
    context['form'] = form
    today = datetime.date.today()
    transactions = models.Transaction.objects.filter(
            timestamp__range=(today,today+datetime.timedelta(1)))
    context['transactions'] = transactions
    context['can_reverse'] = True
    template = get_template('accounting/transaction.html')
    return HttpResponse(template.render(context))

# cashier permission is the first if
@user_passes_test(lambda u: u.is_authenticated())
def cashsheet_input(request):
    if not m_models.cashier_permission(request):
        return HttpResponse('Sorry, you do not have cashier permission. %s' 
                             % request.META['REMOTE_ADDR'])
    
    if 'getcashierinfo' in request.GET:
        account_id = request.GET['account']
        account = m_models.Account.objects.get(id=account_id)
        if request.GET['getcashierinfo'] == 'balance':
            return HttpResponse(account.balance)
        elif request.GET['getcashierinfo'] == 'hours_balance':
            return HttpResponse(account.hours_balance)
        else: # request.GET['getcashierinfo'] == 'acct_flags':
            template_file = 'accounting/snippets/acct_flags.html'
            return render_to_response(template_file, locals())

    if request.method == 'POST':
        form = forms.CashsheetForm(request.POST)
        if form.is_valid():
            form.save(entered_by=request.user)
            return HttpResponseRedirect(reverse('cashsheet_input'))
    else:
        form = forms.CashsheetForm()
    today = datetime.date.today()
    transactions = models.Transaction.objects.filter(
            timestamp__range=(today,today+datetime.timedelta(1)))
    can_reverse = True
    return render_to_response('accounting/cashsheet_input.html', locals(),
            context_instance=RequestContext(request))

# cashier permission is the first if
@user_passes_test(lambda u: u.is_authenticated())
def close_out(request, date=None):
    '''Page to double-check payment amounts'''
    if not m_models.cashier_permission(request):
        return HttpResponse('Sorry, you do not have cashier permission. %s' 
                             % request.META['REMOTE_ADDR'])

    if request.method=="POST":
        fixform = forms.CloseOutFixForm(request.POST)
        # hidden form shouldn't have errors, unless amount is bogus
        assert fixform.is_valid(), repr(fixform.errors)
        badtrans = fixform.cleaned_data['transaction']
        badtrans.fix_payment(fix_payment=fixform.cleaned_data['fix_payment'], 
                             entered_by=request.user)
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
        for trans in column['transactions']:
            if not trans.fixes_target():
                column['total'] += trans.fixed_payment_amount()

    closeoutfixform = forms.CloseOutFixForm()

    return render_to_response('accounting/close_out.html', locals(),
            context_instance=RequestContext(request))

@user_passes_test(lambda u: u.is_staff)
def cashsheet(request):
    ''' printable cash sheet for all active accounts '''
    accounts = m_models.Account.objects.active()
    return render_to_response('accounting/cashsheet.html', locals(),
            context_instance=RequestContext(request))

@user_passes_test(lambda u: u.is_staff)
def billing(request):
    ''' view to bill dues and deposits for all active accounts '''
    if request.method=='POST':
        form = forms.BillingForm(request.POST)
        assert form.is_valid(), repr(form.errors)
        total_billable_members = 0
        total_deposits = 0
        total_potential_bills = 0
        accounts = m_models.Account.objects.active()
        for account in accounts:
            billable_members = account.billable_member_count()
            total_billable_members += billable_members
            total_deposits += account.deposit
            potential_bill = (form.cleaned_data['amount_per_member'] * 
                                      billable_members)
            if form.cleaned_data['bill_type'] == 'O':   # O = Deposit
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
        form = forms.BillingForm()
    return render_to_response('accounting/billing.html', locals(),
            context_instance=RequestContext(request))

