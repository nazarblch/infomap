from django.conf.urls import patterns



from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('project',

    (r'^budget/$', 'views.budget', {"templ_dict": None, "shopobj": None} ),
    (r'^optimize_group/$', 'ajax.optimize_group'),

    (r'^banners/$', 'views.banners', {"templ_dict": None, "shopobj": None}),
    (r'^create_banners/$', 'ajax.create_banners_from_tml' ),

)



