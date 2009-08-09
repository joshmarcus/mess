from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def messmoney(value, arg='balance'):
    """
    Fix decimals and neg-parens, so 5.7 becomes 5.70 and -3 becomes (3.00).
    With arg='payment', 5.7 becomes (5.70).
    """
    if value is None or value == '':
        return value
    if (type(value) is not Decimal) or (value and value._exp != -2):
        value = Decimal(value).quantize(Decimal('0.00'))
    if arg == 'payment':
        value = -value
    if value < 0:
        return '(%s)' % -value
    else:
        return '%s' % value
