from home import models
from django.shortcuts import redirect,render,HttpResponse
from urllib.parse import urlencode
from django.contrib import messages
from django.urls import reverse,resolve
from django.utils.html import mark_safe
enabled_admins = {}

class BaseAdmin:
    list_display = []
    list_filters = []
    search_fields = []
    filter_horizontal = []
    list_per_page = 20
    ordering=[]
    readonly_table=False
    readonly_fields=[]
    actions = ["delete_selected_objs"]
    fieldsets = []

    def delete_selected_objs(self,request,querysets):
        url=request.path.replace('/action','/delete')
        query_dict={'id':request.GET.get('id')}
        querystring=urlencode(query_dict)
        return redirect(url+"?"+querystring)
    delete_selected_objs.short_description = '批量删除所有选中项'

class CustomerAdmin(BaseAdmin):
    list_display = ['qq','name','source','consultant','consult_course','ctime','status','id','enroll']
    list_filters = ['name','source','consultant','consult_course','status','ctime']
    search_fields = ['qq', 'name', "consultant__name"]
    filter_horizontal = ['tags']
    ordering = ['id']
    readonly_fields = ['qq','consultant','tags']
    readonly_table = False

    def enroll(self):
        url=reverse('enroll_for_salesman')+'?customer_id=%s'
        ele='<a href="%s">报名</a>'%url
        return ele
    enroll.verbose_name='报名链接'

class CourseRecordAdmin(BaseAdmin):
    list_display = ['from_class', 'day_num', 'teacher', 'has_homework', 'homework_title']
    actions = ["delete_selected_objs",'initialize_study_record']

    def initialize_study_record(self,request,querysets):
        url = request.META.get('HTTP_REFERER')
        if querysets.count()==1:
            obj=querysets[0]
            enrollments_querysets=obj.from_class.enrollment_set.all()
            obj_list=[]
            for enrollment_obj in enrollments_querysets:
                study_obj=models.StudyRecord(student=enrollment_obj,course_record=obj)
                obj_list.append(study_obj)

            try:
                models.StudyRecord.objects.bulk_create(obj_list)
                messages.success(request, '初始化学习记录成功！')
            except Exception:
                messages.error(request, '初始化学习记录失败！请确认学习记录是否已经存在。')
            finally:
                return redirect(url)
        else:
            messages.warning(request,'一次只能初始化一个班级的学习记录！')
            return redirect(url)
    initialize_study_record.short_description = '初始化学习记录'

class StudyRecordAdmin(BaseAdmin):
    list_display = ['student', 'course_record', 'attendance', 'score', 'ctime']

class CustomerFollowUpAdmin(BaseAdmin):
    list_display = ['id','customer','consultant','ctime']


class UserAdmin(BaseAdmin):
    list_display = ['email','name','groups','is_staff','is_active','ctime']
    list_filters = ['groups','is_staff','is_active','ctime']
    search_fields = ['email','name']
    filter_horizontal = ['roles']
    ordering = ['id']
    readonly_fields = ['email','password','last_login','ctime']

    fieldsets = (
        (None, {'fields': ('name', 'email', 'password')}),
        ('个人信息', {'fields': ('roles', 'is_staff','is_active', 'ctime','last_login')}),
        ('权限', {'fields': ('is_superuser', 'groups', 'user_permissions')}),
    )





def register(model_class,admin_class=None):
    # 默认未配置admin时，使用Baseadmin
    if admin_class is None:
        admin_class=BaseAdmin

    if model_class._meta.app_label not in enabled_admins:
        enabled_admins[model_class._meta.app_label]={}

    enabled_admins[model_class._meta.app_label][model_class._meta.model_name]={'model':model_class}

    if admin_class is not None:
        # 判断list_display是否包含主键，并将主键设为第一列
        if model_class._meta.pk.name in admin_class.list_display:
            admin_class.list_display.remove(model_class._meta.pk.name)
            admin_class.list_display.insert(0,model_class._meta.pk.name)
        else:
            admin_class.list_display.insert(0, model_class._meta.pk.name)

        enabled_admins[model_class._meta.app_label][model_class._meta.model_name].update({'admin':admin_class})

        # 如果未设置搜索字段，则将主键设为搜索字段
        if not admin_class.search_fields:
            admin_class.search_fields.insert(0, model_class._meta.pk.name)

        # 判断是否设置了ordering
        if not admin_class.ordering:
            admin_class.ordering=[model_class._meta.pk.name]

        # 整表只读时，保险起见将所有字段设为只读
        if admin_class.readonly_table:
            all_fields=model_class._meta.local_fields+model_class._meta.local_many_to_many
            admin_class.readonly_fields=[field.name for field in all_fields]

        # 未设置fieldset时，默认显示所有字段
        if not admin_class.fieldsets:
            all_fields = model_class._meta.local_fields + model_class._meta.local_many_to_many
            admin_class.fieldsets=(
                (None,{'fields':[field.name for field in all_fields]}),
            )


        # 将model赋值给admin
        admin_class.model=model_class


register(models.User,UserAdmin)
register(models.Customer,CustomerAdmin)
register(models.CustomerFollowUp,CustomerFollowUpAdmin)
register(models.CourseRecord,CourseRecordAdmin)
register(models.StudyRecord,StudyRecordAdmin)
