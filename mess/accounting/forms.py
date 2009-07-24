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
