from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext, loader

from mess.membership import models as membership_models
from mess.profiles import forms, models

# TODO: profile page at /profiles/<username>

def add_contact(request, username, medium):
    context = RequestContext(request)
    referer = request.META.get('HTTP_REFERER', '')
    this_user = get_object_or_404(User, username=username)
    # use 'this_user' because context['user'] overrides logged-in user 
    context['this_user'] = this_user
    # medium may be 'address', 'phone', or 'email'
    context['medium'] = medium
    MediumForm = forms.form_map[medium]
    if request.method == 'POST':
        form = MediumForm(request.POST)
        referer = request.POST.get('referer')
        if form.is_valid():
            field_dict = {}
            for key in form.cleaned_data:
                if key not in ('DELETE', 'id'):
                    field_dict[key] = form.cleaned_data[key]
            try:
                match = form._meta.model.objects.get(**field_dict)
            except form._meta.model.DoesNotExist:
                match = None
            if match:
                medium_obj = match
            else:
                medium_obj = form.save()
            profile = this_user.get_profile()
            profile_medium_objs = {
                'address': profile.addresses,
                'phone': profile.phones,
                'email': profile.emails
            }[medium]
            profile_medium_objs.add(medium_obj)
            if referer:
                return HttpResponseRedirect(referer)
            else:
                # should direct to "profile" page when it works
                return HttpResponseRedirect(reverse('member', 
                        args=[this_user.username]))
    else:
        form = MediumForm()
    context['form'] = form
    context['referer'] = referer
    return render_to_response('profiles/add_contact.html', context)

def remove_contact(request, username, medium, id):
    context = RequestContext(request)
    this_user = get_object_or_404(User, username=username)
    context['this_user'] = this_user
    MediumClass = models.__getattribute__(medium.capitalize())
    context['medium'] = medium
    contact = get_object_or_404(MediumClass, id=id)
    context['contact'] = contact
    # syntax to actually remove it is ?medium=phone&target=1234&yes=yes
    # TODO: change to POST
    if request.method == 'POST':
        profile = this_user.get_profile()
        profile_medium_objs = {
            'address': profile.addresses,
            'phone': profile.phones,
            'email': profile.emails
        }[medium]
        listing = profile_medium_objs.all()
        for l in listing:
            if (str(l) == target):
                profile_medium_objs.remove(l)
                if l.userprofile_set.count() == 0: 
                    l.delete()
        # TODO: should redirect to referer
        return HttpResponseRedirect('/membership/members/'+username)
    # if missing the confirmation &yes=yes:
    return render_to_response('profiles/remove_contact.html', context)
    

def address(request, id):
    context = RequestContext(request)
    context['address'] = get_object_or_404(models.Address, id=id)
    template = get_template('contact/address.html')
    return HttpResponse(template.render(context))

def address_form(request, id=None):
    context = RequestContext(request)
    if id:
        address = get_object_or_404(models.Address, id=id)
    else:
        address = None
    if request.method == 'POST':
        form = forms.AddressForm(request.POST, instance=address)
        referer = request.POST['referer']
        if form.is_valid():
            new_address = form.save()
            if referer:
                return HttpResponseRedirect(referer)
            else:
                return HttpResponseRedirect(reverse('address', 
                        args=[new_address.id]))
    else:
        form = forms.AddressForm(instance=address)
    context['form'] = form
    referer = request.META.get('HTTP_REFERER', '')
    context['referer'] = referer
    template = get_template('contact/address_form.html')
    return HttpResponse(template.render(context))

def profiles_form(request, medium):
    context = RequestContext(request)
    MediumForm = forms.form_map[medium]
    index = request.GET.get('index')
    if index:
        form = MediumForm(prefix='%s-%s' % (medium, index))
    else:
        form = MediumForm()
    context['form'] = form
    template = loader.get_template('profiles/form.html')
    return HttpResponse(template.render(context))
