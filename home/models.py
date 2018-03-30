from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin

from django.contrib.auth import get_user_model
User=get_user_model()

# Create your models here.
class Customer(models.Model):
    '''客户信息表'''
    name=models.CharField('姓名',max_length=32,blank=True,null=True)
    qq=models.CharField('QQ',max_length=64,unique=True)
    qq_name=models.CharField('QQ名',max_length=64,blank=True,null=True)
    mobile=models.CharField('手机号',max_length=32)
    id_num=models.CharField('身份证号',max_length=64,blank=True,null=True)
    email=models.EmailField('邮箱',max_length=64,blank=True,null=True)
    source_choices = ((0,'转介绍'),
                      (1,'QQ群'),
                      (2,'官网'),
                      (3,'百度推广'),
                      (4,'51CTO'),
                      (5,'知乎'),
                      (6,'市场推广')
                      )
    source=models.PositiveSmallIntegerField('来源',choices=source_choices)
    referral_from = models.CharField(verbose_name="转介绍人qq", max_length=64, blank=True, null=True)
    consult_course = models.ForeignKey("Course",verbose_name="咨询课程")
    content = models.TextField(verbose_name="咨询详情")
    tags = models.ManyToManyField("Tag",blank=True)
    status_choices = ((0,'未报名'),
                      (1,'已报名'),
                      )
    status = models.SmallIntegerField(choices=status_choices,default=1)
    consultant = models.ForeignKey(User,verbose_name='咨询顾问')
    memo = models.TextField(blank=True,null=True)
    ctime = models.DateTimeField(auto_now_add=True,verbose_name='创建日期')

    def __str__(self):
        return self.name if self.name else self.qq

    class Meta:
        verbose_name ="客户表"
        verbose_name_plural ="客户表"
        ordering=['id']

class Tag(models.Model):
    name = models.CharField(unique=True,max_length=32)
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "标签"
        verbose_name_plural = "标签"


class CustomerFollowUp(models.Model):
    '''客户跟进记录'''
    customer=models.ForeignKey('Customer')
    content=models.TextField(verbose_name='跟进内容')
    consultant=models.ForeignKey(User)
    intention_choices  = ((0,'2周内报名'),
                          (1,'1个月内报名'),
                          (2,'近期无报名计划'),
                          (3,'已在其它机构报名'),
                          (4,'已报名'),
                          (5,'已拉黑'),
                          )
    intention = models.SmallIntegerField(choices=intention_choices)
    ctime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "<%s : %s>" %(self.customer.qq,self.intention)

    class Meta:
        verbose_name = "客户跟进记录"
        verbose_name_plural = "客户跟进记录"

class Course(models.Model):
    '''课程表'''
    name = models.CharField(max_length=64,unique=True)
    price = models.PositiveSmallIntegerField()
    period = models.PositiveSmallIntegerField(verbose_name="周期(月)")
    outline = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "课程表"
        verbose_name_plural = "课程表"

class Enrollment(models.Model):
    '''报名表'''
    customer = models.ForeignKey("Customer")
    enrolled_class = models.ForeignKey("ClassList",verbose_name="所报班级",null=True)
    consultant = models.ForeignKey(User,verbose_name="课程顾问",null=True)
    contract_agreed = models.BooleanField(default=False,verbose_name="学员已同意合同条款")
    contract_approved = models.BooleanField(default=False,verbose_name="合同已审核")
    status = models.BooleanField(default=False,verbose_name="报名状态")
    ctime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s %s" %(self.customer,self.enrolled_class)

    class Meta:
        unique_together = ("customer","enrolled_class")
        verbose_name_plural = "报名表"

class Payment(models.Model):
    '''缴费记录'''
    enrollment = models.ForeignKey("Enrollment")
    amount = models.PositiveIntegerField(verbose_name="数额")
    ctime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s %s %s" %(self.enrollment.customer.name,self.enrollment.enrolled_class.course.name,self.amount)

    class Meta:
        verbose_name_plural = "缴费记录"

class Branch(models.Model):
    '''校区'''
    name = models.CharField(max_length=128,unique=True)
    addr = models.CharField(max_length=128)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "校区"
        verbose_name_plural = "校区"

class ContractTemplate(models.Model):
    name=models.CharField('合同名称',max_length=64,unique=True)
    template=models.TextField('合同模板')

    def __str__(self):
        return self.name

class ClassList(models.Model):
    '''班级表'''
    branch = models.ForeignKey("Branch",verbose_name="校区")
    course = models.ForeignKey("Course")
    class_type_choices = ((0,'面授(脱产)'),
                          (1,'面授(周末)'),
                          (2,'网络班')
                          )
    class_type = models.SmallIntegerField(choices=class_type_choices,verbose_name="班级类型")
    semester = models.PositiveSmallIntegerField(verbose_name="学期")
    teachers = models.ManyToManyField(User,blank=True)
    contract=models.ForeignKey(to='ContractTemplate',blank=True,null=True)
    start_date = models.DateField(verbose_name="开班日期")
    end_date = models.DateField(verbose_name="结业日期",blank=True,null=True)

    def __str__(self):
        return "%s %s %s" %(self.branch,self.course,self.semester)

    class Meta:
        unique_together = ('branch','course','semester')
        verbose_name_plural = "班级"
        verbose_name = "班级"

class CourseRecord(models.Model):
    '''上课记录表'''
    from_class = models.ForeignKey("ClassList",verbose_name="班级")
    day_num = models.PositiveSmallIntegerField(verbose_name="第几节(天)")
    teacher = models.ForeignKey(User)
    has_homework = models.BooleanField(default=True)
    homework_title = models.CharField(max_length=128,blank=True,null=True)
    homework_content = models.TextField(blank=True,null=True)
    outline = models.TextField(verbose_name="本节课程大纲")
    ctime = models.DateField(auto_now_add=True)

    def __str__(self):
        return "%s %s" %(self.from_class,self.day_num)

    class Meta:
        unique_together = ("from_class", "day_num")
        verbose_name_plural = "上课记录"

class StudyRecord(models.Model):
    '''学习记录表'''
    student = models.ForeignKey("Enrollment")
    course_record = models.ForeignKey("CourseRecord")
    attendance_choices = ((0,'已签到'),
                          (1,'迟到'),
                          (2,'缺勤'),
                          (3,'早退'),
                          )
    attendance = models.SmallIntegerField(choices=attendance_choices,default=0)
    score_choices = ((100,"A+"),
                     (90,"A"),
                     (85,"B+"),
                     (80,"B"),
                     (75,"B-"),
                     (70,"C+"),
                     (60,"C"),
                     (40,"C-"),
                     (-50,"D"),
                     (-100,"COPY"),
                     (0,"N/A"),
                     )
    score = models.SmallIntegerField(choices=score_choices,default=0)
    memo = models.TextField(blank=True,null=True)
    ctime = models.DateField(auto_now_add=True)

    def __str__(self):
        return "%s %s %s" %(self.student,self.course_record,self.score)

    class Meta:
        unique_together = ('student','course_record')
        verbose_name_plural = "学习记录"

class Role(models.Model):
    '''角色表'''
    name = models.CharField(max_length=32,unique=True)
    menus = models.ManyToManyField("Menu",blank=True)

    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = "角色"

class Menu(models.Model):
    '''菜单'''
    name = models.CharField(max_length=32)
    url_name = models.CharField(max_length=64)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name='菜单配置'
        verbose_name_plural ='菜单配置'
