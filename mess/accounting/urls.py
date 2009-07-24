from django.conf.urls.defaults import *

urlpatterns = patterns('mess.accounting.views',
    url(r'^transaction$', 'transaction', name='transaction'),
    url(r'^close_out$', 'close_out', name='close_out'),
    url(r'^billing$', 'billing', name='billing'),
)
