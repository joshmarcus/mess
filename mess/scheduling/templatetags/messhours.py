from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def messhours(value, arg=''):
    """
    Show hours in a reasonable way. 

    If arg is blank (or anything but unexcused), we just return the hours owed or banked.
    If arg=='unexcused' then only return the hours that are unexcused.
    """
    if value is None or value == '':
        return value
    if (type(value) is not Decimal) or (value and value._exp != -2):
        value = Decimal(value).quantize(Decimal('0.00')) 

    if arg=='unexcused':
        return '%s.00' % value.to_integral_value()
    else:
	    value -= value.to_integral_value()
	    value = value.shift(2)
	    return '%s' % abs(value)
