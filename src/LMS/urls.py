from django.conf.urls import patterns, include, url

from django.contrib import admin
from EXPS.views import Site_Login
import settings

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'LMS.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^exps/admin/', include(admin.site.urls)),
    url(r'^exps/assistant/', include('ASS.urls')),
    url(r'^exps/course/', include('EXPS.urls')),
    url(r'^exps/rest/', include('REST.urls')),
    
    url(r'^exps/media/(?P<path>.*)$', 'django.views.static.serve', {'document_root':settings.MEDIA_ROOT}),
    #url(r'^student_assistant/',include(extra_patterns)),
)
