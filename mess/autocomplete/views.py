from django.http import HttpResponse
from django.db.models import Q
from django.utils import simplejson
from django.utils.encoding import smart_unicode


class AutoComplete(object):
    # decorator so UserPassesTestMiddleware doesn't touch it
    decorator = True

    def __init__(self):
        self.settings = dict()

    def __call__(self, request, ac_name, query_param='query'):
        if not self.settings.get(ac_name):
            return self.not_found(ac_name)

        qs, fields, limit, key, label, auth = self.settings[ac_name]
        if auth and not request.user.is_authenticated():
            return self.forbidden(ac_name)
        query = request.GET.get(query_param, '')
        
        # allow hook to create arbitrary filters
        if callable(fields):
            filter = fields(query)
        else:
            filter = Q()
            for field in fields:
                if not '__' in field:
                    field = '%s__startswith' % field
                filter |= Q(**{field: query})
        
        qs = qs.filter(filter).distinct()[:limit]
        
        if isinstance(label, basestring):
            if key == 'pk':
                key = qs.model._meta.pk.attname
            result = list(qs.values_list(key, label))
        else:
            result = []
            for obj in qs:
                result.append((getattr(obj, key), label(obj)))
        return HttpResponse(simplejson.dumps(result),
                mimetype='application/json')

    def register(self, id, queryset, fields, limit=None, key='pk', label=lambda obj: smart_unicode(obj), auth=False):
        self.settings[id] = (queryset, fields, limit, key, label, auth)

    def not_found(self, ac_name):
        return HttpResponse(status=404)

    def forbidden(self, ac_name):
        return HttpResponse(status=403)

    def ac_reverse(self, ac_name, value):
        """
        returns the label associated with the passed-in initial value.
        FIXME: (id=value) clause should be one of those **kwarg things
          and should depend on key
        """
        qs, fields, limit, key, label, auth = self.settings[ac_name]
        try:
            obj = qs.filter(id=value)[0]
        except IndexError:
            return ''
        if isinstance(label,basestring):
            return getattr(obj,label)
        else:
            return label(obj)
        

autocomplete = AutoComplete()
