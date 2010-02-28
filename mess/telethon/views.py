from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.template.loader import get_template

def index(request):
    context = RequestContext(request)
    template = get_template('telethon/index.html')
    return HttpResponse(template.render(context))

def member(request, username):
    user = get_object_or_404(User, username=username)
    member = user.get_profile()
    context = RequestContext(request)
    context['member'] = member
    template = get_template('telethon/member.html')
    return HttpResponse(template.render(context))

