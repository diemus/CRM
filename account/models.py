from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.utils import timezone
from django.utils.safestring import mark_safe

from guardian.mixins import GuardianUserMixin
# Create your models here.
class UserManager(BaseUserManager):
    def _create_user(self, email, name, password, **extra_fields):
        if not email:
            raise ValueError('邮箱不能为空！')
        if not name:
            raise ValueError('姓名不能为空！')
        email = self.normalize_email(email)
        user = self.model(name=name, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, name, password, **extra_fields)

    def create_superuser(self, email, name, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, name, password, **extra_fields)

class User(AbstractBaseUser,PermissionsMixin,GuardianUserMixin):

    email = models.EmailField('邮箱',max_length=255,unique=True)
    name = models.CharField('姓名',max_length=32)
    roles = models.ManyToManyField('home.Role', blank=True)
    is_staff = models.BooleanField('是否为员工',default=False)
    is_active = models.BooleanField('账户状态',default=True)
    ctime = models.DateTimeField('注册时间',default=timezone.now)
    student = models.ForeignKey("home.Customer", verbose_name="关联学员账号", blank=True, null=True,
                                    help_text="只有学员报名后方可为其创建账号")

    password = models.CharField('密码', max_length=128)
    last_login = models.DateTimeField('最后登录时间', blank=True, null=True)


    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta:
        verbose_name='用户信息'
        verbose_name_plural='用户信息'
        permissions=[
            ('global_password_change','有权修改任意账户密码'),
        ]

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        self._meta.get_field('is_superuser').verbose_name = "是否为管理员"
        self._meta.get_field('is_superuser').help_text = "管理员账户拥有所有权限"
        self._meta.get_field('groups').verbose_name = "用户组"
        self._meta.get_field('groups').help_text = "该用户将拥有用户所在组的所有权限"
        self._meta.get_field('user_permissions').verbose_name = "用户权限"
        self._meta.get_field('user_permissions').help_text = "该用户所拥有的权限"

    def clean(self):
        super(User, self).clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        # The user is identified by their email address
        return self.name

    def get_short_name(self):
        # The user is identified by their email address
        return self.name

    def __str__(self):
        return self.email

