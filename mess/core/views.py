from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.template.loader import get_template
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
    # just passing the entries, so we don't have too many
    #entries = _parseUrl("http://www.mariposa.coop/?feed=rss2")
    #feed = feedparser.parse("http://www.mariposa.coop/?feed=rss2")
    #if (len(feed.entries) > MAX_ENTRIES):
    entries = feed.entries[:MAX_ENTRIES]
    #else: 
    #    entries = feed.entries
    #entries = []
    context['rss_entries'] = entries

    template = get_template('welcome.html')
    return HttpResponse(template.render(context))

'''
this code isn't working.  doesn't know what socket is.... 
def _parseUrl(url):
    # copied from http://mxm-mad-science.blogspot.com/2009/01/small-trick-for-socket-timouts-in-plone.html
    # "Fetch the url"
    orig_timout = socket.getdefaulttimeout() # get original timeout
    socket.setdefaulttimeout(20)             # set to 20 seconds
    try:
        result = feedparser.parse(url)['entries']
    except:
        result = []
    socket.setdefaulttimeout(orig_timout)    # set back to original
    endresult = []
    for r in result:
        r2 = {}
        r2.update(r)
        endresult.append(r2)
    # sort for latest first
    decorated = [(r['updated_parsed'], r) for r in endresult]
    decorated.sort()
    decorated.reverse()
    sorted = [d[-1] for d in decorated]
    return sorted
'''
