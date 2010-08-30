from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.db.models import Q

from mess.forum import models
from mess.forum import forms

import datetime

@login_required
def menu(request):
    """ The menu gives a list of forums """
    forums = models.Forum.objects.all().order_by('order')
    return render_to_response('forum/menu.html', locals(),
            context_instance=RequestContext(request))
    
@login_required
def forum(request, forum_slug):
    """ A forum gives a list of its threads """
    DEFAULT_MAXPOSTS = 20
    forum = get_object_or_404(models.Forum, slug=forum_slug)
    forums = models.Forum.objects.all().order_by('order')
    # subject to expand (show all its posts):
    subject = request.GET.get('subject')
    # show newest n posts:
    maxposts = request.GET.get('maxposts') or DEFAULT_MAXPOSTS
    if subject:
        posts = forum.post_set.filter(subject=subject).order_by('-timestamp')
    else:
        posts = forum.post_set.order_by('-timestamp')[:maxposts]
    threads = _organize_as_threads(posts) 
    return render_to_response('forum/forum.html', locals(),
            context_instance=RequestContext(request))
    
def _organize_as_threads(posts):
    threads = {}
    for post in posts.reverse():
        if post.subject in threads:
            threads[post.subject]['posts'].append(post)
            threads[post.subject]['newest'] = post.timestamp
        else:
            threads[post.subject] = {'newest':post.timestamp, 'posts':[post],
                'subject':post.subject,
                'total_posts':models.Post.objects.filter(forum=post.forum, 
                 subject=post.subject).count()}
    threads = threads.values()
    threads.sort(None, lambda t: t['newest'], True) # sort newest to oldest
    return threads

@login_required
def addpost(request, forum_slug):
    """ Add a post to a given forum (optional: in a given thread) """
    forum = get_object_or_404(models.Forum, slug=forum_slug)
    subject = request.GET.get('subject')
    if request.method == "POST":
        form = forms.AddPostForm(request.POST)
        if form.is_valid() and request.POST.get('action')=='Post':
            form.save(author=request.user)
            new_post = form.instance
            return HttpResponseRedirect(new_post.get_absolute_url())
    else:
        form = forms.AddPostForm(initial={'forum':forum.id, 'subject':subject})
    return render_to_response('forum/addpost.html', locals(),
            context_instance=RequestContext(request))

@login_required
def deletepost(request):
    """ Mark post 'deleted' so it won't show up anymore """
    post_id = request.POST.get('post_id')
    post = get_object_or_404(models.Post, id=post_id)
    if post.author != request.user:
        return HttpResponse('Sorry, only the author can delete %s' % post.id)
    post.deleted = True
    post.save()
    return HttpResponse('Post deleted.')
