import re
from django import template
from django.core.urlresolvers import RegexURLResolver
from mess import urls

register = template.Library()

@register.simple_tag
def active(request, pattern=''):
    '''
    Return '-active' if *pattern* matches *request.path* (the current location
    in the browser). The empty string is returned otherwise.  The pattern is
    either given by the user or taken from the URLconf.

    *request* (required): an HttpRequest object
    *pattern* (optional): a regular expression string
    '''
    path = request.path[1:] # Strip the leading /

    if pattern == '':
        return ''

    if re.search(pattern, path):
        return '-active'
    else:
        return ''