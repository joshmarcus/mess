"""
The django-forum and django-simpleforum code looked simple enough,
so I thought I'd do it myself and see how it comes out.  --Paul
"""

from django.db import models
import datetime
from django.contrib.auth import models as auth_models
from django.db.models import Max, Count
from django.utils.http import urlquote

class Forum(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name
        
    def get_absolute_url(self):
        return '/forum/%s/' % self.slug

    def newest_post(self):
        if self.post_set.count():
            return self.post_set.order_by('-timestamp')[0]

    def threads(self):
        """
        A list of subjects, annotated with the last post in each subject
        SQL: select subject, max(timestamp) from posts group by subject
        """
        return self.post_set.values('subject').annotate(
               total_posts=Count('timestamp'), last_post=Max('timestamp')
               ).order_by('-last_post')

class PostManager(models.Manager):

    def threads(self):
        return self.values('subject', 
                           'forum__name', 'forum__slug').annotate(last_post=Max(
                'timestamp')).order_by('-last_post')

class Post(models.Model):
    forum = models.ForeignKey(Forum)
    author = models.ForeignKey(auth_models.User)    
    subject = models.CharField(max_length=255)  #used for grouping into threads
    timestamp = models.DateTimeField(auto_now_add=True)
    body = models.TextField()
    deleted = models.BooleanField()
    objects = PostManager()

    def get_absolute_url(self):   #for now, return the thread's url
        return '/forum/%s/?subject=%s' % (self.forum.slug, urlquote(self.subject, safe=''))

    def get_alias(self):
        return '%s (%s)' % (self.author.first_name, 
                            self.author.get_profile().get_primary_account())

    

