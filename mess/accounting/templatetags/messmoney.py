from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def messmoney(value):
    " fix decimals and neg-parens, so 5.7 becomes 5.70 and -3 becomes (3.00) "
    if (type(value) is not Decimal) or (value and value._exp != -2):
        value = Decimal(value).quantize(Decimal('0.00'))
    if value < 0:
        return '(%s)' % -value
    else:
        return '%s' % value
