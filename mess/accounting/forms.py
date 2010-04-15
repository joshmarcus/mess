from decimal import Decimal
from decimal import InvalidOperation

from django import forms
from django.forms.models import modelformset_factory
from django.utils.safestring import mark_safe
from mess.autocomplete import AutoCompleteWidget

from mess.accounting import models
from mess.membership import models as m_models

class SelectAfterAjax(forms.Select):
    ''' select widget that renders blank, so ajax can fill its choices '''
    def render(self, name, value, attrs=None, choices=()):
        final_attrs = self.build_attrs(attrs, name=name)
        return mark_safe(u'<select%s>' % forms.util.flatatt(final_attrs) +
            u'<option value="" selected="selected">------</option></select>')

class TransactionForm(forms.ModelForm):
    class Meta:
        model = models.Transaction
        exclude = ('account_balance','entered_by')
    account = forms.ModelChoiceField(m_models.Account.objects.all(),
        widget=AutoCompleteWidget('account_spiffy',
            view_name='membership-autocomplete', canroundtrip=True))
    member = forms.ModelChoiceField(m_models.Member.objects.all(),
        widget=SelectAfterAjax(), required=False)

class AfterHoursForm(forms.Form):
    account = forms.ModelChoiceField(m_models.Account.objects.all(),
        widget=AutoCompleteWidget('account_spiffy',
            view_name='membership-autocomplete', canroundtrip=True))
    purchases = forms.CharField(max_length=256, widget=forms.Textarea(attrs={'rows':3}),
                               help_text='e.g: 2.25 + .95*3 + 4.9') # max_length matches trans model notes field
    purchase_total = forms.DecimalField(required=False, widget=forms.HiddenInput())
    
    def clean(self):
        cleaned_data = self.cleaned_data
        try:
            purchases = cleaned_data.get("purchases").split('+')
            total = Decimal(0)
            for st in purchases:
                if '*' in st:
                    multiplicands = st.split('*')
                    if len(multiplicands) != 2:
                        raise forms.ValidationError("too much multiplication")
                    d = (Decimal(multiplicands[0].strip()) * 
                         Decimal(multiplicands[1].strip()))
                else:
                    d = Decimal(st.strip())
                if (d._exp < -2):
                    raise forms.ValidationError("no more than 2 #s after decimal, pls.")
                total += d
        except (InvalidOperation, AttributeError):
            raise forms.ValidationError("Purchases field incorrect.")

        cleaned_data["purchase_total"] = total
        return cleaned_data

class EBTForm(forms.Form):
    """  Okay, so here come some big comments, says Paul.
    So, you display this form on the page, but it's got a couple weird
    fields.  The ebtbulkamount is just for informational purposes, so the
    cashier and the user know what's going on.  It's marked 'disabled'
    so the user can't edit it, but it seems like on my browser (Opera)
    that also means it doesn't get sent back to the server.  Anyway,
    the server doesn't need the field, but if there's a form error that
    could be a bug where your ebtbulkamount disappears.  Nevermind.

    The template sets the magic js varible EBTBULKORDERS, which triggers
    ebtautocalc features of cashier.js.  That is, whenever you edit the
    purchases amount, cashier.js runs autocalc and recomputes your EBT total.

    The EBT total, by the way, is also just for informational purpose.

    Okay, first things first, when you enter the account name and choose
    from the autocomplete, its callback does an eval() of whatever came from
    templates/accounting/snippets/ebtbulkorders.js
    This template-js should make it prompt you Yes/No for each EBT bulk order
    you have.  Each time you hit OK/Yes, it adds that amount to ebtbulkamount
    informational field, and appends the FK of the EBTBO onto the field that
    does the real work, ebtbulkorders.  Then you make your transaction, and 
    the cashier knows how much to charge the EBT card because it's shown
    in the ebttotalamount informational line.

    When you hit 'submit', the form takes the regular_sales amount and
    charges it as an EBT transaction (if non-zero).  Then it adds up
    all the EBT bulk orders based on the FKs in the ebtbulkorders hidden field
    and charges them as a big EBT transaction.  When these are charged,
    their paid_by_transaction is set to the current transaction, so
    they will no longer show up in the ebtbulkorders_set.unpaid manager.

    So there.
    
    """
    account = forms.ModelChoiceField(m_models.Account.objects.all(), 
                 widget=AutoCompleteWidget('account_spiffy', 
                     view_name='membership-autocomplete',canroundtrip=True))
    regular_sales = forms.DecimalField(required=False)
    # the EBT bulk orders field will be filled by javascript, with the
    # FKs of any EBT bulk orders to be paid for as part of this purchase.
    # It's a comma-delimited list of FKs, like "23,478,1573"
    ebtbulkorders = forms.CharField(widget=forms.HiddenInput(),required=False)
    ebtbulkamount = forms.CharField(initial='None', required=False,
                widget=forms.TextInput(attrs={'disabled':'true'}))

    def clean_ebtbulkorders(self):
        if self.cleaned_data['ebtbulkorders'] == '':
            return []
        ebtbos = []
        for fk in self.cleaned_data['ebtbulkorders'].split(','):
            try:
                ebtbo = models.EBTBulkOrder.objects.get(id=int(fk))
            except:
                raise forms.ValidationError('invalid EBT bulk fk %s' % fk)
            if ebtbo.account != self.cleaned_data['account']:
                raise forms.ValidationError('wrong account EBT bulk fk %s' % fk)
            ebtbos.append(ebtbo)
        return ebtbos

    def save(self, entered_by):
        regular_sales = self.cleaned_data['regular_sales']
        ebtbulkorders = self.cleaned_data['ebtbulkorders']
        bulktotal = sum([order.amount for order in ebtbulkorders])
        if regular_sales:
            new_ebt = models.Transaction.objects.create(
                        account=self.cleaned_data['account'],
                        entered_by=entered_by, purchase_type='P',
                        payment_type='E', purchase_amount=regular_sales,
                        payment_amount=regular_sales)
        if bulktotal:
            new_ebt = models.Transaction.objects.create(
                        account=self.cleaned_data['account'],
                        entered_by=entered_by, purchase_type='B',
                        payment_type='E', purchase_amount=bulktotal,
                        payment_amount=bulktotal)

class HoursBalanceForm(forms.ModelForm):
    class Meta:
        model = models.HoursTransaction
        exclude = ('hours_balance','entered_by','note')
    account = forms.ModelChoiceField(m_models.Account.objects.all(),
        widget=AutoCompleteWidget('account_spiffy',
            view_name='membership-autocomplete', canroundtrip=True))
    hours_balance_change = forms.CharField(
                widget=forms.TextInput(attrs={'size':'4'}))

    def clean_hours_balance_change(self):
        value = str(self.cleaned_data['hours_balance_change'])
        if value[0] == '(' and value[-1] == ')':
            value = '-'+value[1:-1]
        try:
            return Decimal(value)
        except:
            raise forms.ValidationError('invalid hours balance')

class ReverseForm(forms.Form):
    reverse_id = forms.ModelChoiceField(models.Transaction.objects.all(),
            widget=forms.HiddenInput())
    reverse_reason = forms.CharField(widget=forms.HiddenInput())

    def save(self, entered_by):
        trans = self.cleaned_data['reverse_id']
        trans.reverse(entered_by, self.cleaned_data['reverse_reason'])
        return trans

class CashsheetForm(forms.Form):
    account = forms.ModelChoiceField(m_models.Account.objects.all(),
            widget=AutoCompleteWidget('account_spiffy',
                view_name='membership-autocomplete', canroundtrip=True))
    misc = forms.DecimalField(required=False,
                widget=forms.TextInput(attrs={'size':'4'}))
    deposit = forms.DecimalField(required=False,
                widget=forms.TextInput(attrs={'size':'4'}))
    bulk_orders = forms.DecimalField(required=False,
                widget=forms.TextInput(attrs={'size':'4'}))
    regular_sales = forms.DecimalField(required=False,
                widget=forms.TextInput(attrs={'size':'4'}))
    credit_debit = forms.DecimalField(required=False,
                widget=forms.TextInput(attrs={'size':'4'}))
    check_mo = forms.DecimalField(required=False,
                widget=forms.TextInput(attrs={'size':'4'}))
    note = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        if kwargs.has_key('tofix'):
            tofix = kwargs.pop('tofix')
            data = {'account':tofix.account.id}
            if tofix.purchase_type == 'S':
                data['misc'] = tofix.purchase_amount
            elif tofix.purchase_type == 'O':
                data['deposit'] = tofix.purchase_amount
            elif tofix.purchase_type == 'B':
                data['bulk_orders'] = tofix.purchase_amount
            elif tofix.purchase_type == 'P':
                data['regular_sales'] = tofix.purchase_amount
            if tofix.payment_type == 'C':
                data['credit_debit'] = tofix.payment_amount
            elif tofix.payment_type == 'K':
                data['check_mo'] = tofix.payment_amount
            super(CashsheetForm, self).__init__(data, *args, **kwargs)
        else:
            super(CashsheetForm, self).__init__(*args, **kwargs)

    def clean(self):
        ''' Weird transactions need notes '''
        note = self.cleaned_data.get('note')
        for value in self.cleaned_data.values():
            if type(value) is Decimal and value < 0 and not note:
                raise forms.ValidationError('note required for negative entry')
        if self.cleaned_data.get('misc') and not note:
            raise forms.ValidationError('note required for misc transaction')
        return self.cleaned_data

    def save(self, entered_by=None):
        purchases = [(purchase_type, self.cleaned_data[fieldname])
            for purchase_type, fieldname in (
                ('S', 'misc'),
                ('O', 'deposit'),
                ('B', 'bulk_orders'),
                ('P', 'regular_sales'))
            if self.cleaned_data[fieldname]]
        payments = [(payment_type, self.cleaned_data[fieldname])
            for payment_type, fieldname in (
                ('C', 'credit_debit'),
                ('K', 'check_mo'))
            if self.cleaned_data[fieldname]]
        if len(purchases) == len(payments) == 1:
            trans = models.Transaction(account=self.cleaned_data['account'],
                                       payment_type=payments[0][0],
                                       payment_amount=payments[0][1],
                                       purchase_type=purchases[0][0],
                                       purchase_amount=purchases[0][1],
                                       note=self.cleaned_data['note'],
                                       entered_by=entered_by)
            trans.save()
        else:
            for purchase in purchases:
                trans = models.Transaction(account=self.cleaned_data['account'],
                                       purchase_type=purchase[0],
                                       purchase_amount=purchase[1],
                                       note=self.cleaned_data['note'],
                                       entered_by=entered_by)
                trans.save()
            for payment in payments:
                trans = models.Transaction(account=self.cleaned_data['account'],
                                       payment_type=payment[0],
                                       payment_amount=payment[1],
                                       note=self.cleaned_data['note'],
                                       entered_by=entered_by)
                trans.save()

class CloseOutForm(forms.ModelForm):
    class Meta:
        model = models.Reconciliation

class BillingForm(forms.Form):
    bill_type = forms.ChoiceField(
                choices=(('O','Member Equity'),('U','Dues')))
    amount_per_member = forms.DecimalField(initial=20)
    max_deposit_per_member = forms.DecimalField(initial=100)

class CashSheetFormatForm(forms.Form):
    row_height = forms.DecimalField(initial=2.5,
                widget=forms.TextInput(attrs={'size':'4'}))
    rows_per_page = forms.IntegerField(initial=25,
                widget=forms.TextInput(attrs={'size':'4'}))

StoreDayFormSet = modelformset_factory(models.StoreDay, extra=1, can_delete=True)
class StoreDayForm(forms.ModelForm):
    class Meta:
        model = models.StoreDay

class EBTBulkOrderForm(forms.ModelForm):
    class Meta:
        model = models.EBTBulkOrder
        exclude = ("paid_by_transaction",)

