from django.conf.urls.defaults import *

urlpatterns = patterns('mess.accounting.views',
    url(r'^transaction$', 'transaction', name='transaction'),
    url(r'^after_hours$', 'after_hours', name='after_hours'),
    url(r'^EBT$', 'EBT', name='EBT'),
    url(r'^close_out$', 'close_out', name='close_out'),
    url(r'^billing$', 'billing', name='billing'),
    url(r'^frozen$', 'frozen', name='frozen'),
    url(r'^cashsheet$', 'cashsheet', name='cashsheet'),
    url(r'^cashsheet_input$', 'cashsheet_input', name='cashsheet_input'),
    url(r'^hours_balance$', 'hours_balance', name='hours_balance'),
    url(r'^storeday$', 'storeday', name='storeday'),
#   url(r'^reverse_trans$', 'reverse_trans', name='reverse_trans'),
)
