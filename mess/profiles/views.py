from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from django.contrib.auth.models import User
from mess.profiles.models import Address
from mess.profiles.forms import PhoneForm

def add_phone(request, username):
	c = RequestContext(request)
	c['user'] = get_object_or_404(User, username=username)
	c['userprofile'] = c['user'].get_profile()
	if request.method == 'POST':
		form = PhoneForm(request.POST)
		if form.is_valid:
			form.save()
			c['userprofile'].phones.add(form.instance)
			return HttpResponseRedirect('/membership/members/'+username)
	else:
		c['form'] = PhoneForm()
	return render_to_response('profiles/add_phone.html', c)

def remove_phone(request, username):
	return HttpResponse('remove phone is not written yet')

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
