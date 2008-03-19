from django.shortcuts import render_to_response
from django.template import RequestContext

def welcome(request):
    page_name = 'Welcome'
    return render_to_response('welcome.html', locals(),
                                context_instance=RequestContext(request))

