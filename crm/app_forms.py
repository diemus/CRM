from django import forms
from home import models
from django.forms import ValidationError
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from home import models as crm_models

User=get_user_model()

class AddEnrollment(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(AddEnrollment, self).__init__(*args, **kwargs)
        # model为了方便创建设置为了null=True,填写是需限定为required
        self.fields['enrolled_class'].required = True
        self.fields['consultant'].required = True

    class Meta:
        model=crm_models.Enrollment
        fields=['customer','enrolled_class','consultant']


class StudentRegistration(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(StudentRegistration, self).__init__(*args, **kwargs)
        # Django1.9版本后，可以设定disabled属性，Django会自动使用initial原值
        # 而widget里的attr中disabled=True无此效果
        self.fields['qq'].disabled = True
        self.fields['consultant'].disabled = True
        self.fields['source'].disabled = True

    class Meta:
        model=crm_models.Customer
        exclude=['content','tags','status','memo','ctime','referral_from','consult_course']

class StudentRegistrationReview(forms.ModelForm):

    class Meta:
        model=crm_models.Customer
        exclude=['content','tags','status','memo','ctime','referral_from','consult_course']

class Payment(forms.ModelForm):

    class Meta:
        model=crm_models.Payment
        fields=['amount']

