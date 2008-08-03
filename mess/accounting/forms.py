from django import forms

from mess.accounting.models import Transaction, Reconciliation
from mess.accounting.models import get_credit_choices, get_debit_choices
from mess.accounting.models import get_account_balance, get_todays_transactions


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction

    def clean_balance(self, credit=0, debit=0):
		# This line is the cause of ticket #30.  If 'member' is undefined, this
		# raises errors.
		#    I'd like to find where this is called from, to see if the
		# problem could be handled before it gets to this function, but 
		# it seems to be called by Django Form-Handling itself??  --Paul 8/3/08
         return (get_account_balance(self.cleaned_data.get('member').id) -
                self.cleaned_data.get('credit') +
                self.cleaned_data.get('debit')
                )
        
    def clean(self):
        debit = self.cleaned_data['debit']
        debit_type = self.cleaned_data['debit_type']
        credit = self.cleaned_data['credit']
        credit_type = self.cleaned_data['credit_type']
        if debit != 0 and debit_type == 'N':
            raise Exception, 'You need to select a "Debit Type"'
        if credit != 0 and credit_type == 'N':
            raise Exception, 'You need to select a "Credit Type"'
        if debit == 0 and credit == 0:
            raise Exception, 'You need to enter the transaction amount'
        if debit == 0 and debit_type != 'N':
            raise Exception, ('A "Debit Amount" is required for a "Debit \
                                Type" of %s' % debit_type)
        if credit == 0 and credit_type != 'N':
            raise Exception, ('A "Credit Amount" is required for a "Credit \
                                Type" of %s' % self.get_debit_type_display)
        return self.cleaned_data
        
    
class CloseOutForm(forms.ModelForm):
    class Meta:
        model = Reconciliation
