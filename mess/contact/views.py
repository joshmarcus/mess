from django.http import HttpResponse
from django.utils import simplejson

from mess.utils.search import search_for_string

def search_for(request):
    if request.GET.has_key('string')  and request.GET.has_key('search'):
        string = request.GET.get('string')
        search = request.GET.get('search')
        dict = search_for_string(search, string)
    return HttpResponse(simplejson.dumps(dict),
                        mimetype='application/javascript')
