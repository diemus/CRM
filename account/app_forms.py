from django import forms
from home import models
from django.contrib.auth import authenticate,password_validation
from django.contrib.auth import forms as django_auth_forms

class AuthenticationForm(django_auth_forms.AuthenticationForm):
    """
    邮箱及密码验证，通过后验证账户是否冻结。
    """
    email=forms.EmailField(max_length=255,error_messages={'invalid':'邮箱格式错误！'},label='邮箱：')
    password=forms.CharField(label='密码：',widget=forms.PasswordInput())

    field_order=['email','password']
    error_messages = {
        'invalid_login': '用户名或密码错误！',
        'inactive': '账户已冻结！',
    }

    # 注意第一个默认参数为request，因此实例化是必须注明data=request.POST，
    # 否则会被当做data为空处理，不会做任何字段验证。
    def __init__(self, request=None, *args, **kwargs):
        super(AuthenticationForm, self).__init__(request=request,*args, **kwargs)
        # 去掉父类中的username字段
        self.fields.pop('username')

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email is not None and password:
            self.user_cache = authenticate(email=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )

class SetPasswordForm(django_auth_forms.SetPasswordForm):
    """
    密码重置（不需要输入旧密码）
    """
    error_messages = {
        'password_mismatch': '两次密码输入不一致！',
    }
    new_password1 = forms.CharField(
        label='新密码：',
        widget=forms.PasswordInput,
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label='请再次输入：',
        strip=False,
        widget=forms.PasswordInput,
    )

class PasswordChangeForm(SetPasswordForm,django_auth_forms.PasswordChangeForm):
    """
    密码变更（需要输入旧密码验证）
    使用了多继承，由于python继承顺序，字段会使用左侧自定制的Form的中文字段，而
    clean_old_password则会使用右侧的django原form中的方法
    """
    error_messages = dict(SetPasswordForm.error_messages, **{
        'password_incorrect': "密码错误，请重试！",
    })
    old_password = forms.CharField(
        label="旧密码",
        strip=False,
        widget=forms.PasswordInput(attrs={'autofocus': True}),
    )

    field_order = ['old_password', 'new_password1', 'new_password2']