from django import forms
from home import models
from django.forms import ValidationError
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import ReadOnlyPasswordHashField

User=get_user_model()

def create_model_form(model_class,admin_class=None):
    attrs = {}

    class Meta:
        model=model_class
        fields="__all__"
        exclude=['last_login']
        if admin_class.readonly_fields:
            exclude.extend(admin_class.readonly_fields)
    attrs['Meta']=Meta

    # readonly Field 过滤
    if admin_class:
        def clean(self):
            # 检查整表只读时，数据是否有修改
            if admin_class.readonly_table:
                if self.changed_data:
                    raise ValidationError('此表已设为只读，不可修改！')

            # 只读字段检测
            for field in admin_class.readonly_fields:
                # 存在实例时为编辑状态
                if self.instance and self.instance.pk:
                    # 检查被修改的数据中是否包含只读字段
                    if field in self.changed_data:
                        self.add_error(field,'只读字段不可修改！')



        attrs['clean']=clean

    _model_form_class=type('DynamicModelForm',(forms.ModelForm,),attrs)
    return _model_form_class
