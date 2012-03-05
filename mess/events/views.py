from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from django.template import RequestContext
from django.template.loader import get_template
from django.conf import settings

from mess.events import models
from mess.membership import models as m_models
from mess.events import forms
from mess.core.permissions import has_elevated_perm

from datetime import datetime

def orientations(request):
    '''
    list of all orientations, the most recent first
    '''
    if not has_elevated_perm(request, 'events', 'add_orientation'):
        return HttpResponseRedirect(reverse('welcome'))

    context = RequestContext(request)

    context['upcoming_orientations'] = models.Orientation.objects.filter(datetime__gte=datetime.now()).order_by('-datetime')
    context['past_orientations'] = models.Orientation.objects.filter(datetime__lt=datetime.now()).order_by('-datetime')

    template = get_template('events/orientations.html')
    return HttpResponse(template.render(context))

def orientation_form(request, id=None):
    context = RequestContext(request)
    template = get_template('events/orientation_form.html')

    if request.method == "POST":
        if 'cancel' in request.POST:
            return HttpResponseRedirect(reverse('events-orientations'))
        else:
            if id:
                form = forms.OrientationForm(request.POST, instance=models.Orientation.objects.get(pk=id))
            else:
                form = forms.OrientationForm(request.POST)

            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse('events-orientations'))
    else:
        if id:
            form = forms.OrientationForm(instance=models.Orientation.objects.get(pk=id))
            context["edit"] = True
        else:
            form = forms.OrientationForm()

    context['orientation_form'] = form
    return HttpResponse(template.render(context))

def locations(request):
    '''
    list of all event locations
    '''
    if not has_elevated_perm(request, 'locations', 'add_location'):
        return HttpResponseRedirect(reverse('welcome'))

    context = RequestContext(request)
    context['locations'] = models.Location.objects.order_by('-active', 'name')

    template = get_template('events/locations.html')
    return HttpResponse(template.render(context))

def location_form(request, id=None):
    context = RequestContext(request)
    template = get_template('events/location_form.html')

    if request.method == "POST":
        if 'cancel' in request.POST:
            return HttpResponseRedirect(reverse('events-locations'))
        else:
            if id:
                form = forms.LocationForm(request.POST, instance=models.Location.objects.get(pk=id))
            else:
                form = forms.LocationForm(request.POST)

            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse('events-locations'))
    else:
        if id:
            form = forms.LocationForm(instance=models.Location.objects.get(pk=id))
            context["edit"] = True
        else:
            form = forms.LocationForm()

    context['location_form'] = form
    return HttpResponse(template.render(context))
