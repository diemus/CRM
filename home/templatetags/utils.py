from django import template
from django.utils.safestring import mark_safe
from django.core.exceptions import FieldDoesNotExist
import re
register=template.Library()

@register.filter
def to_bootstrap_tags(tag):
    if tag=='error':
        return 'danger'
    else:
        return tag

@register.filter
def get_model_verbose_name(model_class):
    return model_class._meta.verbose_name

@register.filter
def get_field_verbose_name(admin_class,field):
    try:
        model_class=admin_class.model
        field_obj=model_class._meta.get_field(field)
        if field_obj.verbose_name:
            return field_obj.verbose_name
        else:
            return field
    except FieldDoesNotExist:
        # 自定义非数据库字段
        func=getattr(admin_class,field,None)
        if func:
            return func.verbose_name
        else:
            return field

@register.filter
def get_action_verbose_name(func_name,admin_class):
    func=getattr(admin_class,func_name)
    if hasattr(func,'short_description'):
        return func.short_description
    else:
        return func_name

@register.filter
def get_field_type(model_class,field):
    field_obj = model_class._meta.get_field(field)
    if field_obj.choices:
        return 'CharField'
    elif type(field_obj).__name__ == "ForeignKey":
        return 'ForeignKey'
    elif type(field_obj).__name__ == "DateTimeField":
        return 'DateTimeField'
    elif type(field_obj).__name__ == "DateField":
        return 'DateField'
    elif type(field_obj).__name__ == "TimeField":
        return 'TimeField'
    else:
        return 'CharField'

@register.filter
def get_options(model_class,field):
    '''获取过滤条件，并将列表传回'''
    # 返回格式(value,verbose_name)
    field_obj = model_class._meta.get_field(field)

    if field_obj.choices:
        result = field_obj.choices
    elif type(field_obj).__name__ == "ForeignKey":
        result = field_obj.get_choices()[1:]
    elif type(field_obj).__name__ == "DateTimeField":
        result=[
            ('today','今天'),
            ('past7days','过去7天'),
            ('thismonth','本月'),
            ('thisyear','本年度'),
        ]
    else:
        # 变量型参数名用字典的方式传入
        args_dict = {'%s__isnull' % field: True}
        result=model_class._meta.model.objects.exclude(**args_dict).values_list(field,flat=True).distinct()
        result=list(zip(result,result))
    return result

@register.simple_tag
def is_option_selected(option_value,field,request):
    request_value=request.GET.get(field)
    if request_value==str(option_value):
        return 'selected'
    else:
        return ''

@register.simple_tag
def get_data_by_field(model_obj,field,admin_class):
    try:
        field_obj = model_obj._meta.get_field(field)
        if field_obj.choices:
            result=getattr(model_obj,'get_%s_display'%field)()
        else:
            result =getattr(model_obj, field)

        if type(result).__name__=='datetime':
            result=result.strftime("%Y-%m-%d %H:%M:%S")

        if result is None:result=''
        if result is True:result=mark_safe('<span class="glyphicon glyphicon-ok"></span>')
        if result is False:result=mark_safe('<span class="glyphicon glyphicon-remove"></span>')
        return result
    except FieldDoesNotExist:
        func=getattr(admin_class,field,None)
        if func:
            result=func()%model_obj.pk
            return mark_safe(result)

@register.simple_tag
def get_order_status(request,field,admin_class):
    func=getattr(admin_class,field,None)
    if func and hasattr(func,'__call__'):
        return 'disabled'
    else:
        order=request.GET.get('order')
        if order and order.replace('-','')==field:
            if order.startswith('-'):
                return 'desc'
            else:
                return 'asc'
        else:
            return "none"

@register.filter
def get_order_icon(request,field):
    order=request.GET.get('order')
    if order and order.replace('-','')==field:
        if order.startswith('-'):
            return 'glyphicon-triangle-bottom'
        else:
            return 'glyphicon-triangle-top'
    else:
        return ""

@register.filter
def get_search_value(request,field):
    search_value=request.GET.get(field)
    if search_value:
        return search_value
    else:
        return ""

@register.simple_tag
def get_tooltip_title_for_search(search_list):
    search_range='，'.join(search_list)
    return '搜索字段包括：%s'%search_range

@register.filter
def add_class(field_obj,css_classes):
    return field_obj.as_widget(attrs={'class':css_classes})

@register.filter
def add_attrs(field_obj,string):
    attrs={}
    for item in string.split(','):
        attr,value=item.split('=')
        attrs[attr]=value
    return field_obj.as_widget(attrs=attrs)

@register.filter
def get_candidate_options(field_obj):
    # 通过Form字段找到相关联的model对象
    model_class=field_obj.form._meta.model
    field_related_model_class = model_class._meta.get_field(field_obj.name).related_model
    pk_name = field_related_model_class._meta.pk.name
    # 通过是否含有主键值来判断实例是否存在
    if getattr(field_obj.form.instance,pk_name):
        # 获取Field字段实例中已包含的数据的主键，并exclude查找
        instance_queryset=getattr(field_obj.form.instance,field_obj.name)
        result=field_related_model_class.objects.exclude(pk__in=instance_queryset.values_list(pk_name,flat=True))
    else:
        result=field_obj.field.queryset
    return result


@register.filter
def get_selected_options(field_obj):
    model_class=field_obj.form._meta.model
    field_related_model_class = model_class._meta.get_field(field_obj.name).related_model
    pk_name = field_related_model_class._meta.pk.name
    # 通过是否含有主键值来判断实例是否存在
    if getattr(field_obj.form.instance,pk_name):
        # 获取Field字段实例中已包含的数据的主键，并exclude查找
        instance_queryset=getattr(field_obj.form.instance,field_obj.name)
        result =instance_queryset.all()
    else:
        result=[]
    return result

@register.simple_tag
def do_replace(string,pattern,new):
    return re.sub(pattern,new,string)

@register.filter
def show_nested_objects(objects_list):
    '''将objects列表通过递归，整理成ul元素返回'''
    #由于递归循环，因此外层已包含了<ul></ul>不需要单独添加
    ele_ul='<ul>%s</ul>'
    ul_list=[]
    for i in objects_list:
        if isinstance(i,list):
            ul_result=show_nested_objects(i)
            ul_list.append(ul_result)
        else:
            ele_li='<li>%s:%s</li>'%(i._meta.model._meta.verbose_name_plural,str(i))
            ul_list.append(ele_li)
    result=ele_ul%''.join(ul_list)
    return mark_safe(result)

@register.filter
def show(form):
    # print(form)
    print(form)
    print(dir(form))
    # print(dir(form.fields['is_active']))

@register.filter
def get_field(field,form):
    '''get field obj from a form by field name'''
    try:
        field_obj=form[field]
    except KeyError:
        field_obj=None
    return field_obj

@register.filter
def get_field_type_of_form(field):
    return type(field.field).__name__

@register.filter
def get_readonlyfield_data(field,form):
    data=getattr(form.instance,field)

    # True和False
    if data is True: data = mark_safe('<span class="glyphicon glyphicon-ok"></span>')
    if data is False: data = mark_safe('<span class="glyphicon glyphicon-remove"></span>')

    # 多对多类型
    func=getattr(data, 'all', None)
    if func:
        data=','.join([obj for obj in func()])

    # 密码类型转义，并加*隐藏
    if field=='password':
        try:
            data_list=data.split('$')
            ele='<strong>加密算法：</strong>%s<strong> 迭代次数：</strong>%s<strong> 盐：</strong>%s<strong> Hash：</strong>%s'
            data=ele%(
                data_list[0],
                data_list[1],
                string_hide(data_list[2]),
                string_hide(data_list[3]),
            )
        except Exception:
            data='*'*20

    # 时间类型转换
    if type(data).__name__=='datetime':
        data=data.strftime("%Y-%m-%d %H:%M:%S")

    return mark_safe(data)

def string_hide(string):
    hide_num=int(len(string)*0.6)
    start_num=int((len(string)-hide_num)/2)
    hide_part=string[0+start_num:hide_num+start_num]
    return string.replace(hide_part,'*'*hide_num)

@register.filter
def get_readonlyfield_label(field, form):
    model = form._meta.model
    field_obj=model._meta.get_field(field)
    if field_obj.verbose_name:
        return field_obj.verbose_name
    else:
        return field

@register.filter
def get_field_help_text(field, form):
    model=form._meta.model
    field_obj=model._meta.get_field(field)
    return field_obj.help_text

@register.filter
def get_field_attr(field_obj,attr_name):
    return getattr(field_obj,attr_name)

@register.filter
def get_meta(obj,name):
    return getattr(obj._meta,name)

