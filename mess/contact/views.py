from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
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
    context = {}
    try:
        address = Address.objects.get(id=id)
    except Address.DoesNotExist:
        return Http404
    context['address'] = address
    return render_to_response('contact/address.html', context,
                            context_instance=RequestContext(request))

def address_add(request, person_id):
    context = RequestContext(request)
    referer = request.META['HTTP_REFERER']
    if request.method == 'POST':
        form = AddressForm(request.POST)
        referer = request.POST['referer']
        if form.is_valid():
            new_address = form.save()
            person = Person.objects.get(id=person_id)
            person.addresses.add(new_address)
            return HttpResponseRedirect(referer)
    else:
        form = AddressForm()
    context['form'] = form
    context['referer'] = referer
    template = get_template('contact/address_edit.html')
    return HttpResponse(template.render(context))

def address_edit(request, id):
    context = RequestContext(request)
    referer = request.META['HTTP_REFERER']
    try:
        address = Address.objects.get(id=id)
    except Address.DoesNotExist:
        return Http404
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        referer = request.POST['referer']
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(referer)
    else:
        form = AddressForm(instance=address)
    context['address'] = address
    context['form'] = form
    context['referer'] = referer
    template = get_template('contact/address_edit.html')
    return HttpResponse(template.render(context))

