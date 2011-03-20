from django.core import serializers
from django.http import HttpResponse
from django.template import RequestContext
from django.template.loader import get_template

def index(request):
    if request.method == 'POST':
        pass
    return HttpResponse('{"json":"yes!"}', mimetype='application/json')
