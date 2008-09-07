import re
from django import template
from django.core.urlresolvers import RegexURLResolver
from mess import urls

register = template.Library()

@register.simple_tag
def active_class(request, pattern):
    '''
    Return ' class="active"' if request.path starts with pattern, else return 
    an empty string.  

    *request* (required): an HttpRequest object
    *pattern* (optional): a string
    '''
    #path = request.path[1:] # Strip the leading /

    #if pattern == '':
    #    return ''

    #return request.path

    if request.path.startswith(pattern):
        return ' class="active"'
    else:
        return ''
