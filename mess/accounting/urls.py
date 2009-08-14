from django.conf.urls.defaults import *

urlpatterns = patterns('mess.accounting.views',
    url(r'^transaction$', 'transaction', name='transaction'),
    url(r'^close_out$', 'close_out', name='close_out'),
    url(r'^billing$', 'billing', name='billing'),
    url(r'^cashsheet$', 'cashsheet', name='cashsheet'),
    url(r'^cashsheet_input$', 'cashsheet_input', name='cashsheet_input'),
    url(r'^hours_balance$', 'hours_balance', name='hours_balance'),
)
