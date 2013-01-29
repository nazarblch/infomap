from django.conf.urls import patterns
from agency.views import login, logout, show_clients, new_client, addclient_todb



urlpatterns = patterns('agency',
        (r'^$',  login),              
        (r'^clients/$',  show_clients),
        (r'^logout/$', logout), 
        (r'^newclient/$', new_client),
        (r'^addclient_todb/$', addclient_todb),
)



