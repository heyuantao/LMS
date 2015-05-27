from django.conf.urls import patterns, include, url
from rest_framework.urlpatterns import format_suffix_patterns
from django.contrib import admin
from api import Exp_List,Exp_Detail,Exp_Arangement_Detail,Exp_Arangement_List
from REST.api import Location_Detail, Location_List
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'LMS.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^exp/$',Exp_List.as_view()),
    url(r'^exp/(?P<exp_id>\d+)/$',Exp_Detail.as_view()),
    url(r'^arangement/$',Exp_Arangement_List.as_view()),
    url(r'^arangement/(?P<arangement_id>\d+)/$',Exp_Arangement_Detail.as_view()),
    url(r'^location/$',Location_List.as_view()),
    url(r'^location/(?P<location_id>\d+)/$',Location_Detail.as_view()),
    #url(r'^exp/(?P<exp_id>\d+)/$',Arange_Info.as_view(),name='arange_info'),
    #url(r'^assistant_arange_check/', Student_Assistant_Arange_Edit.as_view(),{'todo':'check'},name='assistant_arange_check'),
    #url(r'^assistant_arange_edit/(?P<week_order_abbr>\d+)/$', Student_Assistant_Arange_Edit.as_view(),{'todo':'edit'},name='assistant_arange_edit'),

    #url(r'^arange_edit/(?P<exp_id>\d+)/$',Arange_Info.as_view(),name='arange_info'),
    
)
urlpatterns= format_suffix_patterns(urlpatterns)

