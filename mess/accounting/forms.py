from django import newforms as forms

from accounting.models import Transaction, get_account_balance
from accounting.models import OTHER_CREDIT_CHOICES, OTHER_DEBIT_CHOICES
from accounting.models import CASHIER_CREDIT_CHOICES, CASHIER_DEBIT_CHOICES
from accounting.models import COMMON_CREDIT_CHOICES, COMMON_DEBIT_CHOICES
from accounting.models import CREDIT_CHOICES, DEBIT_CHOICES



class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction

    def clean_balance(self, credit=0, debit=0):
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
        
    #def save(self):
    #    f = self
    #    debit = f.cleaned_data['debit']
    #    debit_type = f.cleaned_data['debit_type']
    #    credit = f.cleaned_data['credit']
    #    credit_type = f.cleaned_data['credit_type']
    #    if credit_type != 'N':
    #        f.cleaned_data['debit_type'] = 'N'
    #        f.cleaned_data['debit'] = 0
    #        f.save()
    #    if debit_type != 'N':
    #        f.cleaned_data['credit_type'] = 'N'
    #        f.cleaned_data['credit'] = 0
    #        f.cleaned_data['debit_type'] = debit_type
    #        f.cleaned_data['debit'] = debit
    #        f.save()


class NewTransactionForm(forms.Form):
    
    role = 'Cashier'
    if role == 'Cashier':
        CREDIT_CHOICES = CASHIER_CREDIT_CHOICES
        DEBIT_CHOICES = CASHIER_DEBIT_CHOICES
    elif role == 'Member':
        CREDIT_CHOICES = MEMBER_CREDIT_CHOICES
        DEBIT_CHOICES = (('','None'),)

    account = forms.IntegerField()
    member = forms.IntegerField()
    credit_type = forms.ChoiceField(required=False, choices=CREDIT_CHOICES)
    credit_amount = forms.IntegerField(required=False)
    debit_type = forms.ChoiceField(required=False, choices=DEBIT_CHOICES)
    debit_amount = forms.IntegerField(required=False)
    note = forms.CharField(required=False)
    ref = forms.IntegerField(required=False)

    def clean_account(self):
        account = self.clean_data.get('account')
        try:
            Account.objects.get(id=account)
        except DoesNotExist:
            print 'Do what now?'
        return account

    def clean_member(self):
        member = self.clean_data.get('member')
        try:
            Account.objects.get(id=account).members.get(id=member)
            return member
        except DoesNotExist:
            try:
                Member.objects.get(id=member)
            except DoesNotExist:
                pass
                #raise forms.ValidationError('There is no member 
                #                            with an id of %s' % self.member)
        return member

    #def clean(self):
    #    # Do I need to call these? - dv
    #    clean_account
    #    clean_member
    #    if  

    def save(self):
        pass
    


