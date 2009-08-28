from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.template.loader import get_template

def welcome(request):
    context = RequestContext(request)
    template = get_template('welcome.html')
    return HttpResponse(template.render(context))
