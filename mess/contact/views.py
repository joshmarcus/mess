from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import simplejson

from mess.utils.search import search_for_string

from mess.contact.models import Address
from mess.contact.forms import AddressForm

def search_for(request):
    if request.GET.has_key('string')  and request.GET.has_key('search'):
        string = request.GET.get('string')
        search = request.GET.get('search')
        dict = search_for_string(search, string)
    return HttpResponse(simplejson.dumps(dict),
                        mimetype='application/javascript')

def address(request, id):
    context = {}
    try:
        address = Address.objects.get(id=id)
    except Address.DoesNotExist:
        return Http404
    context['address'] = address
    return render_to_response('contact/address.html', context,
                            context_instance=RequestContext(request))

def address_add(request):
    context = {}
    form = AddressForm()
    context['form'] = form
    return render_to_response('contact/address_edit.html', context,
                            context_instance=RequestContext(request))

def address_edit(request, id):
    context = {}
    try:
        address = Address.objects.get(id=id)
    except Address.DoesNotExist:
        return Http404
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
    else:
        form = AddressForm(instance=address)
    context['address'] = address
    context['form'] = form
    return render_to_response('contact/address_edit.html', context,
                            context_instance=RequestContext(request))
