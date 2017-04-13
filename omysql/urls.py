# coding:utf-8
from django.conf.urls import patterns, include, url
from omysql.views import *

urlpatterns = patterns('',
    url(r'^omysql/add/$', mysql_add, name='mysql_add'),
    #url(r"^asset/add_batch/$", asset_add_batch, name='asset_add_batch'),
    url(r'^omysql/list/$', mysql_list, name='mysql_list'),
    url(r'^omysql/del/$', mysql_del, name='mysql_del'),
    url(r"^omysql/detail/$", mysql_detail, name='mysql_detail'),
    url(r'^omysql/edit/$', mysql_edit, name='mysql_edit'),
    #url(r'^asset/edit_batch/$', asset_edit_batch, name='asset_edit_batch'),
    #url(r'^asset/update/$', asset_update, name='asset_update'),
    #url(r'^asset/update_batch/$', asset_update_batch, name='asset_update_batch'),
    #url(r'^asset/upload/$', asset_upload, name='asset_upload'),
    url(r'^group/del/$', group_del, name='mysql_group_del'),
    url(r'^group/add/$', group_add, name='mysql_group_add'),
    url(r'^group/list/$', group_list, name='mysql_group_list'),
    url(r'^group/edit/$', group_edit, name='mysql_group_edit'),
)