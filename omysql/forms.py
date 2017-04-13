# coding:utf-8
from django import forms

from omysql.models import MysqlServer,MysqlGroup, Asset, AssetGroup


class MysqlForm(forms.ModelForm):

    class Meta:
        model = MysqlServer

        fields = [
            "mysqlname","mysqlserverid","mysql_ip","username","username","port","group","status","env","checksql","is_active","comment"
        ]


class MysqlGroupForm(forms.ModelForm):
    class Meta:
        model = MysqlGroup
        fields = [
            "name", "comment"
        ]




