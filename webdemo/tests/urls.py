from django.conf.urls import patterns

urlpatterns = patterns('tests',
    (r'^popup/$', 'views.popup'),
    (r'^pymorphy/$', 'views.pymorphy'),
    (r'^vk/$', 'views.vk'),
)

