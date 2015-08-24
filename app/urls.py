from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns('',
    url(r'^$', views.landing, name='landing'),
    url(r'^register/$', views.register, name='register'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),

    url(r'^auth/info/$', views.auth_info, name='auth_info'),
    url(r'^auth/request/$', views.auth_request, name='auth_request'),
    url(r'^auth/process/$', views.auth_process, name='auth_process'),
    url(r'^auth/error/$', views.auth_error, name='auth_error'),

    url(r'^home/$', views.user_home, name='user_home'),
    url(r'^table/(?P<pk>[0-9]+)/$', views.table_detail, name='table_detail'),
    url(r'^table/new/$', views.table_new, name='table_new'),
    url(r'^table/(?P<pk>[0-9]+)/edit/$', views.table_edit, name='table_edit'),
    url(r'^table/(?P<pk>[0-9]+)/delete/$', views.table_delete, name='table_delete'),
    # url(r'^user/(?P<pk>[0-9]+)/recent$', views.user_recent, name='user_recent'),

    url(r'^api/tables/$', views.api_table_list, name="api_table_list"),
    url(r'^api/table/(?P<pk>[0-9]+)/$', views.api_table_detail, name='api_table_detail'),
    url(r'^api/followees/$', views.api_followees_list, name='api_followees_list'),

    url(r'^test/$', views.test_lb_, name='test_lb_'),
    url(r'^test[.]html$', views.test_lb_, name='test_lb_'),
)
