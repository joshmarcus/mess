from django.contrib.auth.models import User
from django.db import models
from mess.accounting.models import Transaction
from mess.membership.models import Member

LOAN_TERMS = (
    ('D', 'donation'),
    ('F', '5 year loan with no interest'),
    ('G', '5 year loan at 3% simple interest'),
    ('T', '10 year loan with no interest'),
    ('U', '10 year loan at 3% simple interest'),
)

LOAN_TERMS_BRIEF = {
    'D': 'donation',
    'F': '5y loan',
    'G': '5y3% loan',
    'T': '10y loan',
    'U': '10y3% loan',
}

class Call(models.Model):
    caller = models.ForeignKey(User)
    callee = models.ForeignKey(Member)
    note = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    do_not_call = models.BooleanField()
    pledge_amount = models.DecimalField(max_digits=8, decimal_places=2,
        blank=True, null=True)
    # XXX: other pledge stuff?
    loan_term = models.CharField(max_length=1, choices=LOAN_TERMS, blank=True, 
        help_text='By selecting a donation or loan term, the pledge amount will be immediately deducted from the member\'s Mariposa account.  For a pledge to be paid in the future, just leave this blank.')
    loan = models.ForeignKey(Transaction, null=True, blank=True)

    def loan_term_brief(self):
        if self.loan_term:
            return LOAN_TERMS_BRIEF[self.loan_term]

    class Meta:
        permissions = (
            ('can_fundraise', 'Can fundraise'),
        )
