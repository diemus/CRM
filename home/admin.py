from django.contrib import admin
from home import models

from guardian.admin import GuardedModelAdmin
# Register your models here.
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id','qq','source','consultant','content','status','ctime')
    list_filter = ('source','consultant','ctime')
    search_fields = ('qq','name')
    raw_id_fields = ('consult_course',)
    filter_horizontal = ('tags',)
    # list_editable = ('status',)
    # readonly_fields = ['qq','consultant']
    actions = ['gogogo']
    # date_hierarchy='ctime'

    def gogogo(self,arg1,arg2):
        print(self,arg1,arg2)
        from django.shortcuts import HttpResponse
        return HttpResponse('ok')


admin.site.register(models.Customer,CustomerAdmin)
admin.site.register(models.CustomerFollowUp)
admin.site.register(models.Enrollment)
admin.site.register(models.Course)
admin.site.register(models.ClassList)
admin.site.register(models.CourseRecord)
admin.site.register(models.Branch)
admin.site.register(models.Role)
admin.site.register(models.Payment)
admin.site.register(models.StudyRecord)
admin.site.register(models.Tag)
admin.site.register(models.Menu)
admin.site.register(models.ContractTemplate)
