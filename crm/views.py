from django.shortcuts import render,HttpResponse,redirect
from crm import app_forms
import json
import string
import random
from django.core.cache import cache
from home import models as crm_models
from PerfectCRM import settings
import os
from django.urls import reverse
from django.contrib import messages
# Create your views here.
def index(request):
    return render(request, 'crm/index.html')

def enroll(request):

    if request.method=='GET':
        customer_id=request.GET.get('customer_id')
        obj = crm_models.Enrollment.objects.filter(customer_id=customer_id,status=False).last()
        # 通过该用户最后一次注册，判断是否存在未完成的注册实例
        if not obj:
            crm_models.Enrollment.objects.create(customer_id=customer_id)

        form1 = app_forms.AddEnrollment(instance=obj)
        form3=app_forms.StudentRegistration(instance=crm_models.Customer.objects.get(pk=customer_id))
        form4=app_forms.Payment()
        return render(request,'crm/salesman/enroll.html',{'form1':form1,'form3':form3,'form4':form4,'enrollment_obj':obj})

    if request.method=='POST':
        customer_id=request.POST.get('customer')
        obj=crm_models.Enrollment.objects.filter(customer_id=customer_id,status=False).last()
        form1 = app_forms.AddEnrollment(data=request.POST,instance=obj)
        rep_data={'status':True,'errors':None}
        if form1.is_valid():
            enroll_obj=form1.save()
            if cache.get(enroll_obj.pk):
                random_str=cache.get(enroll_obj.pk)
            else:
                random_str=''.join(random.sample(string.ascii_lowercase+string.digits,10))
                cache.set(enroll_obj.pk,random_str,60*60*24*15)
            link='''http://127.0.0.1:8000/crm/salesman/stu_registration/%s/%s'''%(enroll_obj.pk,random_str)
            rep_data['link']=link
            rep_data['enrollment_id']=enroll_obj.pk
        else:
            rep_data['status']=False
            rep_data['errors']=json.loads(form1.errors.as_json())
        return HttpResponse(json.dumps(rep_data))

def enrollment_check(request):
    if request.method=='POST':
        rep_data = {'status': True}
        enrollment_id=request.POST.get('id')
        obj = crm_models.Enrollment.objects.filter(id=enrollment_id).first()
        if obj and obj.contract_agreed:
            pass
        else:
            rep_data['status'] = False
        return HttpResponse(json.dumps(rep_data))

def stu_registration(request,nid,random_str):
    enrollment_obj = crm_models.Enrollment.objects.get(pk=nid)
    if cache.get(enrollment_obj.pk)==random_str:
        if request.method=='GET':
            customer_form=app_forms.StudentRegistration(instance=enrollment_obj.customer)
            return render(request,'crm/salesman/stu_registration.html',{'customer_form':customer_form,'enrollment_obj':enrollment_obj})

        elif request.method=="POST":
            customer_form = app_forms.StudentRegistration(data=request.POST,instance=enrollment_obj.customer)
            if customer_form.is_valid():
                customer_form.save()
                enrollment_obj.contract_agreed=True
                enrollment_obj.save()
            return render(request, 'crm/salesman/stu_registration.html',
                          {'customer_form': customer_form, 'enrollment_obj': enrollment_obj})
    else:
        return HttpResponse('该链接已失效，请重新生成！')

def stu_registration_review(request,nid):
    rep_data = {'status': True}
    if request.method=="POST":
        obj=crm_models.Enrollment.objects.filter(pk=nid).first()
        review=request.POST.get('review')
        if obj and review=='false':
            obj.contract_agreed=False
            obj.contract_approved = False
            obj.save()
        elif obj and review=='true':
            obj.contract_agreed = True
            obj.contract_approved=True
            obj.save()
        return HttpResponse(json.dumps(rep_data))


def stu_registration_payment(request,nid):
    rep_data = {'status': True,'msg':None}
    if request.method=="POST":
        obj=crm_models.Enrollment.objects.filter(pk=nid).first()
        form=app_forms.Payment(data=request.POST)
        if obj and form.is_valid() and form.cleaned_data.get('amount')>=500:
            crm_models.Payment.objects.create(enrollment_id=obj.pk,amount=form.cleaned_data.get('amount'))
            obj.status=True
            obj.save()
            obj.customer.status=0
            obj.customer.save()
        else:
            rep_data['status']=False
            rep_data['msg']='金额不足'
        return HttpResponse(json.dumps(rep_data))

def stu_id_image_upload(request,nid,type):
    if request.method=='POST':
        path=os.path.join(settings.ENROLL_IMAGE_DIR,nid,type)
        if not os.path.exists(path):
            os.makedirs(path,exist_ok=True)

        for k,file in request.FILES.items():
            f=open(os.path.join(path,file.name),'wb')
            for chunk in file.chunks():
                f.write(chunk)

        return HttpResponse('ok')

def show_stu_id_image(request,nid,type):
    if request.user.is_staff:
        if request.method=='GET':
            folder_path=os.path.join(settings.ENROLL_IMAGE_DIR,nid,type)
            try:
                filename=os.listdir(folder_path)[0]
                full_path=os.path.join(folder_path,filename)
                f=open(full_path,'rb')
                return HttpResponse(f.read())
            except Exception:
                return HttpResponse('Not Found',status=404)
    else:
        return HttpResponse('内部图片，禁止浏览！')


def course_management(request):
    if request.method=="GET":
        stu_obj=request.user.student
        if stu_obj:
            enrollment_querysets=stu_obj.enrollment_set.all()
            return render(request, 'crm/student/course_management.html',{'customer_obj':stu_obj})
        else:
            messages.error(request,'非学生账户')
            return redirect(reverse('crm_index'))

def homework_management(request,nid):
    if request.method=="GET":
        enroll_obj=crm_models.Enrollment.objects.get(pk=nid)
        return render(request,'crm/student/homework_management.html',{'enroll_obj':enroll_obj})

def homework_detail(request,nid):
    if request.method=="GET":
        study_record_obj=crm_models.StudyRecord.objects.get(pk=nid)
        return render(request,'crm/student/homework_detail.html',{'study_record_obj':study_record_obj})

def homework_upload(request,nid):
    rep_data={'status': True,'msg':None,'data':[]}

    if request.method=='GET':
        folder_path = os.path.join(settings.STU_HOMEWORK_DIR, nid)
        if os.path.exists(folder_path):
            for i in os.listdir(folder_path):
                filename = i
                filesize=os.path.getsize(os.path.join(folder_path,filename))
                thumbnail_url='/static/image/1.jpg'
                rep_data['data'].append({
                    'name': filename,
                    'size': filesize,
                    'thumbnail_url': thumbnail_url,
                })
        else:
            rep_data['status']=False

        return HttpResponse(json.dumps(rep_data))

    if request.method=="POST":
        study_record_obj=crm_models.StudyRecord.objects.get(pk=nid)
        path=os.path.join(settings.STU_HOMEWORK_DIR,nid)
        if not os.path.exists(path):
            os.makedirs(path,exist_ok=True)

        for k,file in request.FILES.items():
            full_path=os.path.join(path, file.name)
            f=open(full_path,'wb')
            for chunk in file.chunks():
                f.write(chunk)
            rep_data['data'].append({
                'name':file.name,
                'size':file.size,
                'thumbnail_url':full_path,
            })
        return HttpResponse(json.dumps(rep_data))