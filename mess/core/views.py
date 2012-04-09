import feedparser
import socket

from django.contrib.auth import forms as auth_forms
from django.contrib.auth import authenticate, login
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.db.models.options import FieldDoesNotExist
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.template import RequestContext
from django.template.loader import get_template

from mess.forum import models as f_models


MAX_ENTRIES = 5    # maximum number of rss items to show on welcome page
TIMEOUT = 5  # timeout in seconds in case rss server is down
NORMAL_TIMEOUT = 30 # a sane value, I think

def welcome(request):
    context = RequestContext(request)

    if request.user.is_authenticated():
        entries = cache.get('entries')
        if not entries:
            socket.setdefaulttimeout(TIMEOUT)
            feed = feedparser.parse("http://www.mariposa.coop/?feed=rss2")
            socket.setdefaulttimeout(NORMAL_TIMEOUT)
            entries = feed.entries[:MAX_ENTRIES]
            cache.set('entries', entries, 300)
        context['rss_entries'] = entries

        # not sure why we're getting the FieldDoesNotExist error with locmem
        # but this try/except block seems to handle it
        try:
            threads = cache.get('threads')
        except FieldDoesNotExist:
            threads = None
        if not threads:
            threads = f_models.Post.objects.threads()[:MAX_ENTRIES]
            cache.set('threads', threads)
        context['threads'] = threads
        template = get_template('welcome.html')
    else:
        if request.method == 'POST':
            auth_form = auth_forms.AuthenticationForm(data=request.POST)
            if auth_form.is_valid():
                user = auth_form.get_user()
                login(request, user)
                redirect = request.POST.get('next', reverse('welcome'))
                #raise Exception, auth_form.cleaned_data
                return HttpResponseRedirect(redirect)
        else:
            auth_form = auth_forms.AuthenticationForm()
            context['next'] = request.GET.get('next', '')
        context['form'] = auth_form
        template = get_template('welcome-anon.html')
    return HttpResponse(template.render(context))
