from django.contrib.auth import backends
from django.contrib.auth import get_user_model
UserModel = get_user_model()

class CustomAuthBackend(backends.ModelBackend):
    """
    由于django自带的认证后端包含了user_can_authenticate（is_active）认证，与
    AuthenticationForm中的功能重复，导致认证失败时无法提示是由于用户名或密码错误
    还是由于账户冻结导致的，因此写了类以覆盖自带认证后端，将账户冻结放在form验证，
    仅删除了原先的user_can_authenticate，未做大的修改。
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        try:
            user = UserModel._default_manager.get_by_natural_key(username)
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a non-existing user (#20760).
            UserModel().set_password(password)
        else:
            if user.check_password(password):
                return user