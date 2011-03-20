from django.core import serializers
from django.http import HttpResponse
from django.template import RequestContext
from django.template.loader import get_template
import django.conf as conf

def index(request):
    # verify secret
    if not request.GET.has_key('secret') or request.GET['secret'] != conf.settings.IS4C_SECRET or conf.settings.IS4C_SECRET == 'fakesecret':
        return HttpResponse('Wrong IS4C secret!!')

    if request.method == 'POST':
        pass
    return HttpResponse('{"json":"yes!x"}', mimetype='application/json')
