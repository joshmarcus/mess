from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.template.loader import get_template

def welcome(request):
    context = RequestContext(request)
    # TODO: stick feedparser stuff in context['rss_list']
    template = get_template('welcome.html')
    return HttpResponse(template.render(context))
