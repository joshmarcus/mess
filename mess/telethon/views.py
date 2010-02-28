from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.template.loader import get_template

def index(request):
    context = RequestContext(request)
    template = get_template('fundraising/index.html')
    return HttpResponse(template.render(context))

