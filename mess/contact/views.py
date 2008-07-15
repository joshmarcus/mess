from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.template.loader import get_template
from django.utils import simplejson

from mess.utils.search import search_for_string

from mess.contact.models import Address
from mess.contact.forms import AddressForm
from mess.people.models import Person

def search_for(request):
    if request.GET.has_key('string')  and request.GET.has_key('search'):
        string = request.GET.get('string')
        search = request.GET.get('search')
        dict = search_for_string(search, string)
    return HttpResponse(simplejson.dumps(dict),
                        mimetype='application/javascript')

def address(request, id):
    context = RequestContext(request)
    context['address'] = get_object_or_404(Address, id=id)
    template = get_template('contact/address.html')
    return HttpResponse(template.render(context))

def address_form(request, id=None):
    context = RequestContext(request)
    if id:
        address = get_object_or_404(Address, id=id)
    else:
        address = None
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        referer = request.POST['referer']
        if form.is_valid():
            new_address = form.save()
            if referer:
                return HttpResponseRedirect(referer)
            else:
                return HttpResponseRedirect(reverse('address', 
                        args=[new_address.id]))
    else:
        form = AddressForm(instance=address)
    context['form'] = form
    referer = request.META.get('HTTP_REFERER', '')
    context['referer'] = referer
    template = get_template('contact/address_form.html')
    return HttpResponse(template.render(context))

