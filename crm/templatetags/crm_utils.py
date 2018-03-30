from django import template
from django.utils.safestring import mark_safe
from django.core.exceptions import FieldDoesNotExist
import re
import json
from django.db.models import Sum
register=template.Library()

@register.filter
def render_contract_template(enrollment_obj):
    render_map={
        'stu_name':enrollment_obj.customer.name,
        'course_name':enrollment_obj.enrolled_class
    }
    return enrollment_obj.enrolled_class.contract.template.format(**render_map)

@register.filter
def get_error_for_all(form):
    errors=json.loads(form.errors.as_json())
    if errors.get('__all__'):
        return errors.get('__all__')[0]['message']
    else:
        return ''

@register.filter
def get_enrolled_classes(enroll_obj):
    return enroll_obj.enrollment_set.filter(status=True)

@register.filter
def get_student_sum_score(enroll_obj,customer_obj):
    score=enroll_obj.studyrecord_set.filter(course_record__from_class=enroll_obj.enrolled_class).aggregate(Sum('score'))['score__sum']
    if score:
        return score
    else:
        return 0

@register.filter
def get_attendance_status(courserecord_obj,enroll_obj):
    studyrecord_obj=courserecord_obj.studyrecord_set.get(student=enroll_obj)
    return studyrecord_obj.get_attendance_display()

@register.filter
def get_score(courserecord_obj,enroll_obj):
    studyrecord_obj=courserecord_obj.studyrecord_set.get(student=enroll_obj)
    return studyrecord_obj.get_score_display()

