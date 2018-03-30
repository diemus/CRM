from django.shortcuts import render,redirect,HttpResponse
from account import app_forms
from django.contrib.auth import authenticate,logout,login
from django.contrib.auth import views as django_auth_views
from django.contrib import messages
from account import models
from django.utils.decorators import method_decorator
from guardian.decorators import permission_required,permission_required_or_403
import gettext
# Create your views here.

def test(request):
    user=models.User.objects.get_by_natural_key('zf@163.com')
    # print(user.check_password('123'))
    # user.set_password('123')
    # user.save()
    # print(user.check_password('123'))
    return HttpResponse('ok')

class LoginView(django_auth_views.LoginView):
    authentication_form = app_forms.AuthenticationForm
    template_name = 'account/login.html'
    extra_context={}

    def form_valid(self, form):
        login(self.request, form.get_user())
        if self.request.POST.get('remeber-me'): self.request.session.set_expiry(60 * 60 * 24 * 30)
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        if form.errors.as_data().get('__all__'):
            for error in form.errors.as_data().get('__all__'):
                messages.error(self.request, error.message)
        return self.render_to_response(self.get_context_data(form=form))

def logout_view(request):
    if request.method=='GET':
        logout(request)
        messages.success(request,'你已成功注销！')
        return redirect('/login')

class PasswordChangeView(django_auth_views.PasswordChangeView):
    form_class = app_forms.PasswordChangeForm
    success_url = '/'
    template_name = 'account/password_change.html'
    title = 'Password change'

    def form_valid(self, form):
        messages.success(self.request, '密码修改成功！')
        return super(PasswordChangeView, self).form_valid(form)

@method_decorator(permission_required('account.global_password_change',return_403=True),name='dispatch')
class GlobalPasswordChangeView(PasswordChangeView):

    def get_form_kwargs(self):
        kwargs = super(PasswordChangeView, self).get_form_kwargs()
        try:
            #存在指定id时，更改指定id用户密码，否则更改当前用户密码
            if self.request.method == "GET":
                uid = self.request.GET.get('id')
            elif self.request.method == "POST":
                uid = self.request.POST.get('id')
            else:
                uid = self.request.PUT.get('id')
            kwargs['user']=models.User.objects.get(pk=uid)
        except Exception:
            kwargs['user'] = self.request.user
        return kwargs
