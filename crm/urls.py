from django.conf.urls import url,include

from crm import views

urlpatterns = [
    url(r'^index$',views.index,name='crm_index'),
    url(r'^salesman/enroll$',views.enroll,name='enroll_for_salesman'),
    url(r'^salesman/enrollment_check$',views.enrollment_check,name='enrollment_check'),
    url(r'^salesman/stu_registration/(?P<nid>[a-zA-Z0-9]+)/(?P<random_str>[a-zA-Z0-9]+)$',views.stu_registration,name='enroll_for_student'),
    url(r'^salesman/stu_registration_upload/(?P<nid>[a-zA-Z0-9]+)/(?P<type>[a-zA-Z0-9]+)$',views.stu_id_image_upload,name='stu_registration_upload'),
    url(r'^salesman/stu_registration_review/(?P<nid>[a-zA-Z0-9]+)$',views.stu_registration_review,name='stu_registration_review'),
    url(r'^salesman/stu_registration_payment/(?P<nid>[a-zA-Z0-9]+)$',views.stu_registration_payment,name='stu_registration_payment'),
    url(r'^salesman/show_stu_id_image/(?P<nid>[a-zA-Z0-9]+)/(?P<type>[a-zA-Z0-9]+)$',views.show_stu_id_image,name='show_stu_id_image'),
    url(r'^student/course_management$',views.course_management,name='course_management'),
    url(r'^student/homework_management/(?P<nid>[a-zA-Z0-9]+)$',views.homework_management,name='homework_management'),
    url(r'^student/homework_detail/(?P<nid>[a-zA-Z0-9]+)$',views.homework_detail,name='homework_detail'),
    url(r'^student/homework_upload/(?P<nid>[a-zA-Z0-9]+)$',views.homework_upload,name='homework_upload'),

]
