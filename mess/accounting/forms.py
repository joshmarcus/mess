from decimal import Decimal
from decimal import InvalidOperation

from django import forms
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
                               help_text='separate purchases with +') # max_length matches trans model notes field
    purchase_total = forms.DecimalField(required=False, widget=forms.HiddenInput())
    
    def clean(self):
        cleaned_data = self.cleaned_data
        try:
            purchases = cleaned_data.get("purchases").split('+')
            total = Decimal(0)
            for st in purchases:
                d = Decimal(st.strip())
                if (d._exp < -2):
                    raise forms.ValidationError("no more than 2 #s after decimal, pls.")
                total += d
        except (InvalidOperation, AttributeError):
            raise forms.ValidationError("Purchases field incorrect.")

        cleaned_data["purchase_total"] = total
        return cleaned_data

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
    after_hours = forms.DecimalField(required=False,
                widget=forms.TextInput(attrs={'size':'4'}))
    regular_sales = forms.DecimalField(required=False,
                widget=forms.TextInput(attrs={'size':'4'}))
    credit_debit = forms.DecimalField(required=False,
                widget=forms.TextInput(attrs={'size':'4'}))
    check_mo = forms.DecimalField(required=False,
                widget=forms.TextInput(attrs={'size':'4'}))
    note = forms.CharField(required=False)

    def save(self, entered_by=None):
        purchases = [(purchase_type, self.cleaned_data[fieldname])
            for purchase_type, fieldname in (
                ('S', 'misc'),
                ('O', 'deposit'),
                ('B', 'bulk_orders'),
                ('A', 'after_hours'),
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

class CloseOutFixForm(forms.Form):
    transaction = forms.ModelChoiceField(models.Transaction.objects.all(),
        widget=forms.HiddenInput)
    fix_payment = forms.DecimalField(widget=forms.HiddenInput)

class BillingForm(forms.Form):
    bill_type = forms.ChoiceField(
                choices=(('O','Deposit'),('U','Dues')))
    amount_per_member = forms.DecimalField(initial=20)
    max_deposit_per_member = forms.DecimalField(initial=100)

class CashSheetFormatForm(forms.Form):
    row_height = forms.DecimalField(initial=2.5,
                widget=forms.TextInput(attrs={'size':'4'}))
    rows_per_page = forms.IntegerField(initial=25,
                widget=forms.TextInput(attrs={'size':'4'}))

