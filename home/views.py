from django.shortcuts import render, HttpResponse, redirect
from home import king_admin
from django.core.paginator import Paginator, InvalidPage, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.db.models.deletion import Collector
from django.contrib.admin.utils import NestedObjects
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
import datetime
from home import models
from home import app_forms



# Create your views here.
def index(request):
    return render(request, 'home/index.html', {'table_list': king_admin.enabled_admins})


def tables(request, app_name):
    models_dict = king_admin.enabled_admins.get(app_name)
    if models_dict:
        return render(request, 'home/tables.html', {'models_dict': models_dict, 'app_name': app_name})
    else:
        return HttpResponse('404', status=404)


def table_data(request, app_name, table_name):
    model_class = king_admin.enabled_admins.get(app_name).get(table_name).get('model')
    admin_class = king_admin.enabled_admins.get(app_name).get(table_name).get('admin')
    order = request.GET.get('order')
    if model_class:
        # 整理过滤条件
        field_dict = {}
        q_search = Q()
        for field, value in request.GET.items():
            # Select过滤部分：判断是否为空值，同时是否在admin设置的过滤条件里（防止排序和分页字段干扰）
            # Q查询类型：AND
            if field in admin_class.list_filters and value:
                # 在此对字段进行处理，直接生成查询字典
                # 1、对时间类字段进行特殊处理
                field_obj = model_class._meta.get_field(field)
                if type(field_obj).__name__ == "DateField":
                    today = datetime.date.today()
                    if value == 'today':
                        field_dict[field] = today
                    elif value == 'past7days':
                        field_dict['%s__gte' % field] = today - datetime.timedelta(days=6)
                        field_dict['%s__lte' % field] = today
                    elif value == 'thismonth':
                        field_dict['%s__gte' % field] = datetime.date(today.year, today.month, 1)
                        field_dict['%s__lt' % field] = datetime.date(today.year, today.month + 1, 1)
                    elif value == 'thisyear':
                        field_dict['%s__gte' % field] = datetime.date(today.year, 1, 1)
                        field_dict['%s__lt' % field] = datetime.date(today.year + 1, 1, 1)
                elif type(field_obj).__name__ == "DateTimeField":
                    today = datetime.date.today()
                    time_zero = datetime.time(0, 0, 0)
                    if value == 'today':
                        field_dict['%s__gte' % field] = datetime.datetime.combine(today, time_zero)
                        field_dict['%s__lt' % field] = datetime.datetime.combine(today + datetime.timedelta(days=1),
                                                                                 time_zero)
                    elif value == 'past7days':
                        field_dict['%s__gte' % field] = datetime.datetime.combine(today - datetime.timedelta(days=6),
                                                                                  time_zero)
                        field_dict['%s__lt' % field] = datetime.datetime.combine(today + datetime.timedelta(days=1),
                                                                                 time_zero)
                    elif value == 'thismonth':
                        field_dict['%s__gte' % field] = datetime.datetime.combine(
                            datetime.date(today.year, today.month, 1), time_zero)
                        field_dict['%s__lt' % field] = datetime.datetime.combine(
                            datetime.date(today.year, today.month + 1, 1), time_zero)
                    elif value == 'thisyear':
                        field_dict['%s__gte' % field] = datetime.datetime.combine(datetime.date(today.year, 1, 1),
                                                                                  time_zero)
                        field_dict['%s__lt' % field] = datetime.datetime.combine(datetime.date(today.year + 1, 1, 1),
                                                                                 time_zero)
                # elif type(field_obj).__name__ == "TimeField":
                #     return 'TimeField'
                else:
                    field_dict[field] = value
            # Search过滤部分
            # Q查询类型；OR
            if field == '_search' and value:
                q_search.connector = 'OR'
                for field in admin_class.search_fields:
                    q_search.children.append(("%s__contains" % field, value))

        # 排序部分
        if order:
            query_set = model_class.objects.filter(q_search, **field_dict).order_by(order)
        else:
            query_set = model_class.objects.filter(q_search, **field_dict).order_by(*admin_class.ordering)
        # 分页部分
        paginator = Paginator(query_set, admin_class.list_per_page)
        current_page_id = request.GET.get('p', 1)
        try:
            current_page = paginator.page(current_page_id)
        except PageNotAnInteger:
            current_page = paginator.page(1)
        except EmptyPage:
            current_page = paginator.page(paginator.num_pages)

        return render(request, 'home/table_data.html',
                      {'current_page': current_page, 'model_class': model_class, 'admin_class': admin_class,
                       'app_name': app_name, 'table_name': table_name})
    else:
        return HttpResponse('404', status=404)


def edit(request, app_name, table_name, nid):
    model_class = king_admin.enabled_admins.get(app_name).get(table_name).get('model')
    admin_class = king_admin.enabled_admins.get(app_name).get(table_name).get('admin')
    if model_class and nid:
        obj = model_class.objects.filter(id=nid).first()
        DynamicModelForm = app_forms.create_model_form(model_class,admin_class)
        if request.method == "GET":
            form_obj = DynamicModelForm(instance=obj)
            return render(request, 'home/edit.html', {'model_class': model_class,
                                                      'admin_class': admin_class,
                                                      'app_name': app_name,
                                                      'table_name': table_name,
                                                      'nid': nid,
                                                      'form_obj': form_obj,
                                                      })
        elif request.method == 'POST':
            form_obj = DynamicModelForm(request.POST, instance=obj)
            if admin_class.readonly_table:
                messages.error(request, '此表已设为只读，不可修改数据！')
            else:
                if form_obj.is_valid():
                    form_obj.save()
                else:
                    messages.error(request,'警告：保存失败，请重试！')
                    return render(request, 'home/edit.html', {'model_class': model_class,
                                                          'admin_class': admin_class,
                                                          'app_name': app_name,
                                                          'table_name': table_name,
                                                          'nid': nid,
                                                          'form_obj': form_obj,
                                                          })
            return redirect('/king_admin/%s/%s' % (app_name, table_name))
    else:
        return HttpResponse('404', status=404)

def delete(request, app_name, table_name):
    model_class = king_admin.enabled_admins.get(app_name).get(table_name).get('model')
    admin_class = king_admin.enabled_admins.get(app_name).get(table_name).get('admin')

    if model_class:
        if request.method=="GET":
            id_list = request.GET.get('id').split(',')
            queryset = model_class.objects.filter(pk__in=id_list)
            collector = NestedObjects(using="default")
            collector.collect(queryset)

            summary_list=[]
            for k,v in collector.data.items():
                summary_list.append('%s:%s'%(k._meta.verbose_name_plural,len(v)))
            related_objects_list=collector.nested()

            return render(request, 'home/delete.html', {'model_class': model_class,
                                                            'admin_class': admin_class,
                                                            'app_name': app_name,
                                                            'table_name': table_name,
                                                            'queryset':queryset,
                                                            'summary_list':summary_list,
                                                            'related_objects_list':related_objects_list,
                                                          })
        elif request.method == 'POST':
            if admin_class.readonly_table:
                messages.error(request, '此表已设为只读，不可修改数据！')
            else:
                obj_list=request.POST.getlist('id')
                try:
                    model_class.objects.filter(pk__in=obj_list).delete()
                    messages.success(request, '删除成功！')
                except Exception as e:
                    messages.error(request, '警告：删除失败！%s'%e)
            url = request.path.replace('/delete', '')
            return redirect(url)
    else:
        return HttpResponse('404', status=404)


def add(request,app_name, table_name):
    model_class = king_admin.enabled_admins.get(app_name).get(table_name).get('model')
    admin_class = king_admin.enabled_admins.get(app_name).get(table_name).get('admin')
    if model_class:
        DynamicModelForm = app_forms.create_model_form(model_class)
        if request.method == "GET":
            form_obj = DynamicModelForm()
            return render(request, 'home/add.html', {'model_class': model_class,
                                                      'admin_class': admin_class,
                                                      'app_name': app_name,
                                                      'table_name': table_name,
                                                      'form_obj': form_obj,
                                                      })
        elif request.method == 'POST':
            form_obj = DynamicModelForm(request.POST)
            if form_obj.is_valid():
                form_obj.save()
                return redirect('/king_admin/%s/%s' % (app_name, table_name))
            else:
                return render(request, 'home/add.html', {'model_class': model_class,
                                                          'admin_class': admin_class,
                                                          'app_name': app_name,
                                                          'table_name': table_name,
                                                          'form_obj': form_obj,
                                                          })
    return HttpResponse('ok')


def action(request,app_name, table_name):
    model_class = king_admin.enabled_admins.get(app_name).get(table_name).get('model')
    admin_class = king_admin.enabled_admins.get(app_name).get(table_name).get('admin')
    action_name=request.GET.get('name')
    redirect_url=request.path.replace('/action', '')
    if action_name in admin_class.actions:
        id_list = request.GET.get('id')
        if id_list:
            id_list = id_list.split(',')
            queryset = model_class.objects.filter(pk__in=id_list)
            func=getattr(admin_class,action_name)
            return func(admin_class,request,queryset)
        else:
            messages.warning(request, '请先勾选需要处理的数据后再提交!')
            return redirect(redirect_url)
    else:
        messages.warning(request, '请选择需要执行的动作后再提交!')
        return redirect(redirect_url)

# from django.contrib.auth.decorators import permission_required

# @permission_required('car.drive_car')