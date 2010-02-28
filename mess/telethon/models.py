from django.contrib.auth.models import User
from django.db import models
from mess.accounting.models import Transaction
from mess.membership.models import Member

LOAN_TERMS = (
    ('a', 'Loan Term A'),
    ('b', 'Loan Term B'),
    ('c', 'Loan Term C'),
)

class Call(models.Model):
    caller = models.ForeignKey(User)
    callee = models.ForeignKey(Member)
    note = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    do_not_call = models.BooleanField()
    pledge_amount = models.DecimalField(max_digits=8, decimal_places=2,
        default=0, blank=True)
    # XXX: other pledge stuff?
    loan_term = models.CharField(max_length=1, choices=LOAN_TERMS, default='a', 
        blank=True)
    loan = models.ForeignKey(Transaction, null=True, blank=True)

    class Meta:
        permissions = (
            ('can_fundraise', 'Can fundraise'),
        )

