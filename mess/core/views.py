from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.template.loader import get_template
import feedparser

def welcome(request):
    MAX_ENTRIES = 5    # maximum number of rss items to show on welcome page
    context = RequestContext(request)

    # just passing the entries, so we don't have too many
    #feed = feedparser.parse("http://www.mariposa.coop/?feed=rss2")
    #if (len(feed.entries) > MAX_ENTRIES):
    #    entries = feed.entries[:MAX_ENTRIES]
    #else: 
    #    entries = feed.entries
    entries = []
    context['rss_entries'] = entries

    template = get_template('welcome.html')
    return HttpResponse(template.render(context))
