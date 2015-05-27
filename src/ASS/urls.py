from django.conf.urls import patterns, include, url

from django.contrib import admin
from EXPS.views import Site_Login,Site_Logout,Site_Main_Page,Site_Register,Exp_Info,\
    Arange_Info,Exp_Edit,Arange_Edit, Exp_Aranges_Finished, Site_Change_Password,Error_Page,\
    Room_Exps_Info,Check_Aranges_Conflict,Table_Import_And_Export,\
    System_Setting, Recent_Exps, Search_Exps
from ASS.views import Show_Student_Assistant, Student_Assistant_Edit,\
    Student_Assistant_Arange_Edit,Show_Assistant_Recent_Aranges,Show_Assistant_Arange_In_Weekorder_Mode
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'LMS.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    
    url(r'^show/', Show_Student_Assistant.as_view(),name='show_assistant'),
    url(r'^show_assistant_aranges/(?P<ass_id>\d+)/$', Show_Assistant_Recent_Aranges.as_view(),name='show_assistant_aranges'),
    url(r'^show_assistant_arange_in_week_mode/(?P<week_order_abbr>\d+)/$',Show_Assistant_Arange_In_Weekorder_Mode.as_view(),name='show_assistant_arange_in_week_mode'),
    
    url(r'^assistant_edit_and_add/', Student_Assistant_Edit.as_view(),{'todo':'show'},name='assistant_edit_and_add'),
    url(r'^assistant_add/', Student_Assistant_Edit.as_view(),{'todo':'add'},name='assistant_add'),
    url(r'^assistant_edit/(?P<ass_id>\d+)/$', Student_Assistant_Edit.as_view(),{'todo':'edit'},name='assistant_edit'),
    url(r'^assistant_delete/(?P<ass_id>\d+)/$', Student_Assistant_Edit.as_view(),{'todo':'delete'},name='assistant_delete'),
    url(r'^assistant_arange_check/', Student_Assistant_Arange_Edit.as_view(),{'todo':'check'},name='assistant_arange_check'),
    url(r'^assistant_arange_edit/(?P<week_order_abbr>\d+)/$', Student_Assistant_Arange_Edit.as_view(),{'todo':'edit'},name='assistant_arange_edit'),

    #url(r'^arange_edit/(?P<exp_id>\d+)/$',Arange_Info.as_view(),name='arange_info'),
    
)


