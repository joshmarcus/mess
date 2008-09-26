from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext, loader

from django.contrib.auth.models import User
from mess.profiles.models import Address, Phone, Email
from mess.profiles.forms import AddressForm, PhoneForm, EmailForm
from mess.profiles import forms

def add_contact(request, username, medium):
    # FIXME this should request.GET.get('medium') just like remove_contact does
    # medium may be 'address', 'phone', or 'email'
    c = RequestContext(request)
    c['user'] = get_object_or_404(User, username=username)
    c['userprofile'] = p = c['user'].get_profile()
    c['medium'] = medium
    mediumform = {'address':AddressForm,'phone':PhoneForm,'email':EmailForm}[medium]
    profilemediumlist = {'address':p.addresses,'phone':p.phones,'email':p.emails}[medium]
    if request.method == 'POST':
        form = mediumform(request.POST)
        if form.is_valid:
            form.save()
            profilemediumlist.add(form.instance)
            # TODO: should redirect to referer
            return HttpResponseRedirect('/membership/members/'+username)
    c['form'] = mediumform()
    return render_to_response('profiles/add_contact.html', c)

def remove_contact(request, username):
    context = RequestContext(request)
    context['user'] = get_object_or_404(User, username=username)
    p = context['userprofile'] = context['user'].get_profile()
    medium = context['medium'] = request.GET.get('medium')
    target = context['target'] = request.GET.get('target')
    profilemediumlist = {'address':p.addresses,'phone':p.phones,'email':p.emails}[medium]
    # syntax to actually remove it is ?medium=phone&target=1234&yes=yes
    if request.GET.has_key('yes'):
        listing = profilemediumlist.all()
        for l in listing:
            if (str(l) == target):
                profilemediumlist.remove(l)
                if l.userprofile_set.count() == 0: 
                    l.delete()
        # TODO: should redirect to referer
        return HttpResponseRedirect('/membership/members/'+username)
    # if missing the confirmation &yes=yes:
    return render_to_response('profiles/remove_contact.html', context)
    

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

# can this be made simpler?
def formset_form(request, prefix, index=-1):
    context = RequestContext(request)
    FormClass = forms.form_map[prefix]
    if index == -1:
        form = FormClass()
    else:
        form = FormClass(prefix='%s-%s' % (prefix, index))
    context['form'] = form
    template = loader.get_template('profiles/formset_form.html')
    return HttpResponse(template.render(context))
