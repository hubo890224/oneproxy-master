# coding: utf-8

import datetime
from django.db import models
from juser.models import User, UserGroup
from jasset.models import Asset,AssetGroup

MYSQL_ENV = (
    (1, U'生产环境'),
    (2, U'测试环境')
    )

MYSQL_STATUS = (
    (0, u"使用"),
    (1, u"未使用")
    )


class MysqlGroup(models.Model):
    GROUP_TYPE = (
        ('P', 'PRIVATE'),
        ('A', 'ASSET'),
    )
    name = models.CharField(max_length=80, unique=True)
    comment = models.CharField(max_length=160, blank=True, null=True)

    def __unicode__(self):
        return self.name




class MysqlServer(models.Model):
    """
    asset modle
    """
    mysqlname = models.CharField(unique=True, max_length=128, verbose_name=u"Mysql名")
    mysqlserverid = models.ForeignKey(Asset,blank=True,null=True,verbose_name=u"mysql服务器ID")
    mysql_ip = models.CharField(max_length=32, blank=True, null=True, verbose_name=u"Mysql服务器IP")
    username = models.CharField(max_length=16, blank=True, null=True, verbose_name=u"管理用户名")
    password = models.CharField(max_length=256, blank=True, null=True, verbose_name=u"密码")
    port = models.IntegerField(blank=True, null=True, verbose_name=u"mysql端口号")
    group = models.ManyToManyField(MysqlGroup, blank=True, verbose_name=u"所属mysql组")
    status = models.IntegerField(choices=MYSQL_STATUS, blank=True, null=True, default=0, verbose_name=u"mysql状态")
    env = models.IntegerField(choices=MYSQL_ENV, blank=True, null=True, verbose_name=u"运行环境")
    checksql = models.CharField(max_length=1000, blank=True, null=True, verbose_name=u"状态监测语句")
    date_added = models.DateTimeField(auto_now=True, null=True)
    is_active = models.BooleanField(default=True, verbose_name=u"是否激活")
    comment = models.CharField(max_length=128, blank=True, null=True, verbose_name=u"备注")

    def __unicode__(self):
        return self.ip



