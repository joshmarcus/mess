from django.contrib.auth.models import User
from django.db import models
from mess.accounting.models import Transaction
from mess.membership.models import Member

class Call(models.Model):
    caller = models.ForeignKey(User)
    callee = models.ForeignKey(Member)
    note = models.TextField(blank=True)
    timestamp = models.DateTimeField()
    do_not_call = models.BooleanField()
    pledge_amount = models.DecimalField(max_digits=8, decimal_places=2,
        default=0, blank=True)
    # XXX: other pledge stuff?

    class Meta:
        permissions = (
            ('can_fundraise', 'Can fundraise'),
        )

LOAN_TERMS = (
    ('a', 'Loan Term A'),
    ('b', 'Loan Term B'),
    ('c', 'Loan Term C'),
)

class Loan(models.Model):
    term = models.CharField(max_length=1, choices=LOAN_TERMS,
            default='a')
    transaction = models.ForeignKey(Transaction)

