from django.conf.urls import patterns, include, url
from django.conf import settings


from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^shop/', include('shop.urls')),
	
    url(r'^project/', include('project.urls')),
    
    url(r'^agency/', include('agency.urls')),

    url(r'^tests/', include('tests.urls')),
)

urlpatterns+=patterns('',
		(r'^media/(?P<path>.*)$', 'django.views.static.serve',  
         	{'document_root':     settings.MEDIA_ROOT}),

)

