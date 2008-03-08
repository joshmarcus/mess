from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.utils import simplejson

from people.models import Person
from people.forms import PersonForm, Search

def search(request):
    if not request.method == 'GET':
        return render_to_response('people/search.html', {})
    if request.GET.has_key('string'):
        auto_dict = {}
        string = request.GET.get('string')
        list = Person.objects.filter(name__icontains=string)
        for i in list:
            auto_dict[i.id] = i.name

        return HttpResponse(simplejson.dumps(auto_dict),
                mimetype='application/javascript')
    return render_to_response('people/search.html', {} )

def people(request):
    pass
    page_name = 'People'
    people_list = Person.objects.all()
    return render_to_response('people/people_list.html', locals())

def person(request, id_num):
    person = Person.objects.get(id=id_num)    
    page_name = person.name
    return render_to_response('people/person.html', locals())

def person_form(request, id=None):
    page_name = 'Person Form'
    if request.method == 'POST':
        if id:
            page_name = ('Edit %s' % person.name)
            person = Person.object.get(id=id)
            form = PersonForm(request.POST, instance=person)
        else:
            form = PersonForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/people')
        else:
            pass
    else:
        if id:
            person = Person.objects.get(id=id)
            form = PersonForm(instance=person)
        else:
            form = PersonForm()
        return render_to_response('people/person_form.html', locals())
