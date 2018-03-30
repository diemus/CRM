from django.db.models.signals import pre_delete,post_delete
from django.dispatch import receiver
from home import king_admin



@receiver(pre_delete)
def protect_posts(sender,instance,**kwargs):

    # 删除前验证是否为只读数据
    app_label=instance._meta.app_label
    model_name=instance._meta.model_name
    app_dict=king_admin.enabled_admins.get(app_label)
    if app_dict:
        if app_dict.get(model_name):
            admin_class=app_dict.get(model_name).get('admin')
            if admin_class.readonly_table:
                raise Exception('%s已被设为只读，不可删除数据！'%model_name)



