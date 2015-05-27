from django.conf.urls import patterns, include, url

from django.contrib import admin
from EXPS.views import Site_Login,Site_Logout,Site_Main_Page,Site_Register,Exp_Info,\
    Arange_Info,Exp_Edit,Arange_Edit, Exp_Aranges_Finished, Site_Change_Password,Error_Page,\
    Room_Exps_Info,Check_Aranges_Conflict,Table_Import_And_Export,\
    System_Setting, Recent_Exps, Search_Exps
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'LMS.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    
    url(r'^login/', Site_Login.as_view(),name='login'),
    url(r'^logout/', Site_Logout.as_view(),name='logout'),
    url(r'^change_password/',Site_Change_Password.as_view(),name='change_password'),
    url(r'^register/', Site_Register.as_view(),name='register'),
    url(r'^error_page/', Error_Page.as_view(),name='error_page'),
    url(r'^system_setting/', System_Setting.as_view(),name='system_setting'),
    url(r'^$',Exp_Info.as_view(),{'todo':'all_exps'},name='site_main_page'),
    url(r'^recent_exps/', Recent_Exps.as_view(),name='recent_exps'),
    url(r'^search_exps/', Search_Exps.as_view(),name='search_exps'),
    #url(r'^site/',Exp_Info.as_view(),{'todo':'all_exps'},name='site_main_page'),
    url(r'^user/',Exp_Info.as_view(),{'todo':'my_exps'},name='user_main_page'),
    url(r'^arange_info/(?P<exp_id>\d+)/$',Arange_Info.as_view(),name='arange_info'),
    url(r'^exp_edit/(?P<exp_id>\d+)/$',Exp_Edit.as_view(),{'todo':'edit'},name='exp_edit'),
    url(r'^exp_delete/(?P<exp_id>\d+)/$',Exp_Edit.as_view(),{'todo':'delete'},name='exp_delete'),
    url(r'^exp_add/',Exp_Edit.as_view(),{'todo':'add'},name='exp_add'),
    url(r'^arange_edit/(?P<exp_id>\d+)/$',Arange_Edit.as_view(),{'todo':'edit'},name='arange_edit'),
    url(r'^arange_add/',Arange_Edit.as_view(),{'todo':'add'},name='arange_add'),
    url(r'^exp_aranges_add_finished/',Exp_Aranges_Finished.as_view(),{'todo':'add'},name='exp_aranges_add_finished'),
    url(r'^exp_aranges_edit_finished/(?P<exp_id>\d+)/$',Exp_Aranges_Finished.as_view(),{'todo':'edit'},name='exp_aranges_edit_finished'),
    url(r'^room_exps_info/(?P<room>\w+)/$',Room_Exps_Info.as_view(),name='foom_exps_info'),
    url(r'^check_aranges_conflict/$',Check_Aranges_Conflict.as_view(),name='check_aranges_conflict'),
    url(r'^table_import_and_export/$',Table_Import_And_Export.as_view(),name='table_import_and_export'),
    
    #url(r'^arange_edit/(?P<exp_id>\d+)/$',Arange_Info.as_view(),name='arange_info'),
    
)


