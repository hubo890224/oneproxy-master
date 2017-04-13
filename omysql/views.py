# coding:utf-8

from django.db.models import Q
from omysql.mysql_api import *
from jumpserver.api import *
from jumpserver.models import Setting
#from jasset.forms import AssetForm, IdcForm
from omysql.forms import MysqlForm,MysqlGroupForm
#from jasset.models import Asset, IDC, AssetGroup, ASSET_TYPE, ASSET_STATUS
from omysql.models import MysqlServer,MysqlGroup,MYSQL_STATUS
from jperm.perm_api import get_group_asset_perm, get_group_user_perm



@require_role('admin')
def group_add(request):
    """
    Group add view
    添加MySQL组
    """
    header_title, path1, path2 = u'添加MySQL组', u'MySQL管理', u'添加MySQL组'
    mysql_all = MysqlServer.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name', '')
        mysql_select = request.POST.getlist('mysql_select', [])
        comment = request.POST.get('comment', '')

        try:
            if not name:
                emg = u'组名不能为空'
                raise ServerError(emg)

            mysql_group_test = get_object(MysqlGroup, name=name)
            if mysql_group_test:
                emg = u"该组名 %s 已存在" % name
                raise ServerError(emg)

        except ServerError:
            pass

        else:
            db_add_group(name=name, comment=comment, mysql_select=mysql_select)
            smg = u"主机组 %s 添加成功" % name

    return my_render('omysql/group_add.html', locals(), request)


@require_role('admin')
def group_edit(request):
    """
    Group edit view
    编辑资产组
    """
    header_title, path1, path2 = u'编辑主机组', u'资产管理', u'编辑主机组'
    group_id = request.GET.get('id', '')
    group = get_object(MysqlGroup, id=group_id)

    mysql_all = MysqlServer.objects.all()
    mysql_select = MysqlServer.objects.filter(group=group)
    mysql_no_select = [a for a in mysql_all if a not in mysql_select]

    if request.method == 'POST':
        name = request.POST.get('name', '')
        mysql_select = request.POST.getlist('mysql_select', [])
        comment = request.POST.get('comment', '')

        try:
            if not name:
                emg = u'组名不能为空'
                raise ServerError(emg)

            if group.name != name:
                mysql_group_test = get_object(MysqlGroup, name=name)
                if mysql_group_test:
                    emg = u"该组名 %s 已存在" % name
                    raise ServerError(emg)

        except ServerError:
            pass

        else:
            group.mysqlserver_set.clear()
            db_update_group(id=group_id, name=name, comment=comment, mysql_select=mysql_select)
            smg = u"主机组 %s 添加成功" % name

        return HttpResponseRedirect(reverse('mysql_group_list'))

    return my_render('omysql/group_edit.html', locals(), request)


@require_role('admin')
def group_list(request):
    """
    list mysql group
    列出MySQL组
    """
    header_title, path1, path2 = u'查看MySQL组', u'MySQL管理', u'查看MySQL组'
    keyword = request.GET.get('keyword', '')
    mysql_group_list = MysqlGroup.objects.all()
    group_id = request.GET.get('id')
    if group_id:
        mysql_group_list = mysql_group_list.filter(id=group_id)
    if keyword:
        mysql_group_list = mysql_group_list.filter(Q(name__contains=keyword) | Q(comment__contains=keyword))

    mysql_group_list, p, mysql_groups, page_range, current_page, show_first, show_end = pages(mysql_group_list, request)
    return my_render('omysql/group_list.html', locals(), request)


@require_role('admin')
def group_del(request):
    """
    Group delete view
    删除主机组
    """
    group_ids = request.GET.get('id', '')
    group_id_list = group_ids.split(',')

    for group_id in group_id_list:
        MysqlGroup.objects.filter(id=group_id).delete()

    return HttpResponse(u'删除成功')

@require_role('admin')
def mysql_list(request):
    """
    asset list view
    """
    header_title, path1, path2 = u'查看MySQL Server', u'MySQL Server管理', u'查看MySQL Server'
    username = request.user.username
    user_perm = request.session['role_id']
    mysql_group_all = MysqlGroup.objects.all()
    #asset_types = MYSQL_TYPE
    mysql_status = MYSQL_STATUS
    group_name = request.GET.get('group', '')
    #asset_type = request.GET.get('asset_type', '')
    status = request.GET.get('status', '')
    keyword = request.GET.get('keyword', '')
    export = request.GET.get("export", False)
    group_id = request.GET.get("group_id", '')
    #idc_id = request.GET.get("idc_id", '')
    mysql_id_all = request.GET.getlist("id", '')

    if group_id:
        group = get_object(MysqlGroup, id=group_id)
        if group:
            mysql_find = MysqlServer.objects.filter(group=group)
    else:
        if user_perm != 0:
            mysql_find = MysqlServer.objects.all()
        else:
            mysql_id_all = []
            user = get_object(User, username=username)
            asset_perm = get_group_user_perm(user) if user else {'asset': ''}
            user_asset_perm = asset_perm['asset'].keys()
            for asset in user_asset_perm:
                mysql_id_all.append(asset.id)
            mysql_find = MysqlServer.objects.filter(pk__in=mysql_id_all)
            mysql_group_all = list(asset_perm['asset_group'])



    if group_name:
        mysql_find = mysql_find.filter(group__name__contains=group_name)


    if status:
        mysql_find = mysql_find.filter(status__contains=status)

    if keyword:
        mysql_find = mysql_find.filter(
            Q(mysqlname__contains=keyword) |
            Q(mysql_ip__contains=keyword) |
            Q(comment__contains=keyword) |
            Q(group__name__contains=keyword))

    if export:
        if mysql_id_all:
            mysql_find = []
            for mysql_id in mysql_id_all:
                mysql = get_object(MysqlServer, id=mysql_id)
                if mysql:
                    mysql_find.append(mysql)
        s = write_excel(mysql_find)
        if s[0]:
            file_name = s[1]
        smg = u'excel文件已生成，请点击下载!'
        return my_render('omysql/asset_excel_download.html', locals(), request)
    mysqls_list, p, mysqls, page_range, current_page, show_first, show_end = pages(mysql_find, request)
    if user_perm != 0:
        return my_render('omysql/mysql_list.html', locals(), request)
    else:
        return my_render('omysql/asset_cu_list.html', locals(), request)


@require_role('admin')
def mysql_add(request):
    """
    Asset add view
    添加资产
    """
    header_title, path1, path2 = u'添加MySQL', u'MySQL管理', u'添加MySQL'
    mysql_group_all = MysqlGroup.objects.all()
    af = MysqlForm()
    default_setting = get_object(Setting, name='default')
    default_port = default_setting.field2 if default_setting else ''
    if request.method == 'POST':
        af_post = MysqlForm(request.POST)
        mysqlip = request.POST.get('mysql_ip', '')
        mysqlname = request.POST.get('mysqlname', '')
        mysqlchecksql=request.POST.get('checksql','')
        mysqlserverid = request.POST.get('mysqlserverid','')

        server_ip = get_object(Asset,id=mysqlserverid)

        is_active = True if request.POST.get('is_active') == '1' else False
        use_default_auth = request.POST.get('use_default_auth', '')
        try:
            if MysqlServer.objects.filter(mysqlname=unicode(mysqlname)):
                error = u'该MySQL名 %s 已存在!' % mysqlname
                raise ServerError(error)
            if len(mysqlname) > 54:
                error = u"MySQL名长度不能超过53位!"
                raise ServerError(error)
            if len(mysqlchecksql) > 500:
                error = u"监测语句长度不能超过500位!"
                raise ServerError(error)
        except ServerError:
            pass
        else:
            if af_post.is_valid():
                mysql_save = af_post.save(commit=False)
                if not use_default_auth:
                    password = request.POST.get('password', '')
                    password_encode = password
                    mysql_save.password = password_encode
                if not mysqlip:
                    mysql_save.mysql_ip = server_ip.ip
                mysql_save.is_active = True if is_active else False
                mysql_save.save()
                af_post.save_m2m()

                msg = u'主机 %s 添加成功' % mysqlname
            else:
                esg = u'主机 %s 添加失败' % mysqlname

    return my_render('omysql/mysql_add.html', locals(), request)


@require_role('admin')
def mysql_del(request):
    """
    del a mysql
    删除mysql
    """
    mysql_id = request.GET.get('id', '')
    if mysql_id:
        MysqlServer.objects.filter(id=mysql_id).delete()

    if request.method == 'POST':
        mysql_batch = request.GET.get('arg', '')
        mysql_id_all = str(request.POST.get('mysql_id_all', ''))

        if mysql_batch:
            for mysql_id in mysql_id_all.split(','):
                mysql = get_object(MysqlServer, id=mysql_id)
                mysql.delete()

    return HttpResponse(u'删除成功')

@require_role(role='super')
def mysql_edit(request):
    """
    edit a asset
    修改主机
    """
    header_title, path1, path2 = u'修改MySQL', u'MySQL管理', u'修改MySQL'

    mysql_id = request.GET.get('id', '')
    username = request.user.username
    mysql = get_object(MysqlServer, id=mysql_id)
    if mysql:
        #password_old = mysql.password
        password_old = 'a'

    af = MysqlForm(instance=mysql)
    if request.method == 'POST':
        af_post = MysqlForm(request.POST, instance=mysql)
        mysqlip = request.POST.get('ip', '')
        mysqlname = request.POST.get('mysqlname', '')
        password = request.POST.get('password', '')
        is_active = True if request.POST.get('is_active') == '1' else False
        #use_default_auth = request.POST.get('use_default_auth', '')
        try:
            mysql_test = get_object(MysqlServer, mysqlname=mysqlname)
            if mysql_test and mysql_id != unicode(mysql_test.id):
                emg = u'该MySQL名 %s 已存在!' % mysqlname
                raise ServerError(emg)
            if len(mysqlname) > 54:
                emg = u'主机名长度不能超过54位!'
                raise ServerError(emg)
            else:
                if af_post.is_valid():
                    af_save = af_post.save(commit=False)
                    #if use_default_auth:
                    #    af_save.username = ''
                    #    af_save.password = ''
                        # af_save.port = None
                    #else:
                    if password:
                            password_encode = CRYPTOR.encrypt(password)
                            af_save.password = password_encode
                    else:
                            af_save.password = password_old
                    af_save.is_active = True if is_active else False
                    af_save.save()
                    af_post.save_m2m()
                    # asset_new = get_object(Asset, id=asset_id)
                    # asset_diff_one(asset_old, asset_new)
                    info = mysql_diff(af_post.__dict__.get('initial'), request.POST)
                    #db_mysql_alert(mysql, username, info)

                    smg = u'主机 %s 修改成功' % mysqlip
                else:
                    emg = u'主机 %s 修改失败' % mysqlip
                    raise ServerError(emg)
        except ServerError as e:
            error = e.message
            return my_render('omysql/mysql_edit.html', locals(), request)
        return HttpResponseRedirect(reverse('mysql_detail')+'?id=%s' % mysql_id)

    return my_render('omysql/mysql_edit.html', locals(), request)

@require_role('admin')
def mysql_detail(request):
    """
    mysql detail view
    """
    header_title, path1, path2 = u'MySQL详细信息', u'MySQL管理', u'MySQL详情'
    mysql_id = request.GET.get('id', '')
    mysql = get_object(MysqlServer, id=mysql_id)
    #perm_info = get_group_asset_perm(mysql)
    log = Log.objects.filter(host=mysql.mysqlname)
    """
    if perm_info:
        user_perm = []
        for perm, value in perm_info.items():
            if perm == 'user':
                for user, role_dic in value.items():
                    user_perm.append([user, role_dic.get('role', '')])
            elif perm == 'user_group' or perm == 'rule':
                user_group_perm = value
    print perm_info
    """

    #asset_record = AssetRecord.objects.filter(asset=asset).order_by('-alert_time')


    #mysql variables
    mysql_options = get_variables('172.30.12.9','root', '111111',3306)

    performance_info = get_performance_info('172.30.12.9','root', '111111',3306)


    return my_render('omysql/mysql_detail.html', locals(), request)