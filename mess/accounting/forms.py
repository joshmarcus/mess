from django import forms

from mess.accounting import models
from mess.accounting.models import Transaction, Reconciliation

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        exclude = ('account_balance',)

class CloseOutForm(forms.ModelForm):
    class Meta:
        model = Reconciliation
