from django.contrib.auth import forms as auth_forms
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.template.loader import get_template

from mess.forum import models as f_models
import feedparser
import socket

def welcome(request):
    MAX_ENTRIES = 5    # maximum number of rss items to show on welcome page
    TIMEOUT = 5  # timeout in seconds in case rss server is down
    NORMAL_TIMEOUT = 30 # a sane value, I think

    context = RequestContext(request)

    socket.setdefaulttimeout(TIMEOUT)
    feed = feedparser.parse("http://www.mariposa.coop/?feed=rss2")
    socket.setdefaulttimeout(NORMAL_TIMEOUT)
    entries = feed.entries[:MAX_ENTRIES]
    context['rss_entries'] = entries

    context['form'] = auth_forms.AuthenticationForm()

    threads = f_models.Post.objects.threads()
    context['threads'] = threads[:MAX_ENTRIES]

    template = get_template('welcome.html')
    return HttpResponse(template.render(context))

