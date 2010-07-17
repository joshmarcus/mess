import re

import django.conf as conf
import django.contrib.auth.decorators as ad 


class UserPassesTestMiddleware(object):
    """
    Originally adapted from mattgrayson's snippet at
    http://www.djangosnippets.org/snippets/1219/.

    Middleware component that wraps the user_passes_test decorator around 
    views for matching URL patterns. To use, add the class to 
    MIDDLEWARE_CLASSES and define USER_PASSES_TEST_URLS in your settings.py.

    The following example limits access to anything under "/topsecret/" to 
    authenticated users:
    
    USER_PASSES_TEST_URLS = (
        (r'^/topsecret/', lambda u: u.is_authenticated),
    )
    
    The following example locks down a typical site, giving access to 
    staff only:
    
    USER_PASSES_TEST_URLS = (
        (r'^/$', None), 
        (r'^/login/$', None),
        (r'^/logout/$', None),
        (r'^/media/', None),
        (r'^/passwordreset/', None),
        (r'', lambda u: u.is_staff),
    )

    Note that patterns with a test of "None" pass the matching view through
    unwrapped.  Also, this example works because the order of 
    USER_PASSES_TEST_URLS matters.  The first matching pattern is the only 
    one applied.  
    
    Views already wrapped in an auth decorator are untouched, so 
    permissions can still be controlled on a view-by-view basis.
    """
    def __init__(self):
        self.urls = [(re.compile(pattern), test) for pattern, test in 
            conf.settings.USER_PASSES_TEST_URLS]
        
    def process_view(self, request, view_func, view_args, view_kwargs):
        # don't wrap if function is already wrapped

        #  This getattr line doesn't work and is breaking non-staff access to 
        # everything as of 7/17/2010.  So I replaced it with low-level 
        # "view_func.func_code_co_name", which should *not* be the right way
        # to do it, but at least it works for now.  --Paul
        # But the getattr part is still needed to make sure autocomplete
        # will still work.  This thing is all confusing!  --Paul
        if getattr(view_func, 'decorator', None):  
            return
        if view_func.func_code.co_name == '_wrapped_view':
            return 

        for regex, test in self.urls:
            if regex.search(request.path): 
                if test:  # return view wrapped in test
                    return ad.user_passes_test(test)(view_func)(request, 
                        *view_args, **view_kwargs)             
                else:  # no test, don't wrap
                    return 

