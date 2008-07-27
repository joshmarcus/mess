from django.shortcuts import render_to_response
from django.template import RequestContext

def welcome(request):
    page_name = 'Welcome'
    return render_to_response('welcome.html', locals(),
                                context_instance=RequestContext(request))

def styleguide(request):
    context = RequestContext(request)
    context['title'] = 'Mess Styleguide' 
    template = get_template('styleguide.html')
    return HttpResponse(template.render(context))



def thanks(request):
    context = {}
    context['page_name'] = 'Thank You'
    try:
        redirect = request.META.get('HTTP_REFERER')
    except:
        redirect = '/'
    return render_to_response('thanks.html', context,
                                context_instance=RequestContext(request))

